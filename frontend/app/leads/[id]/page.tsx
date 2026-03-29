"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import { getLeadById, updateLeadStatus, type LeadRecord, type LeadStatus } from "@/lib/api";
import { useSessionGuard } from "@/lib/use-session-guard";

const STATUS_OPTIONS: LeadStatus[] = ["new", "contacted", "qualified", "ignored"];

export default function LeadDetailPage() {
  const params = useParams<{ id: string }>();
  const { session, isCheckingSession } = useSessionGuard();
  const [lead, setLead] = useState<LeadRecord | null>(null);
  const [status, setStatus] = useState<LeadStatus>("new");
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState<string | null>(null);

  useEffect(() => {
    if (!session?.accessToken) {
      return;
    }

    async function loadLead() {
      setLoading(true);
      setMessage(null);
      try {
        const data = await getLeadById(params.id);
        setLead(data);
        setStatus(data.status);
      } catch (requestError) {
        setMessage(requestError instanceof Error ? requestError.message : "Failed to load lead");
      } finally {
        setLoading(false);
      }
    }

    loadLead();
  }, [params.id, session?.accessToken]);

  async function handleUpdateStatus() {
    if (!session?.accessToken || !lead) {
      return;
    }

    setSaving(true);
    setMessage(null);
    try {
      const updated = await updateLeadStatus(lead.id, status);
      setLead(updated);
      setMessage("Status updated.");
    } catch (requestError) {
      setMessage(requestError instanceof Error ? requestError.message : "Failed to update status");
    } finally {
      setSaving(false);
    }
  }

  if (isCheckingSession) {
    return <main className="mx-auto max-w-4xl px-6 py-10 text-brand-navy/75">Checking your session...</main>;
  }

  if (loading) {
    return <main className="mx-auto max-w-4xl px-6 py-10 text-brand-navy/75">Loading lead...</main>;
  }

  if (!lead) {
    return (
      <main className="mx-auto max-w-4xl px-6 py-10">
        <p className="text-brand-burgundy">Lead not found.</p>
        <Link href="/leads" className="mt-3 inline-block text-brand-navy underline">
          Back to Leads
        </Link>
      </main>
    );
  }

  return (
    <main className="mx-auto max-w-4xl px-6 py-10">
      <header className="brand-card relative overflow-hidden p-6 md:p-7">
        <div className="pointer-events-none absolute -left-8 top-0 h-28 w-28 rounded-full bg-brand-gold/26 blur-2xl" />
        <div className="pointer-events-none absolute -right-8 bottom-0 h-24 w-24 rounded-full bg-brand-orange/24 blur-2xl" />

        <p className="relative text-xs tracking-[0.24em] text-brand-burgundy/80">LEAD DETAIL</p>
        <h1 className="relative mt-1 text-3xl font-semibold text-brand-burgundy" style={{ fontFamily: "var(--font-fraunces)" }}>
          Lead Context And Outreach
        </h1>
      </header>

      <section className="brand-card mt-6 p-6 md:p-7">
        <h2 className="text-xl font-semibold text-brand-navy">{lead.post.title}</h2>
        <p className="mt-2 text-sm text-brand-navy/75">r/{lead.post.subreddit}</p>

        <div className="mt-3 flex flex-wrap gap-2">
          <span className="brand-badge">Score: {lead.lead_score}</span>
          <span className="brand-badge">Status: {lead.status}</span>
        </div>

        <p className="mt-4 text-brand-navy/90">{lead.qualification_reason}</p>
        <p className="mt-2 text-sm text-brand-orange">Outreach idea: {lead.suggested_outreach}</p>
        {lead.post.body ? <p className="mt-3 text-sm text-brand-navy/75">{lead.post.body}</p> : null}

        <div className="mt-5 flex flex-wrap items-center gap-3">
          <label className="text-sm font-medium text-brand-burgundy">Status</label>
          <select
            value={status}
            onChange={(event) => setStatus(event.target.value as LeadStatus)}
            className="brand-select text-sm"
          >
            {STATUS_OPTIONS.map((item) => (
              <option key={item} value={item}>
                {item}
              </option>
            ))}
          </select>

          <button
            type="button"
            onClick={handleUpdateStatus}
            disabled={saving}
            className="brand-btn-primary px-4 py-2 text-sm disabled:opacity-50"
          >
            {saving ? "Saving..." : "Update Status"}
          </button>
        </div>

        <div className="mt-4 flex flex-wrap items-center gap-4">
          <a
            href={lead.post.url}
            target="_blank"
            rel="noreferrer"
            className="text-sm font-medium text-brand-burgundy underline decoration-brand-orange underline-offset-2"
          >
            Open Reddit Post
          </a>
          <Link href="/leads" className="text-sm font-medium text-brand-navy underline">
            Back to Inbox
          </Link>
        </div>

        {message ? <p className="mt-4 text-sm text-brand-navy/80">{message}</p> : null}
      </section>
    </main>
  );
}
