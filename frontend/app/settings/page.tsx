"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { getRuntimeSettings, type RuntimeSettingsResponse } from "@/lib/api";
import { getSession } from "@/lib/session";

export default function SettingsPage() {
  const router = useRouter();
  const [settings, setSettings] = useState<RuntimeSettingsResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const session = getSession();
    if (!session) {
      router.push("/login");
      return;
    }

    async function loadSettings() {
      setError(null);
      try {
        const response = await getRuntimeSettings();
        setSettings(response);
      } catch (requestError) {
        setError(requestError instanceof Error ? requestError.message : "Failed to load settings");
      }
    }

    loadSettings();
  }, [router]);

  return (
    <main className="mx-auto max-w-4xl px-6 py-10">
      <h1 className="text-3xl font-semibold text-brand-burgundy">Settings</h1>
      <p className="mt-2 text-sm text-brand-navy/75">Environment and service health for MVP setup.</p>

      <section className="mt-6 rounded-xl bg-white/80 p-6 shadow-md ring-1 ring-brand-navy/20">
        {error ? <p className="text-sm text-brand-burgundy">{error}</p> : null}

        {!error && !settings ? <p className="text-sm text-brand-navy/70">Loading settings...</p> : null}

        {settings ? (
          <div className="grid gap-3 text-sm text-brand-navy">
            <p>
              <span className="font-semibold text-brand-burgundy">Environment:</span> {settings.environment}
            </p>
            <p>
              <span className="font-semibold text-brand-burgundy">Gemini:</span>{" "}
              {settings.gemini_configured ? "Configured" : "Not configured"}
            </p>
            <p>
              <span className="font-semibold text-brand-burgundy">Reddit:</span>{" "}
              {settings.reddit_configured ? "Configured" : "Not configured"}
            </p>
            <p>
              <span className="font-semibold text-brand-burgundy">Supabase:</span>{" "}
              {settings.supabase_configured ? "Configured" : "Not configured"}
            </p>
          </div>
        ) : null}
      </section>
    </main>
  );
}
