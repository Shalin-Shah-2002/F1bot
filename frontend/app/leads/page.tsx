"use client";

import Link from "next/link";
import { useEffect, useMemo, useState } from "react";
import { useRouter } from "next/navigation";
import { getLeads, type LeadRecord, type LeadStatus } from "@/lib/api";
import { getSession } from "@/lib/session";

const STATUS_OPTIONS: Array<LeadStatus | "all"> = ["all", "new", "contacted", "qualified", "ignored"];

export default function LeadsPage() {
  const router = useRouter();
  const session = getSession();
  const [statusFilter, setStatusFilter] = useState<LeadStatus | "all">("all");
  const [leads, setLeads] = useState<LeadRecord[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  async function loadLeads(nextStatus: LeadStatus | "all" = statusFilter) {
    if (!session) {
      return;
    }
    setLoading(true);
    setError(null);

    try {
      const response = await getLeads(nextStatus === "all" ? undefined : nextStatus);
      setLeads(response.leads);
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : "Failed to load leads");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    if (!session) {
      router.push("/login");
      return;
    }
    loadLeads("all");
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [router, session]);

  const totalByStatus = useMemo(() => {
    return leads.reduce(
      (acc, item) => {
        acc[item.status] += 1;
        return acc;
      },
      { new: 0, contacted: 0, qualified: 0, ignored: 0 } as Record<LeadStatus, number>
    );
  }, [leads]);

  return (
    <main className="mx-auto max-w-6xl px-6 py-10">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-semibold text-brand-burgundy">Leads Inbox</h1>
          <p className="mt-2 text-sm text-brand-navy/75">Review, prioritize, and update lead status.</p>
        </div>

        <div className="flex items-center gap-2">
          <label className="text-sm text-brand-burgundy">Status</label>
          <select
            value={statusFilter}
            onChange={(event) => {
              const next = event.target.value as LeadStatus | "all";
              setStatusFilter(next);
              loadLeads(next);
            }}
            className="rounded-md border border-brand-navy/25 bg-white px-3 py-2 text-sm text-brand-navy focus:border-brand-gold focus:outline-none"
          >
            {STATUS_OPTIONS.map((item) => (
              <option key={item} value={item}>
                {item}
              </option>
            ))}
          </select>
        </div>
      </div>

      <div className="mt-4 flex flex-wrap gap-2 text-sm">
        <span className="rounded-full bg-white/70 px-3 py-1 ring-1 ring-brand-navy/15">New: {totalByStatus.new}</span>
        <span className="rounded-full bg-white/70 px-3 py-1 ring-1 ring-brand-navy/15">Contacted: {totalByStatus.contacted}</span>
        <span className="rounded-full bg-white/70 px-3 py-1 ring-1 ring-brand-navy/15">Qualified: {totalByStatus.qualified}</span>
        <span className="rounded-full bg-white/70 px-3 py-1 ring-1 ring-brand-navy/15">Ignored: {totalByStatus.ignored}</span>
      </div>

      {error ? <p className="mt-4 text-sm text-brand-burgundy">{error}</p> : null}

      <section className="mt-6 grid gap-4">
        {loading ? <p className="text-brand-navy/70">Loading leads...</p> : null}

        {!loading && leads.length === 0 ? <p className="text-brand-navy/70">No leads found.</p> : null}

        {leads.map((lead) => (
          <article key={lead.id} className="rounded-xl bg-white/80 p-5 shadow-md ring-1 ring-brand-navy/20">
            <div className="flex flex-wrap items-center justify-between gap-2">
              <h2 className="text-lg font-semibold text-brand-navy">{lead.post.title}</h2>
              <span className="rounded-full bg-brand-gold/35 px-3 py-1 text-sm font-medium text-brand-burgundy">
                {lead.status.toUpperCase()} · {lead.lead_score}
              </span>
            </div>

            <p className="mt-2 text-sm text-brand-navy/70">r/{lead.post.subreddit}</p>
            <p className="mt-3 text-sm text-brand-navy/90">{lead.qualification_reason}</p>

            <div className="mt-4 flex flex-wrap items-center gap-3">
              <Link
                href={`/leads/${lead.id}`}
                className="rounded-md bg-brand-orange px-3 py-2 text-sm font-medium text-brand-cream hover:bg-brand-burgundy"
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
      </section>
    </main>
  );
}
