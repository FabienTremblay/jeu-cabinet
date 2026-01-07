// src/types/game.ts

// --------- Formes brutes issues de l'API moteur ---------

// Réponse brute de /parties/{id}/etat
export interface ReponseEtatBrute {
  partie_id: string;
  etat: Record<string, unknown>;
}

// Requête pour /parties/{id}/actions
export interface RequeteAction {
  acteur: string; // id du joueur
  type_action: string; // ex.: "ENGAGER_CARTE", "VOTE_PROGRAMME", etc.
  donnees?: Record<string, unknown>;
}

// --------- Modèle "vue" simplifié pour le front ---------

export interface IndicateursGlobaux {
  capital_collectif: number;
  capital_opposition: number;
}

export interface JoueurEtat {
  id: string;
  alias: string;
  capital_politique: number;

  attention_max?: number;
  attention_dispo?: number;
  poids_vote?: number;
  peut_voter?: boolean;

  // champs facultatifs qu'on pourra enrichir plus tard
  role?: string;
  pret?: boolean;
}

export interface Carte {
  id: string;
  nom: string;           // ex. "Investir dans les hôpitaux"
  type: string;          // ex. "mesure", "contre_coup"
  resume: string;        // résumé synthétique
  cout_attention?: number;
  cout_cp?: number;      // coût en capital politique, optionnel
  details?: string[];    // effets détaillés en puces
}



export interface CarteEngagee extends Carte {
  /** identifiant unique de l’entrée dans le programme (ex.: EP-1) */
  uid?: string;
  /** id du ministre qui a proposé / engagé la carte */
  auteur_id?: string;
  /** points d’attention effectivement engagés sur cette entrée */
  attention_engagee?: number;
}

export interface JournalEntree {
  id: string;
  tour?: number;
  message: string;
  category?: string;
  severity?: string;
}

export interface AttenteUiField {
  name: string;
  label: string;
  required: boolean;
  domain?: string;
}

export interface AttenteUiAction {
  op: string;
  label: string;
  fields?: AttenteUiField[];
}

export interface AttenteEtat {
  statut: string;
  type: string;
  joueurs: string[];
  recus: string[];

  titre?: string;
  description?: string;
  ui_actions?: AttenteUiAction[];
}

// carte telle qu’affichée dans la main / programme
export interface CarteDansMain {
  id: string;
  nom: string;
  type: string;
  resume: string;
  cout_attention?: number;
  cout_cp?: number;
  details?: string[];
}

// indicateurs globaux de la partie
export interface IndicateursPartie {
  capital_collectif: number;
  opposition: number;
  axes: Record<string, number>;
}

// pour un classement final
export interface EntreePalmares {
  joueur_id: string;
  alias: string;
  score_total: number;
  rang: number;
  // facultatif si tu veux détailler par axe
  scores_axes?: Record<string, number>;
}

// tu peux garder joueurs en any si tu ne veux pas tout typer maintenant
export type JoueursEtat = Record<string, JoueurEtat>;

export interface EvenementDef {
  id: string;
  nom: string;
  type: string; // "evenement" (ou autre selon skin)
  commandes?: any[];
}


// représentation de l’état de partie pour le front
export interface EtatPartieVue {
  partie_id: string;
  tour: number | null;
  phase: string;
  sous_phase: string;

  // fin de partie
  termine: boolean;
  raison_fin?: string | null;

  // palmarès final, si disponible
  palmares?: EntreePalmares[];

  joueurs: JoueursEtat;
  indicateurs: IndicateursPartie;

  // économie/budget (optionnel selon skin/mapping)
  eco?: {
    // breakdowns (si présents dans l'état)
    recettes?: Record<string, number>;
    depenses?: Record<string, number>;

    // agrégats
    dette?: number | null;
    taux_interet?: number | null; // ex.: 0.05 (5%)
  } | null;

  programme_cabinet: CarteEngagee[];

  programme_votes?: Record<string, number>;
  programme_verdict?: boolean | null;
  main_joueur_courant: CarteDansMain[];

  journal: JournalEntree[];
  attente: AttenteEtat | null;

  attention_disponible: number | null;
  attention_max: number | null;

  // définitions EVT-xxx (pour résumer les impacts dans l'UI)
  evenements?: EvenementDef[];

}


