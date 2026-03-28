"use client";

import { FormEvent, useEffect, useMemo, useState } from "react";
import { useRouter } from "next/navigation";
import { getProfile, scanLeads, type LeadInsight } from "@/lib/api";
import { getSession } from "@/lib/session";

const DEFAULT_SUBREDDITS = "entrepreneur,smallbusiness,marketing,sales";
const DEFAULT_KEYWORDS = "looking for,need help,recommend,best tool";

export default function ScanPage() {
  const router = useRouter();
  const session = getSession();
  const hasSession = Boolean(session?.accessToken);
  const [businessDescription, setBusinessDescription] = useState(
    "We help D2C founders generate better leads and improve conversion."
  );
  const [keywords, setKeywords] = useState(DEFAULT_KEYWORDS);
  const [subreddits, setSubreddits] = useState(DEFAULT_SUBREDDITS);
  const [limit, setLimit] = useState(20);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [leads, setLeads] = useState<LeadInsight[]>([]);
  const [usedAi, setUsedAi] = useState(false);
  const [totalCandidates, setTotalCandidates] = useState(0);

  useEffect(() => {
    if (!hasSession) {
      router.push("/login");
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
  }, [hasSession, router]);

  const canSubmit = useMemo(
    () => businessDescription.trim().length > 10 && !loading,
    [businessDescription, loading]
  );

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!hasSession) {
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
        limit
      });

      setLeads(response.leads);
      setUsedAi(response.used_ai);
      setTotalCandidates(response.total_candidates);
    } catch (scanError) {
      setError(scanError instanceof Error ? scanError.message : "Failed to scan leads");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="mx-auto max-w-5xl px-6 py-10 text-brand-navy">
      <header className="mb-8">
        <h1 className="text-3xl font-semibold tracking-tight text-brand-burgundy">Manual Lead Scan</h1>
        <p className="mt-2 text-brand-navy/80">Search relevant Reddit conversations and score potential leads.</p>
      </header>

      <section className="rounded-xl bg-white/75 p-6 shadow-md ring-1 ring-brand-navy/20 backdrop-blur-sm">
        <form onSubmit={handleSubmit} className="grid gap-4">
          <label className="grid gap-2">
            <span className="text-sm font-medium text-brand-burgundy">Business Description</span>
            <textarea
              value={businessDescription}
              onChange={(event) => setBusinessDescription(event.target.value)}
              className="h-28 rounded-md border border-brand-navy/30 bg-white/90 p-3 focus:border-brand-gold focus:outline-none"
              placeholder="Describe your product or service"
            />
          </label>

          <div className="grid gap-4 md:grid-cols-2">
            <label className="grid gap-2">
              <span className="text-sm font-medium text-brand-burgundy">Keywords (comma separated)</span>
              <input
                value={keywords}
                onChange={(event) => setKeywords(event.target.value)}
                className="rounded-md border border-brand-navy/30 bg-white/90 p-3 focus:border-brand-gold focus:outline-none"
              />
            </label>

            <label className="grid gap-2">
              <span className="text-sm font-medium text-brand-burgundy">Subreddits (comma separated)</span>
              <input
                value={subreddits}
                onChange={(event) => setSubreddits(event.target.value)}
                className="rounded-md border border-brand-navy/30 bg-white/90 p-3 focus:border-brand-gold focus:outline-none"
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
              onChange={(event) => setLimit(Number(event.target.value) || 20)}
              className="rounded-md border border-brand-navy/30 bg-white/90 p-3 focus:border-brand-gold focus:outline-none"
            />
          </label>

          <div className="flex flex-wrap items-center gap-3">
            <button
              type="submit"
              disabled={!canSubmit}
              className="inline-flex w-fit items-center rounded-md bg-brand-orange px-4 py-2 text-sm font-medium text-brand-cream transition-colors hover:bg-brand-burgundy disabled:cursor-not-allowed disabled:opacity-50"
            >
              {loading ? "Scanning..." : "Find Leads"}
            </button>

            <button
              type="button"
              onClick={() => router.push("/leads")}
              className="rounded-md bg-brand-navy px-4 py-2 text-sm font-medium text-brand-cream hover:bg-brand-burgundy"
            >
              Open Leads Inbox
            </button>
          </div>

          {error ? <p className="text-sm text-brand-burgundy">{error}</p> : null}
        </form>
      </section>

      <section className="mt-8">
        <div className="mb-4 flex flex-wrap items-center gap-3 text-sm text-brand-navy/85">
          <span className="rounded-full bg-white/60 px-3 py-1 ring-1 ring-brand-navy/15">{`Leads: ${leads.length}`}</span>
          <span className="rounded-full bg-white/60 px-3 py-1 ring-1 ring-brand-navy/15">{`Candidates scanned: ${totalCandidates}`}</span>
          <span className="rounded-full bg-white/60 px-3 py-1 ring-1 ring-brand-navy/15">{`AI scoring: ${usedAi ? "Enabled" : "Heuristic mode"}`}</span>
        </div>

        <div className="grid gap-4">
          {leads.map((lead) => (
            <article key={lead.post.id} className="rounded-xl bg-white/75 p-5 shadow-md ring-1 ring-brand-navy/20 backdrop-blur-sm">
              <div className="flex flex-wrap items-center justify-between gap-2">
                <h2 className="text-lg font-semibold">{lead.post.title}</h2>
                <span className="rounded-full bg-brand-gold/30 px-3 py-1 text-sm font-medium text-brand-burgundy ring-1 ring-brand-orange/25">
                  Score: {lead.lead_score}
                </span>
              </div>

              <p className="mt-1 text-sm text-brand-navy/70">r/{lead.post.subreddit}</p>
              <p className="mt-3 text-brand-navy/95">{lead.qualification_reason}</p>
              <p className="mt-2 text-sm text-brand-orange">Outreach idea: {lead.suggested_outreach}</p>

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
