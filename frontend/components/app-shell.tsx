"use client";

import { usePathname } from "next/navigation";
import { PhaseNav } from "@/components/phase-nav";

export function AppShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const showNav = pathname !== "/login" && pathname !== "/register";

  return (
    <div className="aurora-grid relative min-h-screen">
      <span className="float-orb orb-a" aria-hidden />
      <span className="float-orb orb-b" aria-hidden />
      {showNav ? <PhaseNav /> : null}
      <div>{children}</div>
    </div>
  );
}
