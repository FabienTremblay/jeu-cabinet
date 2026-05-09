import { beforeEach, describe, expect, it, vi } from "vitest";
import { lireContexteRepriseJoueur } from "../api/lobbyApi";
import { lireSituationJoueur } from "../api/uiEtatJoueur";
import {
  destinationDepuisContexteLobby,
  destinationDepuisSituationUI,
  resoudreDestinationJoueur,
} from "./navigationJoueur";

vi.mock("../api/lobbyApi", () => ({
  lireContexteRepriseJoueur: vi.fn(),
}));

vi.mock("../api/uiEtatJoueur", () => ({
  lireSituationJoueur: vi.fn(),
}));

const situationLobby = {
  version: 1,
  joueur_id: "J000001",
  ancrage: {
    type: "lobby",
    table_id: null,
    partie_id: null,
  },
  etat_partie: {
    phase: null,
    sous_phase: null,
    tour: null,
  },
  actions_disponibles: [],
  journal_recent: [],
} as any;

describe("navigationJoueur", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("résout une table ouverte depuis le contexte lobby", async () => {
    vi.mocked(lireSituationJoueur).mockResolvedValueOnce(situationLobby);
    vi.mocked(lireContexteRepriseJoueur).mockResolvedValueOnce({
      id_joueur: "J000001",
      id_table: "T000001",
      id_partie: null,
      statut_table: "ouverte",
    });

    await expect(resoudreDestinationJoueur("J000001")).resolves.toBe(
      "/tables/T000001"
    );
  });

  it("résout une table en_preparation depuis le contexte lobby", async () => {
    vi.mocked(lireSituationJoueur).mockResolvedValueOnce(situationLobby);
    vi.mocked(lireContexteRepriseJoueur).mockResolvedValueOnce({
      id_joueur: "J000001",
      id_table: "T000002",
      id_partie: null,
      statut_table: "en_preparation",
    });

    await expect(resoudreDestinationJoueur("J000001")).resolves.toBe(
      "/tables/T000002"
    );
  });

  it("résout une partie en_cours avec id_partie depuis le contexte lobby", async () => {
    vi.mocked(lireSituationJoueur).mockResolvedValueOnce(situationLobby);
    vi.mocked(lireContexteRepriseJoueur).mockResolvedValueOnce({
      id_joueur: "J000001",
      id_table: "T000003",
      id_partie: "P000003",
      statut_table: "en_cours",
    });

    await expect(resoudreDestinationJoueur("J000001")).resolves.toBe(
      "/parties/P000003"
    );
  });

  it("reste au lobby quand le contexte lobby est vide", async () => {
    vi.mocked(lireSituationJoueur).mockResolvedValueOnce(situationLobby);
    vi.mocked(lireContexteRepriseJoueur).mockResolvedValueOnce({
      id_joueur: "J000001",
      id_table: null,
      id_partie: null,
      statut_table: null,
    });

    await expect(resoudreDestinationJoueur("J000001")).resolves.toBe("/lobby");
  });

  it("ne redirige pas automatiquement vers une partie terminée", async () => {
    vi.mocked(lireSituationJoueur).mockResolvedValueOnce({
      ...situationLobby,
      ancrage: {
        type: "partie",
        table_id: null,
        partie_id: "PTERMINEE",
      },
      etat_partie: {
        phase: "TERMINEE",
        sous_phase: null,
        tour: 4,
      },
    });

    await expect(resoudreDestinationJoueur("J000001")).resolves.toBe("/lobby");
    expect(lireContexteRepriseJoueur).not.toHaveBeenCalled();
  });

  it("garde ui-etat-joueur comme source prioritaire quand l'ancrage est utilisable", async () => {
    vi.mocked(lireSituationJoueur).mockResolvedValueOnce({
      ...situationLobby,
      ancrage: {
        type: "table",
        table_id: "TUI",
        partie_id: null,
      },
    });

    await expect(resoudreDestinationJoueur("J000001")).resolves.toBe(
      "/tables/TUI"
    );
    expect(lireContexteRepriseJoueur).not.toHaveBeenCalled();
  });

  it("ignore les contextes terminés côté lobby", () => {
    expect(
      destinationDepuisContexteLobby({
        id_joueur: "J000001",
        id_table: "TTERMINEE",
        id_partie: "PTERMINEE",
        statut_table: "terminee",
      })
    ).toBe("/lobby");
  });

  it("ignore une situation UI de partie terminée dans la résolution directe", () => {
    expect(
      destinationDepuisSituationUI({
        ...situationLobby,
        ancrage: {
          type: "partie",
          table_id: null,
          partie_id: "PTERMINEE",
        },
        etat_partie: {
          phase: "TERMINEE",
          sous_phase: null,
          tour: 1,
        },
      })
    ).toBeNull();
  });
});
