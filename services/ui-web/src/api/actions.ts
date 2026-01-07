// src/api/actions.ts
import type { RequeteAction } from "../types/game";

/**
 * Construit une requête d'action standardisée pour le moteur.
 *
 * @param op         code d'opération fonctionnel (ex. "programme.engager_carte")
 * @param acteurId   id du joueur qui agit
 * @param partieId   id de la partie concernée
 * @param payload    données spécifiques à l'action (ex. { carte_id: "MES-001" })
 */
export function construireRequeteAction(
  op: string,
  acteurId: string,
  partieId: string,
  payload: Record<string, unknown> = {}
): RequeteAction {
  // mapping simple entre op "métier" et type_action attendu par le moteur
  // (tu pourras affiner ce mapping plus tard si besoin)
  const type_action = op.toUpperCase().replace(/\./g, "_");

  return {
    acteur: acteurId,
    type_action,
    donnees: {
      partie_id: partieId,
      op,
      ...payload,
    },
  };
}
