import { useEffect, useState } from "react";
import { lireSituationJoueur, JournalRecentEntry } from "../api/uiEtatJoueur";

export function useJournalRecentPolling(
  joueurId: string | undefined,
  options?: { intervalMs?: number }
) {
  const [journalRecent, setJournalRecent] = useState<JournalRecentEntry[]>([]);
  const [erreur, setErreur] = useState<string | null>(null);

  const intervalMs = options?.intervalMs ?? 2000;

  useEffect(() => {
    if (!joueurId) {
      setJournalRecent([]);
      setErreur(null);
      return;
    }

    let cancelled = false;

    async function tick() {
      try {
        const sit = await lireSituationJoueur(joueurId);
        const jr = Array.isArray(sit?.journal_recent) ? sit.journal_recent : [];
        if (!cancelled) {
          setJournalRecent(jr);
          setErreur(null);
        }
      } catch (e: any) {
        if (!cancelled) setErreur(e?.message ?? "Erreur ui-etat-joueur");
      }
    }

    tick();
    const id = setInterval(tick, intervalMs);
    return () => {
      cancelled = true;
      clearInterval(id);
    };
  }, [joueurId, intervalMs]);

  return { journalRecent, erreur };
}

