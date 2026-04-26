import { clearSession, clearSessionCache, getCsrfToken } from "@/lib/session";

export interface CandidatePost {
  id: string;
  title: string;
  body: string;
  match_source: "post" | "comment";
  subreddit: string;
  url: string;
  author: string;
  created_utc: string;
  score: number;
  num_comments: number;
}

export interface LeadInsight {
  post: CandidatePost;
  lead_score: number;
  qualification_reason: string;
  suggested_outreach: string;
}

export interface LeadScanRequest {
  business_description: string;
  keywords: string[];
  subreddits: string[];
  limit: number;
}

export interface LeadScanResponse {
  leads: LeadInsight[];
  total_candidates: number;
  used_ai: boolean;
}

export type LeadStatus = "new" | "contacted" | "qualified" | "ignored";

export interface LoginRequest {
  email: string;
  password: string;
}

export interface LoginResponse {
  user_id: string;
  email: string;
  access_token?: string;
  token_type?: string;
}

export interface RegisterRequest {
  email: string;
  password: string;
  full_name?: string;
}

export interface RegisterResponse {
  user_id: string;
  email: string;
  access_token?: string;
  token_type?: string;
}

export interface BusinessProfile {
  user_id: string;
  business_description: string;
  keywords: string[];
  subreddits: string[];
  updated_at?: string;
}

export interface SaveProfileRequest {
  business_description: string;
  keywords: string[];
  subreddits: string[];
}

export interface LeadRecord {
  id: string;
  user_id: string;
  status: LeadStatus;
  post: CandidatePost;
  lead_score: number;
  qualification_reason: string;
  suggested_outreach: string;
  scan_id: string;
  created_at: string;
  updated_at: string;
}

export interface LeadListResponse {
  leads: LeadRecord[];
}

export interface RuntimeSettingsResponse {
  environment: string;
  gemini_configured: boolean;
  reddit_configured: boolean;
  sample_leads_fallback_enabled: boolean;
  supabase_configured: boolean;
  supabase_auth_enabled: boolean;
  scan_rate_limit_per_minute: number;
  scan_rate_limit_window_seconds: number;
  scan_daily_quota: number;
}

export interface RuntimeHealthResponse {
  status: string;
  environment: string;
  gemini_configured: boolean;
  reddit_configured: boolean;
}

interface FastApiValidationError {
  loc: Array<string | number>;
  msg: string;
  type: string;
}

interface FastApiErrorPayload {
  detail?: string | FastApiValidationError[];
}

const configuredApiBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL?.trim() || "http://localhost:8000";
const shouldUseProxy =
  typeof window !== "undefined" &&
  window.location.protocol === "https:" &&
  configuredApiBaseUrl.startsWith("http://");

const API_BASE_URL = (shouldUseProxy ? "/backend" : configuredApiBaseUrl).replace(/\/$/, "");
const CSRF_HEADER_NAME = "X-CSRF-Token";
const SCAN_REQUEST_TIMEOUT_MS = 90_000;

function toHeaderObject(headers?: HeadersInit): Record<string, string> {
  if (!headers) {
    return {};
  }

  if (headers instanceof Headers) {
    return Object.fromEntries(headers.entries());
  }

  if (Array.isArray(headers)) {
    return Object.fromEntries(headers);
  }

  return { ...headers };
}

function requiresCsrf(method?: string): boolean {
  const normalized = (method || "GET").toUpperCase();
  return normalized === "POST" || normalized === "PUT" || normalized === "PATCH" || normalized === "DELETE";
}

function isAbortError(error: unknown): boolean {
  return error instanceof Error && error.name === "AbortError";
}

function buildCsrfHeader(method?: string): Record<string, string> {
  if (!requiresCsrf(method)) {
    return {};
  }

  const csrfToken = getCsrfToken();
  if (!csrfToken?.trim()) {
    throw new Error("Session security token missing. Please log in again.");
  }

  return {
    [CSRF_HEADER_NAME]: csrfToken,
  };
}

function formatValidationErrors(errors: FastApiValidationError[]): string {
  const messages = errors
    .map((entry) => {
      const field = entry.loc
        .map((value) => String(value))
        .filter((value) => value !== "body" && value !== "query" && value !== "path")
        .join(".");

      return field ? `${field}: ${entry.msg}` : entry.msg;
    })
    .filter(Boolean);

  return messages.length > 0 ? messages.join("; ") : "Request validation failed";
}

async function parseErrorResponse(response: Response): Promise<string> {
  const contentType = response.headers.get("content-type") || "";
  if (contentType.includes("application/json")) {
    try {
      const payload = (await response.json()) as FastApiErrorPayload;
      if (typeof payload.detail === "string" && payload.detail.trim().length > 0) {
        return payload.detail;
      }
      if (Array.isArray(payload.detail)) {
        return formatValidationErrors(payload.detail);
      }
    } catch {
      // Fallback to plain text when JSON parsing fails.
    }
  }

  const text = await response.text();
  return text || `Request failed with status ${response.status}`;
}

