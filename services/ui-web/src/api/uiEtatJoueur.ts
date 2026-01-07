// src/api/uiEtatJoueur.ts
import { makeGetJson } from "./apiClient";

const getUiEtatJson = makeGetJson(
  "VITE_UI_ETAT_BASE_URL",
  "http://ui-etat.cabinet.localhost"
);

export type TypeAncrage = "lobby" | "table" | "partie";

export type Audience =
  | { scope: "joueur"; joueur_id: string }
  | { scope: "all" }
  | null;

export type JournalRecentEntry = {
  event_id: string;
  occurred_at: string;
  category?: string | null;
  severity?: string | null;
  message: string;
  code?: string | null;
  meta?: Record<string, any> | null;
  audience?: Audience;
};

export interface SituationJoueur {
  version: number;
  joueur_id: string;
  ancrage: {
    type: TypeAncrage;
    table_id?: string | null;
    partie_id?: string | null;
  };
  etat_partie: {
    phase?: string | null;
    sous_phase?: string | null;
    tour?: number | null;
  };
  actions_disponibles: Array<{
    code: string;
    label: string;
    payload: Record<string, unknown>;
    requires_confirmation: boolean;
  }>;
  journal_recent: JournalRecentEntry[];
}

export async function lireSituationJoueur(
  joueurId: string
): Promise<SituationJoueur> {
  return getUiEtatJson<SituationJoueur>(`/ui/joueurs/${joueurId}/situation`);
}

