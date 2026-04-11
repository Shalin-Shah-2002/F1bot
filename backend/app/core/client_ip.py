from functools import lru_cache
from ipaddress import ip_address, ip_network
from ipaddress import IPv4Address, IPv4Network, IPv6Address, IPv6Network

from fastapi import Request

from app.core.config import get_settings

UNKNOWN_REMOTE_IP = "unknown"

IPAddress = IPv4Address | IPv6Address
IPNetwork = IPv4Network | IPv6Network


def _normalize_ip_token(value: str | None) -> str | None:
    if value is None:
        return None

    candidate = value.strip().strip('"').strip("'")
    if not candidate:
        return None

    # Support tokens that may include RFC7239-style key prefix.
    if candidate.lower().startswith("for="):
        candidate = candidate.split("=", 1)[1].strip().strip('"').strip("'")

    # Support IPv6 bracket notation and optional port wrappers.
    if candidate.startswith("["):
        bracket_end = candidate.find("]")
        if bracket_end > 1:
            candidate = candidate[1:bracket_end]
    elif candidate.count(":") == 1 and "." in candidate:
        host_part, port_part = candidate.rsplit(":", 1)
        if port_part.isdigit():
            candidate = host_part

    try:
        return str(ip_address(candidate))
    except ValueError:
        return None


@lru_cache(maxsize=32)
def _parse_trusted_networks(raw_cidrs: tuple[str, ...]) -> tuple[IPNetwork, ...]:
    parsed_networks: list[IPNetwork] = []

    for raw_cidr in raw_cidrs:
        cidr = raw_cidr.strip()
        if not cidr:
            continue

        try:
            if "/" in cidr:
                parsed_networks.append(ip_network(cidr, strict=False))
                continue

            addr = ip_address(cidr)
            prefix = 32 if addr.version == 4 else 128
            parsed_networks.append(ip_network(f"{addr}/{prefix}", strict=False))
        except ValueError:
            continue

    return tuple(parsed_networks)


def _is_trusted_proxy(ip_text: str, trusted_networks: tuple[IPNetwork, ...]) -> bool:
    try:
        parsed_ip: IPAddress = ip_address(ip_text)
    except ValueError:
        return False

    return any(parsed_ip in network for network in trusted_networks)


def _parse_x_forwarded_for(x_forwarded_for: str | None) -> list[str]:
    if not x_forwarded_for:
        return []

    hops: list[str] = []
    for token in x_forwarded_for.split(","):
        normalized = _normalize_ip_token(token)
        if normalized:
            hops.append(normalized)

    return hops


def _resolve_client_ip(
    peer_ip: str | None,
    x_forwarded_for: str | None,
    trusted_proxy_cidrs: list[str] | tuple[str, ...],
) -> str:
    normalized_peer_ip = _normalize_ip_token(peer_ip)
    if not normalized_peer_ip:
        return UNKNOWN_REMOTE_IP

    trusted_networks = _parse_trusted_networks(tuple(str(value) for value in trusted_proxy_cidrs))
    if not trusted_networks:
        return normalized_peer_ip

    hops = _parse_x_forwarded_for(x_forwarded_for)
    hops.append(normalized_peer_ip)

    # Remove trusted proxy hops from the right, then use the nearest untrusted hop.
    while hops and _is_trusted_proxy(hops[-1], trusted_networks):
        hops.pop()

    if not hops:
        return normalized_peer_ip

    return hops[-1]


def resolve_client_ip(request: Request) -> str:
    settings = get_settings()
    peer_ip = request.client.host if request.client else None
    x_forwarded_for = request.headers.get("x-forwarded-for")
    return _resolve_client_ip(
        peer_ip=peer_ip,
        x_forwarded_for=x_forwarded_for,
        trusted_proxy_cidrs=settings.trusted_proxy_cidrs,
    )
