import { getSession } from "@/lib/session";

export interface CandidatePost {
  id: string;
  title: string;
  body: string;
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
  access_token: string;
  token_type: string;
}

export interface RegisterRequest {
  email: string;
  password: string;
  full_name?: string;
}

export interface RegisterResponse {
  user_id: string;
  email: string;
  access_token: string;
  token_type: string;
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
  supabase_configured: boolean;
}

const processEnv =
  typeof globalThis === "object" && "process" in globalThis
    ? (globalThis as { process?: { env?: Record<string, string | undefined> } }).process?.env
    : undefined;

const API_BASE_URL = processEnv?.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

function getAuthorizationHeader(): Record<string, string> {
  const session = getSession();

  if (!session?.accessToken) {
    throw new Error("Authentication required. Please log in again.");
  }

  return {
    Authorization: `Bearer ${session.accessToken}`
  };
}

async function authenticatedFetch(path: string, init?: RequestInit): Promise<Response> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...init,
    headers: {
      ...getAuthorizationHeader(),
      ...(init?.headers ?? {})
    }
  });

  return response;
}

async function parseResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const contentType = response.headers.get("content-type") || "";
    if (contentType.includes("application/json")) {
      const data = (await response.json()) as { detail?: string };
      throw new Error(data.detail || "Request failed");
    }

    const text = await response.text();
    throw new Error(text || "Request failed");
  }
  return (await response.json()) as T;
}

export async function login(payload: LoginRequest): Promise<LoginResponse> {
  const response = await fetch(`${API_BASE_URL}/api/auth/login`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify(payload)
  });

  return parseResponse<LoginResponse>(response);
}

export async function register(payload: RegisterRequest): Promise<RegisterResponse> {
  const response = await fetch(`${API_BASE_URL}/api/auth/register`, {
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
  const response = await authenticatedFetch("/api/leads/scan", {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify(payload)
  });

  return parseResponse<LeadScanResponse>(response);
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

export async function downloadLeadsCsv(status?: LeadStatus): Promise<Blob> {
  const query = new URLSearchParams();
  if (status) {
    query.set("status", status);
  }

  const path = query.toString() ? `/api/leads/export.csv?${query.toString()}` : "/api/leads/export.csv";
  const response = await authenticatedFetch(path);
  if (!response.ok) {
    const text = await response.text();
    throw new Error(text || "Failed to export leads");
  }

  return response.blob();
}
