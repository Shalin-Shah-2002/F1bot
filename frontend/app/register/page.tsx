"use client";

import Link from "next/link";
import { FormEvent, useState } from "react";
import { useRouter } from "next/navigation";
import { register } from "@/lib/api";
import { saveSession } from "@/lib/session";

export default function RegisterPage() {
  const router = useRouter();
  const [fullName, setFullName] = useState("Founder");
  const [email, setEmail] = useState("founder@f1bot.ai");
  const [password, setPassword] = useState("password123");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const response = await register({
        full_name: fullName,
        email,
        password
      });

      if (!response.access_token?.trim()) {
        setError("Registration succeeded, but no login token was returned. Confirm your email if required, then login.");
        return;
      }

      saveSession({
        userId: response.user_id,
        email: response.email,
        accessToken: response.access_token
      });

      router.push("/profile");
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : "Registration failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="mx-auto flex min-h-screen w-full max-w-5xl items-center px-6 py-12">
      <section className="grid w-full overflow-hidden rounded-3xl shadow-2xl ring-1 ring-brand-navy/20 md:grid-cols-[0.95fr_1.05fr]">
        <div className="relative bg-brand-burgundy p-8 text-brand-cream md:p-10">
          <div className="absolute -left-12 top-4 h-44 w-44 rounded-full bg-brand-gold/35 blur-2xl" />
          <div className="absolute bottom-0 right-0 h-40 w-40 rounded-full bg-brand-orange/35 blur-2xl" />

          <p className="relative text-sm tracking-[0.28em] text-brand-gold">GET STARTED</p>
          <h1 className="relative mt-4 text-4xl font-semibold leading-tight md:text-5xl" style={{ fontFamily: "var(--font-fraunces)" }}>
            Build Your Lead Engine
          </h1>
          <p className="relative mt-5 max-w-md text-sm text-brand-cream/85 md:text-base">
            Create your account and start scanning relevant Reddit opportunities in minutes.
          </p>
        </div>

        <div className="glass-panel rounded-none p-8 md:p-10">
          <h2 className="text-3xl font-semibold text-brand-burgundy" style={{ fontFamily: "var(--font-fraunces)" }}>
            Create Account
          </h2>
          <p className="mt-2 text-sm text-brand-navy/75">Set up your workspace and begin qualifying leads.</p>

          <form className="mt-6 grid gap-4" onSubmit={handleSubmit}>
            <label className="grid gap-2">
              <span className="text-sm font-medium text-brand-burgundy">Full Name</span>
              <input
                value={fullName}
                onChange={(event) => setFullName(event.target.value)}
                className="brand-input"
                required
              />
            </label>

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
                minLength={6}
                required
              />
            </label>

            <button type="submit" disabled={loading} className="brand-btn-primary mt-2 px-4 py-2.5 disabled:opacity-50">
              {loading ? "Creating account..." : "Register"}
            </button>

            {error ? <p className="text-sm text-brand-burgundy">{error}</p> : null}

            <p className="pt-1 text-sm text-brand-navy/80">
              Already have an account?{" "}
              <Link href="/login" className="font-semibold text-brand-burgundy underline decoration-brand-orange underline-offset-2">
                Login
              </Link>
            </p>
          </form>
        </div>
      </section>
    </main>
  );
}
