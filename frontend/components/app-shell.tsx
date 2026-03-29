"use client";

import { usePathname } from "next/navigation";
import { PhaseNav } from "@/components/phase-nav";

export function AppShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const showNav = pathname !== "/login" && pathname !== "/register";
  const showAmbientDecor = pathname === "/" || pathname === "/login" || pathname === "/register";

  return (
    <div className={`${showAmbientDecor ? "aurora-grid" : ""} relative min-h-screen`}>
      {showAmbientDecor ? <span className="float-orb orb-a" aria-hidden /> : null}
      {showAmbientDecor ? <span className="float-orb orb-b" aria-hidden /> : null}
      {showAmbientDecor ? (
        <span className="pointer-events-none absolute inset-x-0 top-0 h-20 bg-gradient-to-b from-white/35 to-transparent" aria-hidden />
      ) : null}
      {showNav ? <PhaseNav /> : null}
      <div className="relative page-enter">{children}</div>
    </div>
  );
}
