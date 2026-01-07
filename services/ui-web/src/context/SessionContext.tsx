// src/context/SessionContext.tsx
import React, { createContext, useContext, useState } from "react";
import type { JoueurSession } from "../types/lobby";

interface SessionContextValue {
  joueur: JoueurSession | null;
  setJoueur: (j: JoueurSession | null) => void;
}

const SessionContext = createContext<SessionContextValue | undefined>(undefined);

const STORAGE_KEY = "cabinet.session.joueur";

export const SessionProvider: React.FC<React.PropsWithChildren> = ({ children }) => {
  // Initialisation depuis sessionStorage
  const [joueur, setJoueurState] = useState<JoueurSession | null>(() => {
    if (typeof window === "undefined") return null;
    try {
      const raw = window.sessionStorage.getItem(STORAGE_KEY);
      if (!raw) return null;
      return JSON.parse(raw) as JoueurSession;
    } catch {
      return null;
    }
  });

  const setJoueur = (j: JoueurSession | null) => {
    setJoueurState(j);
    if (typeof window === "undefined") return;

    try {
      if (j) {
        window.sessionStorage.setItem(STORAGE_KEY, JSON.stringify(j));
      } else {
        window.sessionStorage.removeItem(STORAGE_KEY);
      }
    } catch {
      // on ignore les erreurs de stockage
    }
  };

  const value: SessionContextValue = { joueur, setJoueur };

  return (
    <SessionContext.Provider value={value}>
      {children}
    </SessionContext.Provider>
  );
};

export function useSession(): SessionContextValue {
  const ctx = useContext(SessionContext);
  if (!ctx) {
    throw new Error("useSession doit être utilisé à l'intérieur de SessionProvider");
  }
  return ctx;
}

