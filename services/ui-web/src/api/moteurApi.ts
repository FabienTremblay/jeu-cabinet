// src/api/moteurApi.ts

import { makeGetJson, makePostJson } from "./apiClient";
import type { RequeteAction, ReponseEtatBrute } from "../types/game";
import { JouerCarteParams } from "../components/game/HandView"; 

// Base URL configurable via Vite, même pattern que lobby / ui-etat
const getJson = makeGetJson(
  "VITE_MOTEUR_BASE_URL",
  "http://moteur-api.localhost"
);
const postJson = makePostJson(
  "VITE_MOTEUR_BASE_URL",
  "http://moteur-api.localhost"
);

/**
 * Contexte optionnel pour enrichir une action avant envoi au moteur.
 *
 *  - acteurId      : id du joueur côté interface (souvent identique à action.acteur)
 *  - attenteType   : type d'attente courant (ex. "ENGAGER_CARTE")
 *  - selectedCardId: carte choisie dans la main du joueur
 *  - cibleId       : joueur cible quand une action demande explicitement un autre joueur
 *  - effort        : valeur numérique pour les champs de type "_effort" (non utilisé pour l'instant)
 */
export interface SoumettreActionContext {
  acteurId?: string;
  attenteType?: string | null;
  selectedCardId?: string | null;
  cibleId?: string | null;
  effort?: number;
}

/**
 * Lecture de l'état d'une partie.
 */
export async function lireEtatPartie(partieId: string): Promise<ReponseEtatBrute> {
  return getJson(`/parties/${partieId}/etat`);
}

// ============================================================================
// Résolution des jokers UI : _auto, _cible, _effort
// ============================================================================

export interface SoumettreActionContext {
  acteurId: string;
  attenteType?: string | null;
  selectedCardId?: string | null;

  // Pour les cartes avancées demandant intervention de l’utilisateur :
  cibleId?: string | null;
  effort?: number | null;
}

/**
 * Remplace tous les jokers avant l’envoi au moteur.
 * Aucune commande ne doit contenir "_auto", "_cible" ou "_effort".
 */
function resoudreJokers(
  donnees: Record<string, any> | undefined,
  ctx: SoumettreActionContext
): Record<string, any> {
  const base = { ...(donnees ?? {}) };

  // ------------------------------------------------------------
  // 1) joueur_id : résoudre _auto et _cible
  // ------------------------------------------------------------
  if (base["joueur_id"] === "_auto") {
    base["joueur_id"] = ctx.acteurId;
  }

  if (base["joueur_id"] === "_cible" && ctx.cibleId) {
    base["joueur_id"] = ctx.cibleId;
  }

  // Fallback : si joueur_id est absent → acteur
  if (!base["joueur_id"]) {
    base["joueur_id"] = ctx.acteurId;
  }

  // ------------------------------------------------------------
  // 2) type d’attente (utile dans attente.joueur_recu)
  // ------------------------------------------------------------
  if (!base["type"] && ctx.attenteType) {
    base["type"] = ctx.attenteType;
  }

  // ------------------------------------------------------------
  // 3) carte_id
  // ------------------------------------------------------------
  if (!base["carte_id"] && ctx.selectedCardId) {
    base["carte_id"] = ctx.selectedCardId;
  }

  // ------------------------------------------------------------
  // 4) effort
  // ------------------------------------------------------------
  if (base["delta"] === "_effort" && typeof ctx.effort === "number") {
    base["delta"] = ctx.effort;
  }

  return base;
}

/**
 * Envoie une action au moteur en complétant systématiquement les données
 * minimales attendues (joueur_id, type d'attente, carte sélectionnée, etc.).
 *
 * L'objectif est d'éviter les "actions incomplètes" qui manquent par exemple
 * le joueur_id ou la carte_id alors que la procédure UI les attend.
 */
export async function soumettreAction(
  partieId: string,
  action: RequeteAction,
  ctx?: SoumettreActionContext
) {
  const acteurId = action.acteur || ctx?.acteurId;

  // On clone les données d'origine pour éviter de muter l'objet passé en paramètre.
  const donnees: Record<string, unknown> = {
    ...(action.donnees ?? {}),
  };

  // ---------------------------------------------------------------------------
  // 1) joueur_id : toujours renseigné si possible
  //    - null/undefined      -> acteurId (joueur de l'interface)
  //    - "_auto"             -> acteurId
  //    - "_cible"            -> ctx.cibleId (si fourni)
  // ---------------------------------------------------------------------------
  if (donnees.joueur_id == null && acteurId) {
    donnees.joueur_id = acteurId;
  }
  if (donnees.joueur_id === "_auto" && acteurId) {
    donnees.joueur_id = acteurId;
  }
  if (donnees.joueur_id === "_cible" && ctx?.cibleId) {
    donnees.joueur_id = ctx.cibleId;
  }

  // Fallback : si on n'a toujours rien, on essaie encore de sauver avec l'acteur
  if (!donnees.joueur_id && acteurId) {
    donnees.joueur_id = acteurId;
  }

  // ---------------------------------------------------------------------------
  // 2) type d'attente (ENGAGER_CARTE, VOTE_PROGRAMME, ...)
  // ---------------------------------------------------------------------------
  if (ctx?.attenteType && donnees.type == null) {
    donnees.type = ctx.attenteType;
  }

  // ---------------------------------------------------------------------------
  // 3) carte sélectionnée pour les domaines "carte_main"
  // ---------------------------------------------------------------------------
  if (ctx?.selectedCardId && donnees.carte_id == null) {
    donnees.carte_id = ctx.selectedCardId;
  }

  // ---------------------------------------------------------------------------
  // 4) joker "_effort" : si le contexte fournit une valeur numérique, on l'injecte
  // ---------------------------------------------------------------------------
  if (donnees.delta === "_effort" && typeof ctx?.effort === "number") {
    donnees.delta = ctx.effort;
  }

  const finalAction: RequeteAction = {
    acteur: acteurId ?? action.acteur,
    type_action: action.type_action,
    donnees,
  };

  return postJson(`/parties/${partieId}/actions`, finalAction);
}

// src/api/moteurApi.ts

// … le reste du fichier inchangé …

/**
 * Utiliser immédiatement une carte de la main du joueur.
 *
 * Implémente le contrat :
 *
 *   POST /parties/:id/jouer_carte
 *   {
 *     "joueur_id": "J000001",
 *     "carte_id": "MES-001",
 *     "params": {
 *       "cible_id": "...",
 *       "effort_attention": 2,
 *       "effort_cp": 1
 *     }
 *   }
 *
 * - params est optionnel.
 * - si effort_attention / effort_cp sont absents, le moteur utilise :
 *   - effort_attention -> cout_attention de la carte
 *   - effort_cp        -> cout_cp de la carte
 */
export async function jouerCarteDirectement(
  partieId: string,
  acteurId: string,
  carteId: string,
  params?: JouerCarteParams
): Promise<ReponseEtat> {
  const donnees: Record<string, any> = {
    joueur_id: acteurId,
    carte_id: carteId,
  };

  // si on a des paramètres d’effort / cible, on les encapsule dans params
  if (params && Object.keys(params).length > 0) {
    donnees.params = { ...params };
  }

  const payload: RequeteAction = {
    acteur: acteurId,
    type_action: "joueur.jouer_carte",
    donnees,
  };

  return await postJson<ReponseEtat>(
    `/parties/${encodeURIComponent(partieId)}/actions`,
    payload
  );
}


