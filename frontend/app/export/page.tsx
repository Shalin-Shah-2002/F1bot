"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { downloadLeadsCsv, type LeadStatus } from "@/lib/api";
import { useSessionGuard } from "@/lib/use-session-guard";

const STATUS_OPTIONS: Array<LeadStatus | "all"> = ["all", "new", "contacted", "qualified", "ignored"];

export default function ExportPage() {
  const router = useRouter();
  const { session, isCheckingSession } = useSessionGuard();
  const [status, setStatus] = useState<LeadStatus | "all">("all");
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState<string | null>(null);

  useEffect(() => {
    if (!session?.accessToken) {
      return;
    }

    setMessage(null);
  }, [session?.accessToken]);

  async function handleExport() {
    if (!session?.accessToken) {
      router.replace("/login");
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

  if (isCheckingSession) {
    return <main className="mx-auto max-w-4xl px-6 py-10 text-brand-navy/75">Checking your session...</main>;
  }

  return (
    <main className="mx-auto max-w-4xl px-6 py-10">
      <header className="brand-card relative overflow-hidden p-6 md:p-7">
        <div className="pointer-events-none absolute -right-8 -top-2 h-28 w-28 rounded-full bg-brand-gold/28 blur-2xl" />
        <div className="pointer-events-none absolute -left-8 bottom-0 h-24 w-24 rounded-full bg-brand-orange/24 blur-2xl" />

        <p className="relative text-xs tracking-[0.24em] text-brand-burgundy/80">EXPORT</p>
        <h1 className="relative mt-1 text-3xl font-semibold text-brand-burgundy" style={{ fontFamily: "var(--font-fraunces)" }}>
          Export Leads As CSV
        </h1>
        <p className="relative mt-2 text-sm text-brand-navy/75">Download your pipeline data with status filtering for reporting and outreach.</p>
      </header>

      <section className="brand-card mt-6 p-6 md:p-7">
        <div className="flex flex-wrap items-center gap-3">
          <label className="text-sm font-medium text-brand-burgundy">Status filter</label>
          <select
            value={status}
            onChange={(event) => setStatus(event.target.value as LeadStatus | "all")}
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
            onClick={handleExport}
            disabled={loading}
            className="brand-btn-primary px-4 py-2.5 text-sm disabled:opacity-50"
          >
            {loading ? "Exporting..." : "Download CSV"}
          </button>
        </div>

        {message ? <p className="mt-4 text-sm text-brand-navy/80">{message}</p> : null}
      </section>
    </main>
  );
}
