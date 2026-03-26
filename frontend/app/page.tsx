"use client";

import { FormEvent, useMemo, useState } from "react";
import { scanLeads, type LeadInsight } from "@/lib/api";

const DEFAULT_SUBREDDITS = "entrepreneur,smallbusiness,marketing,sales";
const DEFAULT_KEYWORDS = "looking for,need help,recommend,best tool";

export default function HomePage() {
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

  const canSubmit = useMemo(
    () => businessDescription.trim().length > 10 && !loading,
    [businessDescription, loading]
  );

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
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
    <main className="mx-auto max-w-5xl px-6 py-10">
      <header className="mb-8">
        <h1 className="text-3xl font-semibold tracking-tight">F1bot</h1>
        <p className="mt-2 text-slate-600">
          Search relevant Reddit conversations and score them as potential leads.
        </p>
      </header>

      <section className="rounded-xl bg-white p-6 shadow-sm ring-1 ring-slate-200">
        <form onSubmit={handleSubmit} className="grid gap-4">
          <label className="grid gap-2">
            <span className="text-sm font-medium">Business Description</span>
            <textarea
              value={businessDescription}
              onChange={(event) => setBusinessDescription(event.target.value)}
              className="h-28 rounded-md border border-slate-300 p-3"
              placeholder="Describe your product or service"
            />
          </label>

          <div className="grid gap-4 md:grid-cols-2">
            <label className="grid gap-2">
              <span className="text-sm font-medium">Keywords (comma separated)</span>
              <input
                value={keywords}
                onChange={(event) => setKeywords(event.target.value)}
                className="rounded-md border border-slate-300 p-3"
                placeholder="need help, recommendation"
              />
            </label>

            <label className="grid gap-2">
              <span className="text-sm font-medium">Subreddits (comma separated)</span>
              <input
                value={subreddits}
                onChange={(event) => setSubreddits(event.target.value)}
                className="rounded-md border border-slate-300 p-3"
                placeholder="smallbusiness, entrepreneur"
              />
            </label>
          </div>

          <label className="grid gap-2 md:max-w-xs">
            <span className="text-sm font-medium">Max Results</span>
            <input
              type="number"
              min={1}
              max={100}
              value={limit}
              onChange={(event) => setLimit(Number(event.target.value) || 20)}
              className="rounded-md border border-slate-300 p-3"
            />
          </label>

          <button
            type="submit"
            disabled={!canSubmit}
            className="mt-2 inline-flex w-fit items-center rounded-md bg-slate-900 px-4 py-2 text-sm font-medium text-white disabled:opacity-50"
          >
            {loading ? "Scanning..." : "Find Leads"}
          </button>

          {error ? <p className="text-sm text-red-600">{error}</p> : null}
        </form>
      </section>

      <section className="mt-8">
        <div className="mb-4 flex flex-wrap items-center gap-3 text-sm text-slate-600">
          <span>{`Leads: ${leads.length}`}</span>
          <span>{`Candidates scanned: ${totalCandidates}`}</span>
          <span>{`AI scoring: ${usedAi ? "Enabled" : "Heuristic mode"}`}</span>
        </div>

        <div className="grid gap-4">
          {leads.map((lead) => (
            <article key={lead.post.id} className="rounded-xl bg-white p-5 shadow-sm ring-1 ring-slate-200">
              <div className="flex flex-wrap items-center justify-between gap-2">
                <h2 className="text-lg font-semibold">{lead.post.title}</h2>
                <span className="rounded-full bg-slate-100 px-3 py-1 text-sm font-medium">
                  Score: {lead.lead_score}
                </span>
              </div>

              <p className="mt-1 text-sm text-slate-500">r/{lead.post.subreddit}</p>
              <p className="mt-3 text-slate-700">{lead.qualification_reason}</p>
              <p className="mt-2 text-sm text-slate-600">Outreach idea: {lead.suggested_outreach}</p>

              <a
                href={lead.post.url}
                target="_blank"
                rel="noreferrer"
                className="mt-4 inline-flex text-sm font-medium text-slate-900 underline"
              >
                Open Reddit Post
              </a>
            </article>
          ))}

          {!loading && leads.length === 0 ? (
            <p className="text-sm text-slate-500">No leads yet. Submit the form to scan Reddit.</p>
          ) : null}
        </div>
      </section>
    </main>
  );
}
