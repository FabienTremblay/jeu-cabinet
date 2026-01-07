// src/types/uiEtat.ts

export type AncrageType = "lobby" | "table" | "partie" | null;

export interface AncrageUI {
  type: AncrageType;
  table_id: string | null;
  partie_id: string | null;
}

export interface EtatPartieUI {
  phase: string | null;
  sous_phase: string | null;
  tour: number | null;
}

export interface ActionDisponible {
  code: string;
  label?: string;
  payload?: Record<string, unknown>;
  requires_confirmation?: boolean;

  // champs additionnels possibles (tolérance à l'évolution)
  [key: string]: unknown;
}

export interface JournalEntryUI {
  event_id?: string;
  occurred_at?: string;
  category?: string;
  severity?: string;
  message?: string;

  raw?: Record<string, unknown>;

  // champs additionnels
  [key: string]: unknown;
}

export interface SituationUI {
  version: number;
  joueur_id: string;
  ancrage: AncrageUI;
  etat_partie: EtatPartieUI | null;
  actions_disponibles: ActionDisponible[];
  journal_recent: JournalEntryUI[];

  // champs additionnels ignorés par l'UI
  [key: string]: unknown;

  marqueurs?: {
    en_lobby?: boolean;
    en_table?: boolean;
    en_partie?: boolean;

    // ui-état demande un retour au lobby (fin de partie ou table fermée)
    retour_lobby?: boolean;

    // marqueurs facultatifs
    table_en_jeu?: boolean;
    partie_terminee?: boolean;
  };
}
