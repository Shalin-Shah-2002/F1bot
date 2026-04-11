"use client";

import { FormEvent, useEffect, useMemo, useState } from "react";
import { useRouter } from "next/navigation";
import { getProfile, saveProfile } from "@/lib/api";
import { useSessionGuard } from "@/lib/use-session-guard";

const DEFAULT_DESCRIPTION = "CalPal is a calorie tracker that helps people lose weight consistently with simple meal logging, macro guidance, and accountability nudges.";
const DEFAULT_KEYWORDS = "calorie tracker,calorie counting app,macro tracking,lose weight app,weight loss plateau,fitness app recommendation";
const DEFAULT_SUBREDDITS = "loseit,CICO,nutrition,weightlossadvice,Fitness,MealPrepSunday,PCOSloseit";

export default function ProfilePage() {
  const router = useRouter();
  const { session, isCheckingSession } = useSessionGuard();
  const [businessDescription, setBusinessDescription] = useState(DEFAULT_DESCRIPTION);
  const [keywords, setKeywords] = useState(DEFAULT_KEYWORDS);
  const [subreddits, setSubreddits] = useState(DEFAULT_SUBREDDITS);
  const [loading, setLoading] = useState(false);
  const [status, setStatus] = useState<string | null>(null);

  useEffect(() => {
    if (!session?.accessToken) {
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
  }, [session?.accessToken]);

  const canSave = useMemo(() => businessDescription.trim().length >= 10 && !loading, [businessDescription, loading]);

  const keywordCount = useMemo(
    () =>
      keywords
        .split(",")
        .map((item) => item.trim())
        .filter(Boolean).length,
    [keywords]
  );

  const subredditCount = useMemo(
    () =>
      subreddits
        .split(",")
        .map((item) => item.trim())
        .filter(Boolean).length,
    [subreddits]
  );

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!session?.accessToken) {
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

  if (isCheckingSession) {
    return <main className="mx-auto max-w-4xl px-6 py-10 text-brand-navy/75">Checking your session...</main>;
  }

  return (
    <main className="mx-auto max-w-5xl px-6 py-10">
      <header className="brand-card relative overflow-hidden p-6 md:p-8">
        <div className="pointer-events-none absolute -left-8 top-0 h-28 w-28 rounded-full bg-brand-gold/30 blur-2xl" />
        <div className="pointer-events-none absolute bottom-0 right-0 h-32 w-32 rounded-full bg-brand-orange/26 blur-2xl" />

        <p className="relative text-xs tracking-[0.24em] text-brand-burgundy/80">PROFILE SETUP</p>
        <h1 className="relative mt-2 text-3xl font-semibold text-brand-burgundy md:text-4xl" style={{ fontFamily: "var(--font-fraunces)" }}>
          Describe Your Buyer Context
        </h1>
        <p className="relative mt-3 max-w-2xl text-sm text-brand-navy/80 md:text-base">
          This profile is sent to the backend scanner so Reddit posts can be scored against your ideal customer profile.
        </p>

        <div className="relative mt-5 grid gap-3 sm:grid-cols-3">
          <div className="brand-stat">
            <p className="text-xs uppercase tracking-[0.14em] text-brand-burgundy/70">Keywords</p>
            <p className="mt-1 text-lg font-semibold text-brand-navy">{keywordCount}</p>
          </div>
          <div className="brand-stat">
            <p className="text-xs uppercase tracking-[0.14em] text-brand-burgundy/70">Subreddits</p>
            <p className="mt-1 text-lg font-semibold text-brand-navy">{subredditCount}</p>
          </div>
          <div className="brand-stat">
            <p className="text-xs uppercase tracking-[0.14em] text-brand-burgundy/70">Profile Owner</p>
            <p className="mt-1 truncate text-sm font-semibold text-brand-navy">{session?.email ?? "Unknown"}</p>
          </div>
        </div>
      </header>

      <form className="brand-card mt-6 grid gap-5 p-6 md:p-7" onSubmit={handleSubmit}>
        <label className="grid gap-2">
          <span className="text-sm font-medium text-brand-burgundy">Business Description</span>
          <textarea
            value={businessDescription}
            onChange={(event) => setBusinessDescription(event.target.value)}
            className="brand-input h-36 resize-y"
            required
          />
        </label>

        <div className="grid gap-4 md:grid-cols-2">
          <label className="grid gap-2">
            <span className="text-sm font-medium text-brand-burgundy">Keywords</span>
            <input
              value={keywords}
              onChange={(event) => setKeywords(event.target.value)}
              className="brand-input"
              placeholder="need help, looking for, recommendation"
            />
          </label>

          <label className="grid gap-2">
            <span className="text-sm font-medium text-brand-burgundy">Subreddits</span>
            <input
              value={subreddits}
              onChange={(event) => setSubreddits(event.target.value)}
              className="brand-input"
              placeholder="entrepreneur, smallbusiness, marketing"
            />
          </label>
        </div>

        <div className="flex flex-wrap items-center gap-3 pt-1">
          <button
            type="submit"
            disabled={!canSave}
            className="brand-btn-primary px-4 py-2.5 text-sm disabled:cursor-not-allowed disabled:opacity-50"
          >
            {loading ? "Saving..." : "Save Profile"}
          </button>
          <button
            type="button"
            onClick={() => router.push("/scan")}
            className="brand-btn-secondary px-4 py-2.5 text-sm"
          >
            Continue To Scan
          </button>
          {status ? (
            <span className={`text-sm ${status.toLowerCase().includes("failed") ? "text-brand-burgundy" : "text-brand-navy/80"}`}>
              {status}
            </span>
          ) : null}
        </div>
      </form>
    </main>
  );
}
