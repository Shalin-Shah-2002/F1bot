"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { usePathname, useRouter } from "next/navigation";
import { clearSession, getSession } from "@/lib/session";

const DASHBOARD_NAV_ITEMS = [
  { href: "/profile", label: "Profile" },
  { href: "/scan", label: "Scan" },
  { href: "/leads", label: "Leads" },
  { href: "/export", label: "Export" },
  { href: "/settings", label: "Settings" }
];

const LANDING_NAV_ITEMS = [
  { href: "#about", label: "About" },
  { href: "#features", label: "Features" },
  { href: "#workflow", label: "Workflow" },
  { href: "#faq", label: "FAQ" }
];

export function PhaseNav() {
  const pathname = usePathname();
  const router = useRouter();
  const [email, setEmail] = useState("Not signed in");
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const isLandingPage = pathname === "/";

  useEffect(() => {
    let isActive = true;

    async function hydrateNavSession() {
      const session = await getSession();
      if (!isActive) {
        return;
      }

      setEmail(session?.email || "Not signed in");
      setIsAuthenticated(Boolean(session));
    }

    hydrateNavSession();

    return () => {
      isActive = false;
    };
  }, [pathname]);

  async function handleLogout() {
    await clearSession();
    setEmail("Not signed in");
    setIsAuthenticated(false);
    router.replace("/login");
  }

  return (
    <header className="sticky top-0 z-20 border-b border-brand-navy/18 bg-brand-cream/82 backdrop-blur-xl">
      <div className="mx-auto flex max-w-6xl items-center justify-between gap-4 px-4 py-3 md:px-6">
        <Link href={isLandingPage ? "/" : "/scan"} className="flex flex-col leading-none">
          <span className="text-xl font-semibold tracking-wide text-brand-burgundy" style={{ fontFamily: "var(--font-fraunces)" }}>
            F1bot
          </span>
          <span className="mt-1 text-[10px] tracking-[0.2em] text-brand-navy/75">REDDIT LEAD STUDIO</span>
        </Link>

        <nav className="flex flex-wrap items-center gap-2 rounded-full bg-white/62 px-2 py-1 ring-1 ring-brand-navy/14">
          {isLandingPage
            ? LANDING_NAV_ITEMS.map((item) => (
                <a
                  key={item.href}
                  href={item.href}
                  className="rounded-full px-3 py-1.5 text-sm font-medium text-brand-navy transition-colors hover:bg-brand-gold/40"
                >
                  {item.label}
                </a>
              ))
            : DASHBOARD_NAV_ITEMS.map((item) => {
                const active = pathname === item.href || pathname.startsWith(`${item.href}/`);
                return (
                  <Link
                    key={item.href}
                    href={item.href}
                    className={`rounded-full px-3 py-1.5 text-sm font-medium transition-colors ${
                      active
                        ? "bg-gradient-to-r from-brand-orange to-brand-burgundy text-brand-cream shadow-md"
                        : "text-brand-navy hover:bg-brand-gold/40"
                    }`}
                  >
                    {item.label}
                  </Link>
                );
              })}
        </nav>

        <div className="flex items-center gap-3">
          {isLandingPage ? (
            isAuthenticated ? (
              <>
                <span className="hidden max-w-44 truncate text-sm text-brand-navy/75 md:inline">{email}</span>
                <Link
                  href="/scan"
                  className="rounded-md bg-brand-navy px-3 py-1.5 text-sm font-medium text-brand-cream transition-colors hover:bg-brand-burgundy"
                >
                  Open App
                </Link>
                <button
                  type="button"
                  onClick={() => {
                    void handleLogout();
                  }}
                  className="rounded-md bg-brand-burgundy px-3 py-1.5 text-sm font-medium text-brand-cream transition-colors hover:bg-brand-orange"
                >
                  Logout
                </button>
              </>
            ) : (
              <>
                <Link
                  href="/login"
                  className="rounded-md bg-brand-navy px-3 py-1.5 text-sm font-medium text-brand-cream transition-colors hover:bg-brand-burgundy"
                >
                  Login
                </Link>
                <Link
                  href="/register"
                  className="rounded-md bg-brand-burgundy px-3 py-1.5 text-sm font-medium text-brand-cream transition-colors hover:bg-brand-orange"
                >
                  Get Started
                </Link>
              </>
            )
          ) : (
            <>
              <span className="hidden max-w-44 truncate text-sm text-brand-navy/75 md:inline">{email}</span>
              <button
                type="button"
                onClick={() => {
                  void handleLogout();
                }}
                className="rounded-md bg-brand-burgundy px-3 py-1.5 text-sm font-medium text-brand-cream transition-colors hover:bg-brand-orange"
              >
                Logout
              </button>
            </>
          )}
        </div>
      </div>
    </header>
  );
}
