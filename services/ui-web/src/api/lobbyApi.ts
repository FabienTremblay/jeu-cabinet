// src/api/lobbyApi.ts
import { makeGetJson, makePostJson } from "./apiClient";
import type {
  JoueurSession,
  ReponseInscription,
  ReponseConnexion,
  ReponseListeTables,
  ReponseTable,
  ReponseListeJoueursTable,
  ReponsePartieLancee,
  ReponseListeSkins,
  SkinInfo,
  ReponseJoueur
} from "../types/lobby";

// même logique que ton TUI : base par défaut = http://lobby.cabinet.localhost
const getJson = makeGetJson(
  "VITE_LOBBY_BASE_URL",
  "http://lobby.cabinet.localhost"
);
const postJson = makePostJson(
  "VITE_LOBBY_BASE_URL",
  "http://lobby.cabinet.localhost"
);

// ---------------------------------------------------------------------------
//  Authentification
// ---------------------------------------------------------------------------

export async function inscription(params: {
  nom: string;
  alias: string;
  courriel: string;
  mot_de_passe: string;
}): Promise<JoueurSession> {
  const data = await postJson<ReponseInscription, typeof params>(
    "/api/joueurs",
    params
  );

  const session: JoueurSession = {
    id_joueur: data.id_joueur,
    nom: data.nom,
    alias: data.alias,
    courriel: data.courriel
  };
  return session;
}

export async function connexion(params: {
  courriel: string;
  mot_de_passe: string;
}): Promise<JoueurSession> {
  const data = await postJson<ReponseConnexion, typeof params>(
    "/api/sessions",
    params
  );

  const session: JoueurSession = {
    id_joueur: data.id_joueur,
    nom: data.nom,
    alias: data.alias,
    courriel: data.courriel,
    jeton_session: data.jeton_session
  };
  return session;
}

// ---------------------------------------------------------------------------
//  Skins
// ---------------------------------------------------------------------------

export async function listerSkins(): Promise<SkinInfo[]> {
  const data = await getJson<ReponseListeSkins>("/api/skins");
  return data.skins;
}

// ---------------------------------------------------------------------------
//  Tables
// ---------------------------------------------------------------------------

export async function listerTables(statut?: string): Promise<ReponseTable[]> {
  const query = statut ? `?statut=${encodeURIComponent(statut)}` : "";
  const data = await getJson<ReponseListeTables>(`/api/tables${query}`);
  return data.tables;
}

export async function creerTable(params: {
  id_hote: string;
  nom_table: string;
  nb_sieges: number;
  mot_de_passe_table?: string | null;
  skin_jeu?: string | null;
}): Promise<ReponseTable> {
  return postJson<ReponseTable, typeof params>("/api/tables", params);
}

// ---------------------------------------------------------------------------
//  Joueurs / lobby & table
// ---------------------------------------------------------------------------

export interface ReponseListeJoueursLobby {
  joueurs: ReponseJoueur[];
}

// GET /api/joueurs/lobby
export async function listerJoueursLobby(): Promise<ReponseListeJoueursLobby> {
  return getJson<ReponseListeJoueursLobby>("/api/joueurs/lobby");
}

// GET /api/tables/{id_table}/joueurs
export async function listerJoueursTable(
  id_table: string
): Promise<ReponseListeJoueursTable> {
  return getJson<ReponseListeJoueursTable>(
    `/api/tables/${id_table}/joueurs`
  );
}

// POST /api/tables/{id_table}/joueurs
export type DemandePriseSiege = {
  id_joueur: string;
  role?: "hote" | "invite";
};

// POST /api/tables/{id_table}/joueurs
export async function joindreTable(params: {
  id_table: string;
  id_joueur: string;
  role?: "hote" | "invite";
}): Promise<void> {
  await postJson<unknown, { id_joueur: string; role?: "hote" | "invite" }>(
    `/api/tables/${params.id_table}/joueurs`,
    {
      id_joueur: params.id_joueur,
      role: params.role ?? "invite"
    }
  );
}
// POST /api/tables/{id_table}/joueurs/pret
export async function joueurPret(params: {
  id_table: string;
  id_joueur: string;
}): Promise<ReponseTable> {
  return postJson<ReponseTable, { id_joueur: string }>(
    `/api/tables/${params.id_table}/joueurs/pret`,
    { id_joueur: params.id_joueur }
  );
}

// POST /api/tables/{id_table}/lancer
export async function lancerPartie(params: {
  id_table: string;
  id_hote: string;
}): Promise<ReponsePartieLancee> {
  return postJson<ReponsePartieLancee, { id_hote: string }>(
    `/api/tables/${params.id_table}/lancer`,
    { id_hote: params.id_hote }
  );
}
// ---------------------------------------------------------------------------
//  Reconnexion : retrouver la table "ouverte" d'un joueur
// ---------------------------------------------------------------------------

export async function trouverTableOuvertePourJoueur(
  id_joueur: string
) {
  // On récupère toutes les tables, sans filtrer par statut
  const tables = await listerTables(); // pas de param

  for (const table of tables) {
    // si ton domaine a un statut "terminee", on l'ignore
    if (table.statut && table.statut.toLowerCase() === "terminee") {
      continue;
    }

    const rep = await listerJoueursTable(table.id_table);
    const estAssis = rep.joueurs.some((j) => j.id_joueur === id_joueur);

    if (estAssis) {
      return table; // ReponseTable
    }
  }

  return null;
}


