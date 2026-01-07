// src/types/lobby.ts

export interface ReponseInscription {
  id_joueur: string;
  nom: string;
  alias: string;
  courriel: string;
}

export interface ReponseConnexion {
  id_joueur: string;
  nom: string;
  alias: string;
  courriel: string;
  jeton_session: string;
}

// Ce qu'on garde en session côté front
export interface JoueurSession {
  id_joueur: string;
  nom: string;
  alias: string;
  courriel: string;
  jeton_session?: string; // présent après connexion
}

export interface ReponseJoueur {
  id_joueur: string;
  nom: string;
  alias: string | null;
  courriel: string;
}

export interface ReponseListeJoueursLobby {
  joueurs: ReponseJoueur[];
}

export type RoleTable = "hote" | "invite";

export interface ReponseJoueurTable {
  id_joueur: string;
  nom: string;
  alias: string | null;
  courriel: string;
  role: RoleTable;
  pret: boolean;
}

export interface ReponseListeJoueursTable {
  id_table: string;
  joueurs: ReponseJoueurTable[];
}

// Table telle que renvoyée par le lobby
export interface ReponseTable {
  id_table: string;
  nom_table: string;
  nb_sieges: number;
  id_hote: string;
  statut: string;          // ex: "en_preparation", "en_jeu", "terminee"
  skin_jeu?: string | null;
}

export interface ReponseListeTables {
  tables: ReponseTable[];
}

export interface ReponsePartieLancee {
  id_partie: string;
}

export interface SkinInfo {
  id_skin: string;
  nom: string;
  description?: string | null;
}

export interface ReponseListeSkins {
  skins: SkinInfo[];
}

export type TableInfo = ReponseTable;
