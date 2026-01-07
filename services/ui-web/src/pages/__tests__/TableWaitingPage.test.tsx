/**
 * @vitest-environment happy-dom
 */
// src/pages/__tests__/TableWaitingPage.test.tsx
import React from "react";
import { describe, it, expect, vi, beforeEach } from "vitest";
import { MemoryRouter, Routes, Route } from "react-router-dom";
import { render, waitFor } from "@testing-library/react";

import TableWaitingPage from "../TableWaitingPage";
import { useSituationPolling } from "../../hooks/useSituationPolling";

// --- mocks de contexte de session -------------------------------------------

vi.mock("../../context/SessionContext", () => ({
  useSession: () => ({
    joueur: {
      id_joueur: "J000001",
      alias: "Georges",
      nom: "Georges",
      courriel: "georges@example.com",
    },
    // les autres champs du contexte ne sont pas utilisés ici
  }),
}));

// --- mocks API lobby ---------------------------------------------------------

vi.mock("../../api/lobbyApi", () => ({
  listerJoueursTable: vi.fn().mockResolvedValue({
    id_table: "T000001",
    joueurs: [
      {
        id_joueur: "J000001",
        alias: "Georges",
        nom: "Georges",
        courriel: "georges@example.com",
        pret: true,
        role: "hote",
      },
    ],
  }),
  joueurPret: vi.fn(),
  lancerPartie: vi.fn().mockResolvedValue({ id_partie: "P000001" }),
}));

// --- mock du hook de polling -------------------------------------------------

vi.mock("../../hooks/useSituationPolling");

function renderWithRouter(
  ui: React.ReactElement,
  initialPath = "/tables/T000001"
) {
  return render(
    <MemoryRouter initialEntries={[initialPath]}>
      <Routes>
        <Route path="/tables/:tableId" element={ui} />
        <Route path="/parties/:partieId" element={<div>Page partie</div>} />
        <Route path="/lobby" element={<div>Lobby</div>} />
      </Routes>
    </MemoryRouter>
  );
}

describe("TableWaitingPage – redirections automatiques", () => {
  const mockedUseSituation = useSituationPolling as unknown as vi.Mock;

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("redirige vers la partie lorsque ancrage.type = 'partie'", async () => {
    mockedUseSituation.mockReturnValue({
      situation: {
        version: 1,
        joueur_id: "J000001",
        ancrage: {
          type: "partie",
          table_id: "T000001",
          partie_id: "P000001",
        },
        etat_partie: {
          phase: "tour",
          sous_phase: null,
          tour: 1,
        },
      },
      marqueurs: { en_partie: true, retour_lobby: false },
      ancrage: {
        type: "partie",
        table_id: "T000001",
        partie_id: "P000001",
      },
      loading: false,
      error: null,
    });

    renderWithRouter(<TableWaitingPage />);

    await waitFor(() => {
      expect(document.body.textContent).toContain("Page partie");
    });
  });

  it("redirige vers le lobby lorsque marqueurs.retour_lobby = true", async () => {
    mockedUseSituation.mockReturnValue({
      situation: {
        version: 1,
        joueur_id: "J000001",
        ancrage: {
          type: "table",
          table_id: "T000001",
          partie_id: null,
        },
        etat_partie: null,
      },
      marqueurs: { en_partie: false, retour_lobby: true },
      ancrage: {
        type: "table",
        table_id: "T000001",
        partie_id: null,
      },
      loading: false,
      error: null,
    });

    renderWithRouter(<TableWaitingPage />);

    await waitFor(() => {
      expect(document.body.textContent).toContain("Lobby");
    });
  });

  it("ne redirige pas quand on reste dans une table normale", async () => {
    mockedUseSituation.mockReturnValue({
      situation: {
        version: 1,
        joueur_id: "J000001",
        ancrage: {
          type: "table",
          table_id: "T000001",
          partie_id: null,
        },
        etat_partie: null,
      },
      marqueurs: { en_partie: false, retour_lobby: false },
      ancrage: {
        type: "table",
        table_id: "T000001",
        partie_id: null,
      },
      loading: false,
      error: null,
    });

    renderWithRouter(<TableWaitingPage />);

    await waitFor(() => {
      // on reste sur la page de la table
      expect(document.body.textContent).toContain("Table T000001");
    });
  });
});
