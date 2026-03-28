"use client";

import { FormEvent, useEffect, useMemo, useState } from "react";
import { useRouter } from "next/navigation";
import { getProfile, saveProfile } from "@/lib/api";
import { getSession } from "@/lib/session";

const DEFAULT_DESCRIPTION = "We help founders identify high-intent Reddit conversations and convert them to sales opportunities.";
const DEFAULT_KEYWORDS = "need help,looking for,recommend,best tool";
const DEFAULT_SUBREDDITS = "entrepreneur,smallbusiness,marketing,sales";

export default function ProfilePage() {
  const router = useRouter();
  const [businessDescription, setBusinessDescription] = useState(DEFAULT_DESCRIPTION);
  const [keywords, setKeywords] = useState(DEFAULT_KEYWORDS);
  const [subreddits, setSubreddits] = useState(DEFAULT_SUBREDDITS);
  const [loading, setLoading] = useState(false);
  const [status, setStatus] = useState<string | null>(null);
  const session = getSession();
  const hasSession = Boolean(session?.accessToken);

  useEffect(() => {
    if (!hasSession) {
      router.push("/login");
      return;
    }

    async function loadProfile() {
      try {
        const profile = await getProfile();
        setBusinessDescription(profile.business_description);
        setKeywords(profile.keywords.join(","));
        setSubreddits(profile.subreddits.join(","));
      } catch {
        // Profile is optional at first login.
      }
    }

    loadProfile();
  }, [hasSession, router]);

  const canSave = useMemo(() => businessDescription.trim().length >= 10 && !loading, [businessDescription, loading]);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!hasSession) {
      return;
    }

    setLoading(true);
    setStatus(null);

    try {
      await saveProfile({
        business_description: businessDescription,
        keywords: keywords.split(",").map((item) => item.trim()).filter(Boolean),
        subreddits: subreddits.split(",").map((item) => item.trim()).filter(Boolean)
      });
      setStatus("Profile saved.");
    } catch (requestError) {
      setStatus(requestError instanceof Error ? requestError.message : "Failed to save profile");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="mx-auto max-w-4xl px-6 py-10">
      <h1 className="text-3xl font-semibold text-brand-burgundy">Business Profile</h1>
      <p className="mt-2 text-brand-navy/75">This context is used to qualify Reddit posts.</p>

      <form className="mt-6 grid gap-4 rounded-xl bg-white/80 p-6 shadow-md ring-1 ring-brand-navy/20" onSubmit={handleSubmit}>
        <label className="grid gap-2">
          <span className="text-sm font-medium text-brand-burgundy">Business Description</span>
          <textarea
            value={businessDescription}
            onChange={(event) => setBusinessDescription(event.target.value)}
            className="h-32 rounded-md border border-brand-navy/30 bg-white p-3 focus:border-brand-gold focus:outline-none"
            required
          />
        </label>

        <div className="grid gap-4 md:grid-cols-2">
          <label className="grid gap-2">
            <span className="text-sm font-medium text-brand-burgundy">Keywords</span>
            <input
              value={keywords}
              onChange={(event) => setKeywords(event.target.value)}
              className="rounded-md border border-brand-navy/30 bg-white p-3 focus:border-brand-gold focus:outline-none"
            />
          </label>

          <label className="grid gap-2">
            <span className="text-sm font-medium text-brand-burgundy">Subreddits</span>
            <input
              value={subreddits}
              onChange={(event) => setSubreddits(event.target.value)}
              className="rounded-md border border-brand-navy/30 bg-white p-3 focus:border-brand-gold focus:outline-none"
            />
          </label>
        </div>

        <div className="flex flex-wrap items-center gap-3">
          <button
            type="submit"
            disabled={!canSave}
            className="rounded-md bg-brand-orange px-4 py-2 font-medium text-brand-cream transition-colors hover:bg-brand-burgundy disabled:opacity-50"
          >
            {loading ? "Saving..." : "Save Profile"}
          </button>
          <button
            type="button"
            onClick={() => router.push("/scan")}
            className="rounded-md bg-brand-navy px-4 py-2 font-medium text-brand-cream hover:bg-brand-burgundy"
          >
            Continue To Scan
          </button>
          {status ? <span className="text-sm text-brand-navy/80">{status}</span> : null}
        </div>
      </form>
    </main>
  );
}
