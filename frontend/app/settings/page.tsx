"use client";

import { useEffect, useState } from "react";
import { getHealth, getRuntimeSettings, type RuntimeHealthResponse, type RuntimeSettingsResponse } from "@/lib/api";
import { useSessionGuard } from "@/lib/use-session-guard";

export default function SettingsPage() {
  const { session, isCheckingSession } = useSessionGuard();
  const [settings, setSettings] = useState<RuntimeSettingsResponse | null>(null);
  const [health, setHealth] = useState<RuntimeHealthResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!session) {
      return;
    }

    async function loadSettings() {
      setError(null);
      try {
        const [settingsResponse, healthResponse] = await Promise.all([getRuntimeSettings(), getHealth()]);
        setSettings(settingsResponse);
        setHealth(healthResponse);
      } catch (requestError) {
        setError(requestError instanceof Error ? requestError.message : "Failed to load settings");
      }
    }

    loadSettings();
  }, [session]);

  if (isCheckingSession) {
    return <main className="mx-auto max-w-4xl px-6 py-10 text-brand-navy/75">Checking your session...</main>;
  }

  return (
    <main className="mx-auto max-w-5xl px-6 py-10">
      <header className="brand-card relative overflow-hidden p-6 md:p-7">
        <div className="pointer-events-none absolute -left-8 top-0 h-28 w-28 rounded-full bg-brand-gold/24 blur-2xl" />
        <div className="pointer-events-none absolute -right-8 bottom-0 h-28 w-28 rounded-full bg-brand-orange/24 blur-2xl" />

        <p className="relative text-xs tracking-[0.24em] text-brand-burgundy/80">SYSTEM SETTINGS</p>
        <h1 className="relative mt-1 text-3xl font-semibold text-brand-burgundy" style={{ fontFamily: "var(--font-fraunces)" }}>
          Runtime Configuration
        </h1>
        <p className="relative mt-2 text-sm text-brand-navy/75">Live backend status, feature flags, and scan limits from API endpoints.</p>
      </header>

      <section className="brand-card mt-6 p-6 md:p-7">
        {error ? <p className="text-sm text-brand-burgundy">{error}</p> : null}

        {!error && !settings ? <p className="text-sm text-brand-navy/70">Loading settings...</p> : null}

        {settings ? (
          <div className="grid gap-6 text-sm text-brand-navy">
            <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
              <div className="brand-stat">
                <p className="text-xs uppercase tracking-[0.14em] text-brand-burgundy/70">Environment</p>
                <p className="mt-1 text-base font-semibold text-brand-navy">{settings.environment}</p>
              </div>
              <div className="brand-stat">
                <p className="text-xs uppercase tracking-[0.14em] text-brand-burgundy/70">API Health</p>
                <p className="mt-1 text-base font-semibold text-brand-navy">{health?.status ?? "Unknown"}</p>
              </div>
              <div className="brand-stat">
                <p className="text-xs uppercase tracking-[0.14em] text-brand-burgundy/70">Supabase Auth</p>
                <p className="mt-1 text-base font-semibold text-brand-navy">
                  {settings.supabase_auth_enabled ? "Enabled" : "Local fallback"}
                </p>
              </div>
              <div className="brand-stat">
                <p className="text-xs uppercase tracking-[0.14em] text-brand-burgundy/70">Signed In</p>
                <p className="mt-1 truncate text-sm font-semibold text-brand-navy">{session?.email ?? "Unknown"}</p>
              </div>
            </div>

            <div className="grid gap-3 sm:grid-cols-3">
              <div className="brand-stat">
                <p className="text-xs uppercase tracking-[0.14em] text-brand-burgundy/70">Gemini</p>
                <p className="mt-1 text-base font-semibold text-brand-navy">
                  {settings.gemini_configured ? "Configured" : "Not configured"}
                </p>
              </div>
              <div className="brand-stat">
                <p className="text-xs uppercase tracking-[0.14em] text-brand-burgundy/70">Reddit</p>
                <p className="mt-1 text-base font-semibold text-brand-navy">
                  {settings.reddit_configured ? "Configured" : "Not configured"}
                </p>
              </div>
              <div className="brand-stat">
                <p className="text-xs uppercase tracking-[0.14em] text-brand-burgundy/70">Supabase</p>
                <p className="mt-1 text-base font-semibold text-brand-navy">
                  {settings.supabase_configured ? "Configured" : "Not configured"}
                </p>
              </div>
            </div>

            <div className="grid gap-3 sm:grid-cols-3">
              <div className="brand-stat">
                <p className="text-xs uppercase tracking-[0.14em] text-brand-burgundy/70">Sample Leads Fallback</p>
                <p className="mt-1 text-base font-semibold text-brand-navy">
                  {settings.sample_leads_fallback_enabled ? "Enabled" : "Disabled"}
                </p>
              </div>
            </div>

            <div className="grid gap-3 sm:grid-cols-3">
              <div className="brand-stat">
                <p className="text-xs uppercase tracking-[0.14em] text-brand-burgundy/70">Rate Limit / Minute</p>
                <p className="mt-1 text-lg font-semibold text-brand-navy">{settings.scan_rate_limit_per_minute}</p>
              </div>
              <div className="brand-stat">
                <p className="text-xs uppercase tracking-[0.14em] text-brand-burgundy/70">Window (seconds)</p>
                <p className="mt-1 text-lg font-semibold text-brand-navy">{settings.scan_rate_limit_window_seconds}</p>
              </div>
              <div className="brand-stat">
                <p className="text-xs uppercase tracking-[0.14em] text-brand-burgundy/70">Daily Quota</p>
                <p className="mt-1 text-lg font-semibold text-brand-navy">{settings.scan_daily_quota}</p>
              </div>
            </div>
          </div>
        ) : null}
      </section>
    </main>
  );
}
