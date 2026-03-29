"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { getSession, type SessionState } from "@/lib/session";

export interface SessionGuardState {
  session: SessionState | null;
  isCheckingSession: boolean;
}

export function useSessionGuard(redirectPath = "/login"): SessionGuardState {
  const router = useRouter();
  const [session, setSession] = useState<SessionState | null>(null);
  const [isCheckingSession, setIsCheckingSession] = useState(true);

  useEffect(() => {
    const currentSession = getSession();
    if (!currentSession) {
      setSession(null);
      setIsCheckingSession(false);
      router.replace(redirectPath);
      return;
    }

    setSession(currentSession);
    setIsCheckingSession(false);
  }, [redirectPath, router]);

  return { session, isCheckingSession };
}
