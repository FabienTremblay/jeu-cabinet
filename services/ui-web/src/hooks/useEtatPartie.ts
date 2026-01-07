// src/hooks/useEtatPartie.ts

import { useEffect, useState } from "react";
import { lireEtatPartie } from "../api/moteurApi";
import { mapEtatToGameState } from "../utils/mapEtat";
import type { EtatPartieVue } from "../types/game";

export interface UseEtatPartieOptions {
  /** intervalle de polling en ms (par défaut 2000) */
  intervalMs?: number;
}

interface UseEtatPartieResult {
  etat: EtatPartieVue | null;
  loading: boolean;
  erreur: string | null;
  /** force un rechargement immédiat en plus du polling périodique */
  forceRefresh: () => void;
}

/**
 * Hook partagé pour charger l'état d'une partie depuis le moteur
 * + polling + mapping vers EtatPartieVue.
 *
 * Réutilisable par GamePage (web) et, plus tard, par une version mobile.
 */
export function useEtatPartie(
  partieId: string | undefined,
  joueurId: string | undefined,
  options?: UseEtatPartieOptions
): UseEtatPartieResult {
  const [etat, setEtat] = useState<EtatPartieVue | null>(null);
  const [loading, setLoading] = useState(true);
  const [erreur, setErreur] = useState<string | null>(null);
  const [refreshToken, setRefreshToken] = useState(0);

  const intervalMs = options?.intervalMs ?? 2000;

  useEffect(() => {
    // Si on n'a pas encore les identifiants nécessaires, on nettoie.
    if (!partieId || !joueurId) {
      setEtat(null);
      setLoading(false);
      setErreur(null);
      return;
    }

    let cancelled = false;

    async function chargerEtat() {
      try {
        const repEtat = await lireEtatPartie(partieId);
        const vue = mapEtatToGameState(repEtat, joueurId);
        if (!cancelled) {
          setEtat(vue);
          setErreur(null);
        }
      } catch (err) {
        if (!cancelled) {
          setErreur((err as Error).message);
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    }

    // Premier chargement immédiat
    chargerEtat();

    // Polling périodique
    const intervalId = setInterval(chargerEtat, intervalMs);

    return () => {
      cancelled = true;
      clearInterval(intervalId);
    };
  }, [partieId, joueurId, intervalMs, refreshToken]);

  const forceRefresh = () => {
    setRefreshToken((c) => c + 1);
  };

  return { etat, loading, erreur, forceRefresh };
}
