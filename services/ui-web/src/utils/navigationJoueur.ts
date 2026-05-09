import { lireContexteRepriseJoueur } from "../api/lobbyApi";
import { lireSituationJoueur } from "../api/uiEtatJoueur";
import type { ReponseContexteReprise } from "../types/lobby";
import type { SituationUI } from "../types/uiEtat";

export type DestinationJoueur = "/lobby" | `/tables/${string}` | `/parties/${string}`;

function valeurTexte(value: unknown): string | null {
  return typeof value === "string" && value.trim() ? value.trim() : null;
}

function phaseTerminee(situation: SituationUI | null | undefined): boolean {
  const phase = valeurTexte(situation?.etat_partie?.phase);
  return phase?.toUpperCase() === "TERMINEE";
}

export function destinationDepuisSituationUI(
  situation: SituationUI | null | undefined
): DestinationJoueur | null {
  const ancrage = situation?.ancrage;
  if (!ancrage) return null;

  const type = valeurTexte((ancrage as any).type);
  const tableId =
    valeurTexte((ancrage as any).table_id) ??
    valeurTexte((ancrage as any).id_table) ??
    valeurTexte((ancrage as any).table);
  const partieId =
    valeurTexte((ancrage as any).partie_id) ??
    valeurTexte((ancrage as any).id_partie) ??
    valeurTexte((ancrage as any).partie);

  if (type === "partie" && partieId && !phaseTerminee(situation)) {
    return `/parties/${partieId}`;
  }

  if (type === "table" && tableId) {
    return `/tables/${tableId}`;
  }

  return null;
}

export function destinationDepuisContexteLobby(
  contexte: ReponseContexteReprise | null | undefined
): DestinationJoueur {
  const statut = valeurTexte(contexte?.statut_table)?.toLowerCase() ?? null;
  const tableId = valeurTexte(contexte?.id_table);
  const partieId = valeurTexte(contexte?.id_partie);

  if (statut === "en_cours" && partieId) {
    return `/parties/${partieId}`;
  }

  if ((statut === "ouverte" || statut === "en_preparation") && tableId) {
    return `/tables/${tableId}`;
  }

  return "/lobby";
}

export async function resoudreDestinationJoueur(
  idJoueur: string
): Promise<DestinationJoueur> {
  try {
    const situation = await lireSituationJoueur(idJoueur);
    const situationUI = situation as unknown as SituationUI;
    const destination = destinationDepuisSituationUI(situationUI);
    if (destination) return destination;

    if (phaseTerminee(situationUI)) {
      return "/lobby";
    }
  } catch (err) {
    console.warn("Impossible de lire la situation du joueur :", err);
  }

  try {
    const contexte = await lireContexteRepriseJoueur(idJoueur);
    return destinationDepuisContexteLobby(contexte);
  } catch (err) {
    console.warn("Impossible de lire le contexte de reprise du joueur :", err);
    return "/lobby";
  }
}
