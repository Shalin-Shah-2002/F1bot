export interface SessionState {
  userId: string;
  email: string;
}

interface SessionPayload {
  user_id?: unknown;
  email?: unknown;
}

const API_BASE_URL = (
  process.env.NEXT_PUBLIC_API_BASE_URL?.trim() || "http://localhost:8000"
).replace(/\/$/, "");
const CSRF_COOKIE_NAME = "f1bot_csrf_token";

let cachedSession: SessionState | null = null;
let hasCachedSession = false;

function parseSessionPayload(value: unknown): SessionState | null {
  if (!value || typeof value !== "object") {
    return null;
  }

  const payload = value as SessionPayload;
  const userId = typeof payload.user_id === "string" ? payload.user_id.trim() : "";
  const email = typeof payload.email === "string" ? payload.email.trim() : "";

  if (!userId) {
    return null;
  }

  return {
    userId,
    email,
  };
}

function readCookie(name: string): string | null {
  if (typeof document === "undefined") {
    return null;
  }

  const encodedName = `${encodeURIComponent(name)}=`;
  const cookies = document.cookie ? document.cookie.split("; ") : [];
  for (const cookie of cookies) {
    if (!cookie.startsWith(encodedName)) {
      continue;
    }

    const rawValue = cookie.slice(encodedName.length);
    return decodeURIComponent(rawValue);
  }

  return null;
}

export function getCsrfToken(): string | null {
  return readCookie(CSRF_COOKIE_NAME);
}

export function saveSession(session: SessionState): void {
  cachedSession = session;
  hasCachedSession = true;
}

export function clearSessionCache(): void {
  cachedSession = null;
  hasCachedSession = false;
}

export async function getSession(forceRefresh = false): Promise<SessionState | null> {
  if (typeof window === "undefined") {
    return null;
  }

  if (!forceRefresh && hasCachedSession) {
    return cachedSession;
  }

  let response: Response;
  try {
    response = await fetch(`${API_BASE_URL}/api/auth/session`, {
      method: "GET",
      credentials: "include",
      cache: "no-store",
      headers: {
        Accept: "application/json",
      },
    });
  } catch {
    clearSessionCache();
    return null;
  }

  if (response.status === 401) {
    clearSessionCache();
    return null;
  }

  if (!response.ok) {
    clearSessionCache();
    return null;
  }

  try {
    const parsed = parseSessionPayload(await response.json());
    if (!parsed) {
      clearSessionCache();
      return null;
    }

    saveSession(parsed);
    return parsed;
  } catch {
    clearSessionCache();
    return null;
  }
}

export async function clearSession(): Promise<void> {
  if (typeof window !== "undefined") {
    const headers: Record<string, string> = { Accept: "application/json" };
    const csrfToken = getCsrfToken();
    if (csrfToken) {
      headers["X-CSRF-Token"] = csrfToken;
    }

    try {
      await fetch(`${API_BASE_URL}/api/auth/logout`, {
        method: "POST",
        credentials: "include",
        cache: "no-store",
        headers,
      });
    } catch {
      // Local cache still needs to be cleared even if network logout fails.
    }
  }

  clearSessionCache();
}

export async function hasSession(): Promise<boolean> {
  return Boolean(await getSession());
}
