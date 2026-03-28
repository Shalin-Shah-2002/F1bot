"use client";

import Link from "next/link";
import { FormEvent, useState } from "react";
import { useRouter } from "next/navigation";
import { login } from "@/lib/api";
import { saveSession } from "@/lib/session";

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState("founder@f1bot.ai");
  const [password, setPassword] = useState("password123");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const response = await login({ email, password });
      saveSession({
        userId: response.user_id,
        email: response.email,
        accessToken: response.access_token
      });
      router.push("/profile");
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : "Login failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="mx-auto flex min-h-screen w-full max-w-5xl items-center px-6 py-12">
      <section className="grid w-full overflow-hidden rounded-3xl shadow-2xl ring-1 ring-brand-navy/20 md:grid-cols-[1.1fr_0.9fr]">
        <div className="relative bg-brand-navy p-8 text-brand-cream md:p-10">
          <div className="absolute -left-8 -top-10 h-40 w-40 rounded-full bg-brand-gold/35 blur-2xl" />
          <div className="absolute -bottom-12 right-0 h-44 w-44 rounded-full bg-brand-orange/35 blur-2xl" />

          <p className="relative text-sm tracking-[0.28em] text-brand-gold">F1BOT</p>
          <h1 className="relative mt-4 text-4xl font-semibold leading-tight md:text-5xl" style={{ fontFamily: "var(--font-fraunces)" }}>
            Turn Conversations Into Customers
          </h1>
          <p className="relative mt-5 max-w-md text-sm text-brand-cream/85 md:text-base">
            Scan high-intent Reddit threads, prioritize with AI, and move faster with a clean outreach workflow.
          </p>
        </div>

        <div className="glass-panel rounded-none p-8 md:p-10">
          <h2 className="text-3xl font-semibold text-brand-burgundy" style={{ fontFamily: "var(--font-fraunces)" }}>
            Welcome Back
          </h2>
          <p className="mt-2 text-sm text-brand-navy/75">Sign in to continue your pipeline.</p>

          <form className="mt-6 grid gap-4" onSubmit={handleSubmit}>
            <label className="grid gap-2">
              <span className="text-sm font-medium text-brand-burgundy">Email</span>
              <input
                type="email"
                value={email}
                onChange={(event) => setEmail(event.target.value)}
                className="brand-input"
                required
              />
            </label>

            <label className="grid gap-2">
              <span className="text-sm font-medium text-brand-burgundy">Password</span>
              <input
                type="password"
                value={password}
                onChange={(event) => setPassword(event.target.value)}
                className="brand-input"
                required
              />
            </label>

            <button type="submit" disabled={loading} className="brand-btn-primary mt-2 px-4 py-2.5 disabled:opacity-50">
              {loading ? "Signing in..." : "Login"}
            </button>

            {error ? <p className="text-sm text-brand-burgundy">{error}</p> : null}

            <p className="pt-1 text-sm text-brand-navy/80">
              New here?{" "}
              <Link href="/register" className="font-semibold text-brand-burgundy underline decoration-brand-orange underline-offset-2">
                Create an account
              </Link>
            </p>
          </form>
        </div>
      </section>
    </main>
  );
}
