"use client";

import { FormEvent, useEffect, useMemo, useState } from "react";
import { useRouter } from "next/navigation";
import { getProfile, scanLeads, type LeadInsight } from "@/lib/api";
import { useSessionGuard } from "@/lib/use-session-guard";

const DEFAULT_SUBREDDITS = "loseit,CICO,nutrition,weightlossadvice,Fitness,MealPrepSunday,PCOSloseit";
const DEFAULT_KEYWORDS = "calorie tracker,calorie counting app,macro tracking,lose weight app,weight loss plateau,fitness app recommendation";

export default function ScanPage() {
  const router = useRouter();
  const { session, isCheckingSession } = useSessionGuard();
  const [businessDescription, setBusinessDescription] = useState(
    "CalPal is a calorie tracker that helps people lose weight consistently with simple meal logging, macro guidance, and accountability nudges."
  );
  const [keywords, setKeywords] = useState(DEFAULT_KEYWORDS);
  const [subreddits, setSubreddits] = useState(DEFAULT_SUBREDDITS);
  const [limit, setLimit] = useState(15);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [leads, setLeads] = useState<LeadInsight[]>([]);
  const [usedAi, setUsedAi] = useState(false);
  const [totalCandidates, setTotalCandidates] = useState(0);
  // Tracks how many scans have completed so we can adapt UI for repeat scans.
  const [scanCount, setScanCount] = useState(0);

  useEffect(() => {
    if (!session) {
      return;
    }

    async function hydrateFromProfile() {
      try {
        const profile = await getProfile();
        setBusinessDescription(profile.business_description);
        if (profile.keywords.length) {
          setKeywords(profile.keywords.join(","));
        }
        if (profile.subreddits.length) {
          setSubreddits(profile.subreddits.join(","));
        }
      } catch {
        // Use current defaults when profile does not exist.
      }
    }

    hydrateFromProfile();
  }, [session]);

  const canSubmit = useMemo(
    () => businessDescription.trim().length > 10 && !loading,
    [businessDescription, loading]
  );

  const keywordCount = useMemo(
    () =>
      keywords
        .split(",")
        .map((item) => item.trim())
        .filter(Boolean).length,
    [keywords]
  );

  const subredditCount = useMemo(
    () =>
      subreddits
        .split(",")
        .map((item) => item.trim())
        .filter(Boolean).length,
    [subreddits]
  );

  const sourceBreakdown = useMemo(() => {
    return leads.reduce(
      (acc, lead) => {
        if (lead.post.match_source === "comment") {
          acc.comment += 1;
          return acc;
        }
        acc.post += 1;
        return acc;
      },
      { post: 0, comment: 0 }
    );
  }, [leads]);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!session) {
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await scanLeads({
        business_description: businessDescription,
        keywords: keywords
          .split(",")
          .map((item) => item.trim())
          .filter(Boolean),
        subreddits: subreddits
          .split(",")
          .map((item) => item.trim())
          .filter(Boolean),
        limit,
      });

      setLeads(response.leads);
      setUsedAi(response.used_ai);
      setTotalCandidates(response.total_candidates);
      setScanCount((prev) => prev + 1);
    } catch (scanError) {
      setError(scanError instanceof Error ? scanError.message : "Failed to scan leads");
    } finally {
      setLoading(false);
    }
  }

  if (isCheckingSession) {
    return <main className="mx-auto max-w-4xl px-6 py-10 text-brand-navy/75">Checking your session...</main>;
  }

  // After the first scan the button label and UX update to reflect that repeat
  // scans return *fresh* leads (deduplication is handled server-side).
  const isRepeatScan = scanCount > 0;
  const submitLabel = loading
    ? isRepeatScan
      ? "Fetching fresh leads\u2026"
      : "Scanning\u2026"
    : isRepeatScan
      ? "\u21bb  Scan for Fresh Leads"
      : "Find Leads";

  return (
    <main className="mx-auto max-w-5xl px-6 py-10 text-brand-navy">
      <header className="brand-card relative mb-8 overflow-hidden p-6 md:p-8">
        <div className="pointer-events-none absolute -right-8 -top-8 h-36 w-36 rounded-full bg-brand-gold/30 blur-2xl" />
        <div className="pointer-events-none absolute -left-8 bottom-0 h-28 w-28 rounded-full bg-brand-orange/28 blur-2xl" />

        <p className="relative text-xs tracking-[0.24em] text-brand-burgundy/80">SCAN WORKSPACE</p>
        <h1
          className="relative mt-2 text-3xl font-semibold tracking-tight text-brand-burgundy md:text-4xl"
          style={{ fontFamily: "var(--font-fraunces)" }}
        >
          Find High-Intent Reddit Leads
        </h1>
        <p className="relative mt-2 max-w-2xl text-sm text-brand-navy/80 md:text-base">
          Send targeting context to your backend pipeline, score opportunities, then move qualified leads to outreach.
        </p>

        <div className="relative mt-5 grid gap-3 sm:grid-cols-4">
          <div className="brand-stat">
            <p className="text-xs uppercase tracking-[0.14em] text-brand-burgundy/70">Keywords</p>
            <p className="mt-1 text-lg font-semibold text-brand-navy">{keywordCount}</p>
          </div>
          <div className="brand-stat">
            <p className="text-xs uppercase tracking-[0.14em] text-brand-burgundy/70">Subreddits</p>
            <p className="mt-1 text-lg font-semibold text-brand-navy">{subredditCount}</p>
          </div>
          <div className="brand-stat">
            <p className="text-xs uppercase tracking-[0.14em] text-brand-burgundy/70">Max Results</p>
            <p className="mt-1 text-lg font-semibold text-brand-navy">{limit}</p>
          </div>
          <div className="brand-stat">
            <p className="text-xs uppercase tracking-[0.14em] text-brand-burgundy/70">Signed In</p>
            <p className="mt-1 truncate text-sm font-semibold text-brand-navy">{session?.email ?? "Unknown"}</p>
          </div>
        </div>
      </header>

      <section className="brand-card p-6 md:p-7">
        <form onSubmit={handleSubmit} className="grid gap-4">
          <label className="grid gap-2">
            <span className="text-sm font-medium text-brand-burgundy">Business Description</span>
            <textarea
              value={businessDescription}
              onChange={(event) => setBusinessDescription(event.target.value)}
              className="brand-input h-32 resize-y"
              placeholder="Describe your product or service"
            />
          </label>

          <div className="grid gap-4 md:grid-cols-2">
            <label className="grid gap-2">
              <span className="text-sm font-medium text-brand-burgundy">Keywords (comma separated)</span>
              <input
                value={keywords}
                onChange={(event) => setKeywords(event.target.value)}
                className="brand-input"
              />
            </label>

            <label className="grid gap-2">
              <span className="text-sm font-medium text-brand-burgundy">Subreddits (comma separated)</span>
              <input
                value={subreddits}
                onChange={(event) => setSubreddits(event.target.value)}
                className="brand-input"
              />
            </label>
          </div>

          <label className="grid gap-2 md:max-w-xs">
            <span className="text-sm font-medium text-brand-burgundy">Max Results</span>
            <input
              type="number"
              min={1}
              max={100}
              value={limit}
              onChange={(event) => setLimit(Number(event.target.value) || 15)}
              className="brand-input"
            />
          </label>

          <div className="flex flex-wrap items-center gap-3">
            <button
              type="submit"
              disabled={!canSubmit}
              className="brand-btn-primary inline-flex w-fit items-center px-4 py-2.5 text-sm disabled:cursor-not-allowed disabled:opacity-50"
            >
              {submitLabel}
            </button>

            <button
              type="button"
              onClick={() => router.push("/leads")}
              className="brand-btn-secondary px-4 py-2.5 text-sm"
            >
              Open Leads Inbox
            </button>
          </div>

          {/* Deduplication hint — shown after the first completed scan */}
          {isRepeatScan && !loading && (
            <p className="flex items-center gap-2 text-xs text-brand-navy/60">
              <span className="inline-flex items-center gap-1 rounded-full bg-green-100 px-2.5 py-0.5 text-xs font-medium text-green-700">
                ✓ Deduplication active
              </span>
              Each scan automatically skips posts you&apos;ve already seen and widens the time window to surface fresh leads.
            </p>
          )}

          {error ? <p className="text-sm text-brand-burgundy">{error}</p> : null}
        </form>
      </section>

      <section className="mt-8">
        <div className="mb-4 flex flex-wrap items-center gap-3 text-sm text-brand-navy/85">
          <span className="brand-badge">
            {isRepeatScan ? "New this scan" : "Leads"}: {leads.length}
          </span>
          <span className="brand-badge">Candidates scanned: {totalCandidates}</span>
          <span className="brand-badge">POST: {sourceBreakdown.post}</span>
          <span className="brand-badge">COMMENTS: {sourceBreakdown.comment}</span>
          <span className="brand-badge">AI scoring: {usedAi ? "Enabled" : "Heuristic mode"}</span>
          {scanCount > 1 && <span className="brand-badge">Scans run: {scanCount}</span>}
        </div>

        <div className="grid gap-4">
          {leads.map((lead) => (
            <article key={lead.post.id} className="brand-card p-5">
              <div className="flex flex-wrap items-center justify-between gap-2">
                <h2 className="text-lg font-semibold">{lead.post.title}</h2>
                <div className="flex flex-wrap items-center gap-2">
                  <span className="brand-badge">
                    Source: {lead.post.match_source === "comment" ? "COMMENTS" : "POST"}
                  </span>
                  <span className="brand-badge">Score: {lead.lead_score}</span>
                </div>
              </div>

              <p className="mt-1 text-sm text-brand-navy/70">r/{lead.post.subreddit}</p>
              <p className="mt-3 text-brand-navy/95">{lead.qualification_reason}</p>
              <p className="mt-2 text-sm text-brand-orange">Outreach idea: {lead.suggested_outreach}</p>
              {lead.post.body ? (
                <p className="mt-3 line-clamp-2 text-sm text-brand-navy/75">{lead.post.body}</p>
              ) : null}

              <a
                href={lead.post.url}
                target="_blank"
                rel="noreferrer"
                className="mt-4 inline-flex text-sm font-medium text-brand-burgundy underline decoration-brand-orange underline-offset-2 transition-colors hover:text-brand-orange"
              >
                Open Reddit Post
              </a>
            </article>
          ))}

          {!loading && leads.length === 0 ? (
            <p className="text-sm text-brand-navy/70">No leads yet. Submit the form to scan Reddit.</p>
          ) : null}
        </div>
      </section>
    </main>
  );
}
