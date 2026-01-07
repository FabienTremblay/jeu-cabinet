import { useEffect, useState } from "react";
import { lireSituationJoueur } from "../api/uiEtatJoueur";
import type { SituationUI } from "../types/uiEtat";

interface OptionsPolling {
  intervalMs?: number;
}

export function useSituationPolling(joueurId: string | null, opts: OptionsPolling = {}) {
  const intervalMs = opts.intervalMs ?? 2000;

  const [situation, setSituation] = useState<SituationUI | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    if (!joueurId) return;

    let cancelled = false;

    async function poll() {
      try {
        setLoading(true);
        const rep = await lireSituationJoueur(joueurId);
        if (!cancelled) setSituation(rep);
      } catch (err: any) {
        if (!cancelled) setError(err);
      } finally {
        if (!cancelled) setLoading(false);
      }
    }

    poll();
    const interval = setInterval(poll, intervalMs);
    return () => {
      cancelled = true;
      clearInterval(interval);
    };
  }, [joueurId, intervalMs]);

  // Données dérivées utiles au front
  const marqueurs = situation?.marqueurs ?? {};
  const ancrage = situation?.ancrage;

  return {
    situation,
    marqueurs,
    ancrage,
    loading,
    error,
  };
}

