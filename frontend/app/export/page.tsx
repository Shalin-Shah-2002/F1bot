"use client";

import { useState } from "react";
import { downloadLeadsCsv, type LeadStatus } from "@/lib/api";
import { getSession } from "@/lib/session";

const STATUS_OPTIONS: Array<LeadStatus | "all"> = ["all", "new", "contacted", "qualified", "ignored"];

export default function ExportPage() {
  const [status, setStatus] = useState<LeadStatus | "all">("all");
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState<string | null>(null);

  async function handleExport() {
    const session = getSession();
    if (!session) {
      setMessage("Please login first.");
      return;
    }

    setLoading(true);
    setMessage(null);

    try {
      const blob = await downloadLeadsCsv(status === "all" ? undefined : status);
      const url = URL.createObjectURL(blob);
      const anchor = document.createElement("a");
      anchor.href = url;
      anchor.download = "leads.csv";
      anchor.click();
      URL.revokeObjectURL(url);
      setMessage("CSV downloaded.");
    } catch (requestError) {
      setMessage(requestError instanceof Error ? requestError.message : "Export failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="mx-auto max-w-4xl px-6 py-10">
      <h1 className="text-3xl font-semibold text-brand-burgundy">Export Leads</h1>
      <p className="mt-2 text-sm text-brand-navy/75">Download current lead data as CSV.</p>

      <section className="mt-6 rounded-xl bg-white/80 p-6 shadow-md ring-1 ring-brand-navy/20">
        <div className="flex flex-wrap items-center gap-3">
          <label className="text-sm font-medium text-brand-burgundy">Status filter</label>
          <select
            value={status}
            onChange={(event) => setStatus(event.target.value as LeadStatus | "all")}
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
            onClick={handleExport}
            disabled={loading}
            className="rounded-md bg-brand-orange px-4 py-2 text-sm font-medium text-brand-cream hover:bg-brand-burgundy disabled:opacity-50"
          >
            {loading ? "Exporting..." : "Download CSV"}
          </button>
        </div>

        {message ? <p className="mt-4 text-sm text-brand-navy/80">{message}</p> : null}
      </section>
    </main>
  );
}
