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
    let isActive = true;

    async function hydrateSession() {
      const currentSession = await getSession();
      if (!isActive) {
        return;
      }

      if (!currentSession) {
        setSession(null);
        setIsCheckingSession(false);
        router.replace(redirectPath);
        return;
      }

      setSession(currentSession);
      setIsCheckingSession(false);
    }

    hydrateSession();

    return () => {
      isActive = false;
    };
  }, [redirectPath, router]);

  return { session, isCheckingSession };
}
