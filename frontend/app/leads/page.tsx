"use client";

import Link from "next/link";
import { useCallback, useEffect, useMemo, useState } from "react";
import { getLeads, type LeadRecord, type LeadStatus } from "@/lib/api";
import { useSessionGuard } from "@/lib/use-session-guard";

const STATUS_OPTIONS: Array<LeadStatus | "all"> = ["all", "new", "contacted", "qualified", "ignored"];
const INITIAL_VISIBLE_LEADS = 24;

export default function LeadsPage() {
  const { session, isCheckingSession } = useSessionGuard();
  const [statusFilter, setStatusFilter] = useState<LeadStatus | "all">("all");
  const [leads, setLeads] = useState<LeadRecord[]>([]);
  const [visibleCount, setVisibleCount] = useState(INITIAL_VISIBLE_LEADS);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadLeads = useCallback(async (nextStatus: LeadStatus | "all") => {
    if (!session?.accessToken) {
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await getLeads(nextStatus === "all" ? undefined : nextStatus);
      setLeads(response.leads);
      setVisibleCount(INITIAL_VISIBLE_LEADS);
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : "Failed to load leads");
    } finally {
      setLoading(false);
    }
  }, [session?.accessToken]);

  useEffect(() => {
    if (!session?.accessToken) {
      return;
    }
    loadLeads("all");
  }, [loadLeads, session?.accessToken]);

  const totalByStatus = useMemo(() => {
    return leads.reduce(
      (acc, item) => {
        acc[item.status] += 1;
        return acc;
      },
      { new: 0, contacted: 0, qualified: 0, ignored: 0 } as Record<LeadStatus, number>
    );
  }, [leads]);

  const visibleLeads = useMemo(() => leads.slice(0, visibleCount), [leads, visibleCount]);

  if (isCheckingSession) {
    return <main className="mx-auto max-w-4xl px-6 py-10 text-brand-navy/75">Checking your session...</main>;
  }

  return (
    <main className="mx-auto flex h-[calc(100dvh-4.5rem)] max-w-6xl flex-col overflow-hidden px-6 py-6 md:py-8">
      <div className="shrink-0 pb-4">
        <div className="leads-sticky-bg">
          <div className="brand-card relative overflow-hidden p-6 md:p-7">
            <div className="pointer-events-none absolute -right-10 top-0 h-32 w-32 rounded-full bg-brand-gold/25 blur-2xl" />
            <div className="pointer-events-none absolute -left-10 bottom-0 h-28 w-28 rounded-full bg-brand-orange/24 blur-2xl" />

            <div>
              <p className="text-xs tracking-[0.24em] text-brand-burgundy/80">LEADS INBOX</p>
              <h1 className="mt-1 text-3xl font-semibold text-brand-burgundy" style={{ fontFamily: "var(--font-fraunces)" }}>
                Review And Qualify Leads
              </h1>
              <p className="mt-2 text-sm text-brand-navy/75">Filter by status, open full context, and keep your pipeline moving.</p>
            </div>

            <div className="mt-4 flex flex-wrap items-end gap-3 md:mt-5">
              <label className="grid gap-1">
                <span className="text-xs uppercase tracking-[0.14em] text-brand-burgundy/80">Status Filter</span>
                <select
                  value={statusFilter}
                  onChange={(event) => {
                    const next = event.target.value as LeadStatus | "all";
                    setStatusFilter(next);
                    loadLeads(next);
                  }}
                  className="brand-select min-w-40 text-sm"
                >
                  {STATUS_OPTIONS.map((item) => (
                    <option key={item} value={item}>
                      {item}
                    </option>
                  ))}
                </select>
              </label>
              <span className="brand-badge">Showing: {visibleLeads.length} / {leads.length}</span>
            </div>
          </div>

          <div className="mt-4 grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
            <div className="brand-stat">
              <p className="text-xs uppercase tracking-[0.14em] text-brand-burgundy/70">New</p>
              <p className="mt-1 text-xl font-semibold text-brand-navy">{totalByStatus.new}</p>
            </div>
            <div className="brand-stat">
              <p className="text-xs uppercase tracking-[0.14em] text-brand-burgundy/70">Contacted</p>
              <p className="mt-1 text-xl font-semibold text-brand-navy">{totalByStatus.contacted}</p>
            </div>
            <div className="brand-stat">
              <p className="text-xs uppercase tracking-[0.14em] text-brand-burgundy/70">Qualified</p>
              <p className="mt-1 text-xl font-semibold text-brand-navy">{totalByStatus.qualified}</p>
            </div>
            <div className="brand-stat">
              <p className="text-xs uppercase tracking-[0.14em] text-brand-burgundy/70">Ignored</p>
              <p className="mt-1 text-xl font-semibold text-brand-navy">{totalByStatus.ignored}</p>
            </div>
          </div>
        </div>

        {error ? <p className="mt-4 text-sm text-brand-burgundy">{error}</p> : null}
      </div>

      <section className="grid min-h-0 flex-1 gap-4 overflow-y-auto pb-4 pr-1">
        {loading ? <p className="text-brand-navy/70">Loading leads...</p> : null}

        {!loading && leads.length === 0 ? <p className="text-brand-navy/70">No leads found.</p> : null}

        {visibleLeads.map((lead) => (
          <article key={lead.id} className="brand-card p-5">
            <div className="flex flex-wrap items-center justify-between gap-2">
              <h2 className="text-lg font-semibold text-brand-navy">{lead.post.title}</h2>
              <span className="brand-badge">
                {lead.status.toUpperCase()} · {lead.lead_score}
              </span>
            </div>

            <p className="mt-2 text-sm text-brand-navy/70">r/{lead.post.subreddit}</p>
            <p className="mt-3 text-sm text-brand-navy/90">{lead.qualification_reason}</p>

            <div className="mt-4 flex flex-wrap items-center gap-3">
              <Link
                href={`/leads/${lead.id}`}
                className="brand-btn-primary px-3 py-2 text-sm"
              >
                Open Lead
              </Link>
              <a
                href={lead.post.url}
                target="_blank"
                rel="noreferrer"
                className="text-sm font-medium text-brand-burgundy underline decoration-brand-orange underline-offset-2"
              >
                Reddit Post
              </a>
            </div>
          </article>
        ))}

        {!loading && visibleLeads.length < leads.length ? (
          <button
            type="button"
            onClick={() => setVisibleCount((current) => current + INITIAL_VISIBLE_LEADS)}
            className="brand-btn-secondary mx-auto mt-2 w-fit px-4 py-2 text-sm"
          >
            Show More Leads
          </button>
        ) : null}
      </section>
    </main>
  );
}
