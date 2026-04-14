import pytest

from app.core.client_ip import (
    UNKNOWN_REMOTE_IP,
    _resolve_client_ip,
    validate_trusted_proxy_startup_configuration,
)


def test_returns_peer_ip_when_trusted_proxy_list_is_empty() -> None:
    resolved = _resolve_client_ip(
        peer_ip="203.0.113.10",
        x_forwarded_for="198.51.100.25",
        trusted_proxy_cidrs=[],
    )

    assert resolved == "203.0.113.10"


def test_uses_forwarded_chain_when_peer_is_trusted_proxy() -> None:
    resolved = _resolve_client_ip(
        peer_ip="10.0.0.2",
        x_forwarded_for="198.51.100.25, 10.0.0.1",
        trusted_proxy_cidrs=["10.0.0.0/8"],
    )

    assert resolved == "198.51.100.25"


def test_uses_nearest_untrusted_hop_when_xff_contains_extra_leftmost_values() -> None:
    resolved = _resolve_client_ip(
        peer_ip="10.0.0.2",
        x_forwarded_for="203.0.113.7, 198.51.100.25, 10.0.0.1",
        trusted_proxy_cidrs=["10.0.0.0/8"],
    )

    assert resolved == "198.51.100.25"


def test_returns_unknown_when_peer_ip_is_missing() -> None:
    resolved = _resolve_client_ip(
        peer_ip=None,
        x_forwarded_for="198.51.100.25",
        trusted_proxy_cidrs=["10.0.0.0/8"],
    )

    assert resolved == UNKNOWN_REMOTE_IP


def test_invalid_trusted_proxy_entries_are_ignored() -> None:
    resolved = _resolve_client_ip(
        peer_ip="198.51.100.8",
        x_forwarded_for="203.0.113.4",
        trusted_proxy_cidrs=["not-a-cidr"],
    )

    assert resolved == "198.51.100.8"


def test_startup_validation_requires_trusted_proxies_for_proxied_envs() -> None:
    with pytest.raises(RuntimeError, match="TRUSTED_PROXY_CIDRS must be configured"):
        validate_trusted_proxy_startup_configuration(
            app_env="production",
            trusted_proxy_cidrs=[],
        )


def test_startup_validation_rejects_invalid_trusted_proxy_cidrs() -> None:
    with pytest.raises(RuntimeError, match="contains invalid entries"):
        validate_trusted_proxy_startup_configuration(
            app_env="production",
            trusted_proxy_cidrs=["not-a-cidr"],
        )


def test_startup_validation_allows_non_proxied_env_without_trusted_proxy_cidrs() -> None:
    validate_trusted_proxy_startup_configuration(
        app_env="development",
        trusted_proxy_cidrs=[],
    )