function handleUnauthorizedResponse(): never {
  clearSessionCache();
  void clearSession();

  if (typeof window !== "undefined") {
    window.location.assign("/login");
  }

  throw new Error("Session expired. Please log in again.");
}

async function apiFetch(path: string, init?: RequestInit): Promise<Response> {
  let response: Response;

  try {
    response = await fetch(`${API_BASE_URL}${path}`, {
      ...init,
      cache: init?.cache ?? "no-store",
      credentials: init?.credentials ?? "include",
      headers: {
        Accept: "application/json",
        ...toHeaderObject(init?.headers)
      }
    });
  } catch (error) {
    if (isAbortError(error)) {
      throw new Error("Scan timed out. Try fewer keywords/subreddits and run again.");
    }
    throw new Error(`Unable to connect to API (${API_BASE_URL}).`);
  }

  return response;
}

async function authenticatedFetch(path: string, init?: RequestInit): Promise<Response> {
  const response = await apiFetch(path, {
    ...init,
    headers: {
      ...buildCsrfHeader(init?.method),
      ...toHeaderObject(init?.headers),
    },
  });

  if (response.status === 401) {
    handleUnauthorizedResponse();
  }

  return response;
}

async function parseResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    throw new Error(await parseErrorResponse(response));
  }

  if (response.status === 204) {
    return undefined as T;
  }

  return (await response.json()) as T;
}

async function parseBlobResponse(response: Response): Promise<Blob> {
  if (!response.ok) {
    throw new Error(await parseErrorResponse(response));
  }

  return response.blob();
}

export async function login(payload: LoginRequest): Promise<LoginResponse> {
  const response = await apiFetch("/api/auth/login", {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify(payload)
  });

  return parseResponse<LoginResponse>(response);
}

export async function register(payload: RegisterRequest): Promise<RegisterResponse> {
  const response = await apiFetch("/api/auth/register", {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify(payload)
  });

  return parseResponse<RegisterResponse>(response);
}

export async function getProfile(): Promise<BusinessProfile> {
  const response = await authenticatedFetch("/api/profile");
  return parseResponse<BusinessProfile>(response);
}

export async function saveProfile(payload: SaveProfileRequest): Promise<BusinessProfile> {
  const response = await authenticatedFetch("/api/profile", {
    method: "PUT",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify(payload)
  });

  return parseResponse<BusinessProfile>(response);
}

export async function scanLeads(payload: LeadScanRequest): Promise<LeadScanResponse> {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), SCAN_REQUEST_TIMEOUT_MS);

  try {
    const response = await authenticatedFetch("/api/leads/scan", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify(payload),
      signal: controller.signal,
    });

    return parseResponse<LeadScanResponse>(response);
  } finally {
    clearTimeout(timeoutId);
  }
}

export async function getLeads(status?: LeadStatus): Promise<LeadListResponse> {
  const query = new URLSearchParams();
  if (status) {
    query.set("status", status);
  }

  const path = query.toString() ? `/api/leads?${query.toString()}` : "/api/leads";
  const response = await authenticatedFetch(path);
  return parseResponse<LeadListResponse>(response);
}

export async function getLeadById(leadId: string): Promise<LeadRecord> {
  const response = await authenticatedFetch(`/api/leads/${leadId}`);
  return parseResponse<LeadRecord>(response);
}

export async function updateLeadStatus(
  leadId: string,
  status: LeadStatus
): Promise<LeadRecord> {
  const response = await authenticatedFetch(`/api/leads/${leadId}/status`, {
    method: "PATCH",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({ status })
  });

  return parseResponse<LeadRecord>(response);
}

export async function getRuntimeSettings(): Promise<RuntimeSettingsResponse> {
  const response = await authenticatedFetch("/api/settings");
  return parseResponse<RuntimeSettingsResponse>(response);
}

export async function getHealth(): Promise<RuntimeHealthResponse> {
  const response = await authenticatedFetch("/api/health");
  return parseResponse<RuntimeHealthResponse>(response);
}

export async function downloadLeadsCsv(status?: LeadStatus): Promise<Blob> {
  const query = new URLSearchParams();
  if (status) {
    query.set("status", status);
  }

  const path = query.toString() ? `/api/leads/export.csv?${query.toString()}` : "/api/leads/export.csv";
  const response = await authenticatedFetch(path, {
    headers: {
      Accept: "text/csv"
    }
  });

  return parseBlobResponse(response);
}
