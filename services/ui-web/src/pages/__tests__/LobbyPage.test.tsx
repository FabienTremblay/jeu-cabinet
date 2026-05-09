/**
 * @vitest-environment happy-dom
 */
import React from "react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { render, waitFor } from "@testing-library/react";

import LobbyPage from "../LobbyPage";
import { lireSituationJoueur } from "../../api/uiEtatJoueur";
import { lireContexteRepriseJoueur } from "../../api/lobbyApi";

const mocks = vi.hoisted(() => ({
  joueurSession: {
    id_joueur: "J000001",
    alias: "Georges",
    nom: "Georges",
    courriel: "georges@example.com",
  },
}));

vi.mock("../../context/SessionContext", () => ({
  useSession: () => ({
    joueur: mocks.joueurSession,
  }),
}));

vi.mock("../../hooks/useSituationPolling", () => ({
  useSituationPolling: () => ({
    situation: {
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
    },
    marqueurs: {},
    ancrage: {
      type: "lobby",
      table_id: null,
      partie_id: null,
    },
    loading: false,
    error: null,
  }),
}));

vi.mock("../../api/uiEtatJoueur", () => ({
  lireSituationJoueur: vi.fn(),
}));

vi.mock("../../api/lobbyApi", () => ({
  listerTables: vi.fn(() => Promise.resolve([])),
  creerTable: vi.fn(),
  listerSkins: vi.fn(() => Promise.resolve([])),
  joindreTable: vi.fn(),
  listerJoueursLobby: vi.fn(() => Promise.resolve({ joueurs: [] })),
  lireContexteRepriseJoueur: vi.fn(),
}));

function renderLobby() {
  return render(
    <MemoryRouter initialEntries={["/lobby"]}>
      <Routes>
        <Route path="/lobby" element={<LobbyPage />} />
        <Route path="/tables/:tableId" element={<div>Page table reprise</div>} />
      </Routes>
    </MemoryRouter>
  );
}

describe("LobbyPage - reprise de contexte", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    vi.mocked(lireSituationJoueur).mockResolvedValue({
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
    });
  });

  it("ne reste pas affichée quand le contexte lobby dit que le joueur est déjà assis", async () => {
    vi.mocked(lireContexteRepriseJoueur).mockResolvedValue({
      id_joueur: "J000001",
      id_table: "T000001",
      id_partie: null,
      statut_table: "en_preparation",
    });

    renderLobby();

    await waitFor(() => {
      expect(document.body.textContent).toContain("Page table reprise");
    });
  });
});
