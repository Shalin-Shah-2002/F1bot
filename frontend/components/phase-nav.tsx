"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { clearSession, getSession } from "@/lib/session";

const NAV_ITEMS = [
  { href: "/profile", label: "Profile" },
  { href: "/scan", label: "Scan" },
  { href: "/leads", label: "Leads" },
  { href: "/export", label: "Export" },
  { href: "/settings", label: "Settings" }
];

export function PhaseNav() {
  const pathname = usePathname();
  const router = useRouter();
  const session = getSession();

  return (
    <header className="sticky top-0 z-20 border-b border-brand-navy/20 bg-brand-cream/85 backdrop-blur-md">
      <div className="mx-auto flex max-w-6xl items-center justify-between gap-4 px-4 py-3 md:px-6">
        <Link href="/scan" className="text-xl font-semibold tracking-wide text-brand-burgundy" style={{ fontFamily: "var(--font-fraunces)" }}>
          F1bot
        </Link>

        <nav className="flex flex-wrap items-center gap-2">
          {NAV_ITEMS.map((item) => {
            const active = pathname === item.href || pathname.startsWith(`${item.href}/`);
            return (
              <Link
                key={item.href}
                href={item.href}
                className={`rounded-full px-3 py-1.5 text-sm font-medium transition-colors ${
                  active
                    ? "bg-gradient-to-r from-brand-orange to-brand-burgundy text-brand-cream shadow-md"
                    : "bg-white/72 text-brand-navy ring-1 ring-brand-navy/20 hover:bg-brand-gold/35"
                }`}
              >
                {item.label}
              </Link>
            );
          })}
        </nav>

        <div className="flex items-center gap-3">
          <span className="hidden text-sm text-brand-navy/75 md:inline">{session?.email ?? "Not signed in"}</span>
          <button
            type="button"
            onClick={() => {
              clearSession();
              router.push("/login");
            }}
            className="rounded-md bg-brand-burgundy px-3 py-1.5 text-sm font-medium text-brand-cream hover:bg-brand-orange"
          >
            Logout
          </button>
        </div>
      </div>
    </header>
  );
}
