"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useParams, useRouter } from "next/navigation";
import { getLeadById, updateLeadStatus, type LeadRecord, type LeadStatus } from "@/lib/api";
import { getSession } from "@/lib/session";

const STATUS_OPTIONS: LeadStatus[] = ["new", "contacted", "qualified", "ignored"];

export default function LeadDetailPage() {
  const params = useParams<{ id: string }>();
  const router = useRouter();
  const session = getSession();
  const hasSession = Boolean(session?.accessToken);
  const [lead, setLead] = useState<LeadRecord | null>(null);
  const [status, setStatus] = useState<LeadStatus>("new");
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState<string | null>(null);

  useEffect(() => {
    if (!hasSession) {
      router.push("/login");
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
  }, [hasSession, params.id, router]);

  async function handleUpdateStatus() {
    if (!hasSession || !lead) {
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
      <h1 className="text-3xl font-semibold text-brand-burgundy">Lead Detail</h1>
      <section className="mt-6 rounded-xl bg-white/80 p-6 shadow-md ring-1 ring-brand-navy/20">
        <h2 className="text-xl font-semibold text-brand-navy">{lead.post.title}</h2>
        <p className="mt-2 text-sm text-brand-navy/75">r/{lead.post.subreddit}</p>

        <p className="mt-4 text-brand-navy/90">{lead.qualification_reason}</p>
        <p className="mt-2 text-sm text-brand-orange">Outreach idea: {lead.suggested_outreach}</p>

        <div className="mt-5 flex flex-wrap items-center gap-3">
          <label className="text-sm font-medium text-brand-burgundy">Status</label>
          <select
            value={status}
            onChange={(event) => setStatus(event.target.value as LeadStatus)}
            className="rounded-md border border-brand-navy/25 bg-white px-3 py-2 text-sm text-brand-navy focus:border-brand-gold focus:outline-none"
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
            className="rounded-md bg-brand-orange px-4 py-2 text-sm font-medium text-brand-cream hover:bg-brand-burgundy disabled:opacity-50"
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
