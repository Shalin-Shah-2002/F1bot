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

const processEnv =
  typeof globalThis === "object" && "process" in globalThis
    ? (globalThis as { process?: { env?: Record<string, string | undefined> } }).process?.env
    : undefined;

const API_BASE_URL = processEnv?.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

export async function scanLeads(payload: LeadScanRequest): Promise<LeadScanResponse> {
  const response = await fetch(`${API_BASE_URL}/api/leads/scan`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify(payload)
  });

  if (!response.ok) {
    const text = await response.text();
    throw new Error(text || "Failed to scan leads");
  }

  return (await response.json()) as LeadScanResponse;
}
