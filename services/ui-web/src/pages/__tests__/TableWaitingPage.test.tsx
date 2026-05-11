/**
 * @vitest-environment happy-dom
 */
// src/pages/__tests__/TableWaitingPage.test.tsx
import React from "react";
import { describe, it, expect, vi, beforeEach, afterEach, type Mock } from "vitest";
import { MemoryRouter, Routes, Route } from "react-router-dom";
import { act, fireEvent, render, screen, waitFor } from "@testing-library/react";

import TableWaitingPage from "../TableWaitingPage";
import AideJeuPage from "../AideJeuPage";
import { useSituationPolling } from "../../hooks/useSituationPolling";
import {
  listerJoueursTable,
  listerTables,
  modifierConfigurationTable,
} from "../../api/lobbyApi";

const mocks = vi.hoisted(() => ({
  joueurSession: {
    id_joueur: "J000001",
    alias: "Georges",
    nom: "Georges",
    courriel: "georges@example.com",
  },
  joueursTable: [
    {
      id_joueur: "J000001",
      alias: "Georges",
      nom: "Georges",
      courriel: "georges@example.com",
      pret: true,
      role: "hote",
    },
  ],
  tables: [
    {
      id_table: "T000001",
      nom_table: "Table T000001",
      nb_sieges: 2,
      id_hote: "J000001",
      statut: "en_preparation",
      skin_jeu: "minimal",
      politique_timeout_partie: {
        version: 1,
        active: true,
        delai_inactivite_secondes: 3600,
      },
    },
  ],
  modifierConfigurationTable: vi.fn(),
}));

// --- mocks de contexte de session -------------------------------------------

vi.mock("../../context/SessionContext", () => ({
  useSession: () => ({
    joueur: mocks.joueurSession,
    // les autres champs du contexte ne sont pas utilisés ici
  }),
}));

// --- mocks API lobby ---------------------------------------------------------

vi.mock("../../api/lobbyApi", () => ({
  listerJoueursTable: vi.fn(() =>
    Promise.resolve({
      id_table: "T000001",
      joueurs: mocks.joueursTable,
    })
  ),
  listerTables: vi.fn(() => Promise.resolve(mocks.tables)),
  joueurPret: vi.fn(),
  lancerPartie: vi.fn().mockResolvedValue({ id_partie: "P000001" }),
  modifierConfigurationTable: mocks.modifierConfigurationTable,
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
        <Route path="/" element={<div>Accueil</div>} />
        <Route path="/aide" element={<AideJeuPage />} />
        <Route path="/tables/:tableId" element={ui} />
        <Route path="/parties/:partieId" element={<div>Page partie</div>} />
        <Route path="/lobby" element={<div>Lobby</div>} />
      </Routes>
    </MemoryRouter>
  );
}

describe("TableWaitingPage – redirections automatiques", () => {
  const mockedUseSituation = useSituationPolling as unknown as Mock;

  beforeEach(() => {
    vi.clearAllMocks();
    vi.useRealTimers();
    mocks.joueurSession = {
      id_joueur: "J000001",
      alias: "Georges",
      nom: "Georges",
      courriel: "georges@example.com",
    };
    mocks.joueursTable = [
      {
        id_joueur: "J000001",
        alias: "Georges",
        nom: "Georges",
        courriel: "georges@example.com",
        pret: true,
        role: "hote",
      },
    ];
    mocks.tables = [
      {
        id_table: "T000001",
        nom_table: "Table T000001",
        nb_sieges: 2,
        id_hote: "J000001",
        statut: "en_preparation",
        skin_jeu: "minimal",
        politique_timeout_partie: {
          version: 1,
          active: true,
          delai_inactivite_secondes: 3600,
        },
      },
    ];
    mocks.modifierConfigurationTable.mockResolvedValue(mocks.tables[0]);
    (listerJoueursTable as unknown as Mock).mockImplementation(() =>
      Promise.resolve({
        id_table: "T000001",
        joueurs: mocks.joueursTable,
      })
    );
    (listerTables as unknown as Mock).mockImplementation(() =>
      Promise.resolve(mocks.tables)
    );
  });

  afterEach(() => {
    vi.useRealTimers();
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

  it("affiche la politique de timeout", async () => {
    mockedUseSituation.mockReturnValue({
      situation: {
        version: 1,
        joueur_id: "J000001",
        ancrage: { type: "table", table_id: "T000001", partie_id: null },
        etat_partie: null,
      },
      marqueurs: { en_partie: false, retour_lobby: false },
      ancrage: { type: "table", table_id: "T000001", partie_id: null },
      loading: false,
      error: null,
    });

    renderWithRouter(<TableWaitingPage />);

    expect(await screen.findByText("Timeout d’inactivité")).toBeInTheDocument();
    expect(document.body.textContent).toContain("Actif");
    expect(document.body.textContent).toContain("délai : 1 heure");
  });

  it("montre les contrôles à l’hôte", async () => {
    mockedUseSituation.mockReturnValue({
      situation: {
        version: 1,
        joueur_id: "J000001",
        ancrage: { type: "table", table_id: "T000001", partie_id: null },
        etat_partie: null,
      },
      marqueurs: { en_partie: false, retour_lobby: false },
      ancrage: { type: "table", table_id: "T000001", partie_id: null },
      loading: false,
      error: null,
    });

    renderWithRouter(<TableWaitingPage />);

    expect(
      await screen.findByLabelText("Timeout d’inactivité actif")
    ).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Enregistrer" })).toBeInTheDocument();
  });

  it("ne montre pas les contrôles d’édition à un invité", async () => {
    mocks.joueurSession = {
      id_joueur: "J000002",
      alias: "Invite",
      nom: "Invite",
      courriel: "invite@example.com",
    };
    mocks.joueursTable = [
      {
        id_joueur: "J000002",
        alias: "Invite",
        nom: "Invite",
        courriel: "invite@example.com",
        pret: false,
        role: "invite",
      },
    ];
    mockedUseSituation.mockReturnValue({
      situation: {
        version: 1,
        joueur_id: "J000002",
        ancrage: { type: "table", table_id: "T000001", partie_id: null },
        etat_partie: null,
      },
      marqueurs: { en_partie: false, retour_lobby: false },
      ancrage: { type: "table", table_id: "T000001", partie_id: null },
      loading: false,
      error: null,
    });

    renderWithRouter(<TableWaitingPage />);

    expect(await screen.findByText("Timeout d’inactivité")).toBeInTheDocument();
    expect(screen.queryByLabelText("Timeout d’inactivité actif")).toBeNull();
    expect(screen.queryByRole("button", { name: "Enregistrer" })).toBeNull();
    expect(document.body.textContent).toContain("Seul l’hôte peut modifier");
  });

  it("convertit les minutes en secondes lors de la sauvegarde", async () => {
    mockedUseSituation.mockReturnValue({
      situation: {
        version: 1,
        joueur_id: "J000001",
        ancrage: { type: "table", table_id: "T000001", partie_id: null },
        etat_partie: null,
      },
      marqueurs: { en_partie: false, retour_lobby: false },
      ancrage: { type: "table", table_id: "T000001", partie_id: null },
      loading: false,
      error: null,
    });

    renderWithRouter(<TableWaitingPage />);

    const delai = await screen.findByLabelText("Délai");
    fireEvent.change(delai, { target: { value: "15" } });
    fireEvent.change(screen.getByLabelText("Unité"), {
      target: { value: "minutes" },
    });
    fireEvent.click(screen.getByRole("button", { name: "Enregistrer" }));

    await waitFor(() => {
      expect(modifierConfigurationTable).toHaveBeenCalledWith({
        id_table: "T000001",
        id_hote: "J000001",
        politique_timeout_partie: {
          active: true,
          delai_inactivite_secondes: 900,
        },
      });
    });
  });

  it("ne réaffiche pas le chargement pendant le polling après le chargement initial", async () => {
    vi.useFakeTimers();
    mockedUseSituation.mockReturnValue({
      situation: {
        version: 1,
        joueur_id: "J000001",
        ancrage: { type: "table", table_id: "T000001", partie_id: null },
        etat_partie: null,
      },
      marqueurs: { en_partie: false, retour_lobby: false },
      ancrage: { type: "table", table_id: "T000001", partie_id: null },
      loading: false,
      error: null,
    });

    const attentePolling = new Promise<never>(() => undefined);
    (listerJoueursTable as unknown as Mock)
      .mockResolvedValueOnce({
        id_table: "T000001",
        joueurs: mocks.joueursTable,
      })
      .mockImplementation(() => attentePolling);

    renderWithRouter(<TableWaitingPage />);

    await act(async () => {
      await Promise.resolve();
      await Promise.resolve();
    });

    expect(screen.getByText("Table T000001")).toBeInTheDocument();

    await act(async () => {
      vi.advanceTimersByTime(3000);
    });

    expect(screen.queryByText("Chargement de la table…")).toBeNull();
    expect(screen.getByText("Timeout d’inactivité")).toBeInTheDocument();
  });

  it("conserve la valeur et le focus du formulaire timeout pendant un refresh", async () => {
    vi.useFakeTimers();
    mockedUseSituation.mockReturnValue({
      situation: {
        version: 1,
        joueur_id: "J000001",
        ancrage: { type: "table", table_id: "T000001", partie_id: null },
        etat_partie: null,
      },
      marqueurs: { en_partie: false, retour_lobby: false },
      ancrage: { type: "table", table_id: "T000001", partie_id: null },
      loading: false,
      error: null,
    });

    renderWithRouter(<TableWaitingPage />);

    await act(async () => {
      await Promise.resolve();
      await Promise.resolve();
    });

    const delai = screen.getByLabelText("Délai");
    const unite = screen.getByLabelText("Unité");
    fireEvent.change(delai, { target: { value: "15" } });
    fireEvent.change(unite, { target: { value: "minutes" } });
    delai.focus();

    mocks.tables = [
      {
        ...mocks.tables[0],
        politique_timeout_partie: {
          version: 1,
          active: true,
          delai_inactivite_secondes: 7200,
        },
      },
    ];

    await act(async () => {
      vi.advanceTimersByTime(3000);
      await Promise.resolve();
    });

    expect(screen.getByLabelText("Délai")).toHaveValue(15);
    expect(screen.getByLabelText("Unité")).toHaveValue("minutes");
    expect(document.activeElement).toBe(screen.getByLabelText("Délai"));
  });

  it("permet de revenir à la table après ouverture de l’aide timeout", async () => {
    mockedUseSituation.mockReturnValue({
      situation: {
        version: 1,
        joueur_id: "J000001",
        ancrage: { type: "table", table_id: "T000001", partie_id: null },
        etat_partie: null,
      },
      marqueurs: { en_partie: false, retour_lobby: false },
      ancrage: { type: "table", table_id: "T000001", partie_id: null },
      loading: false,
      error: null,
    });

    renderWithRouter(<TableWaitingPage />);

    fireEvent.click(await screen.findByRole("link", { name: "aide sur le timeout" }));

    expect(await screen.findByRole("heading", { name: "comprendre le jeu" }))
      .toBeInTheDocument();

    fireEvent.click(screen.getByRole("button", { name: "retour" }));

    expect(await screen.findByText("Table T000001")).toBeInTheDocument();
  });

  it("garde le retour de l’aide vers l’accueil sans paramètre de contexte", async () => {
    renderWithRouter(<AideJeuPage />, "/aide");

    expect(await screen.findByRole("heading", { name: "comprendre le jeu" }))
      .toBeInTheDocument();

    fireEvent.click(screen.getByRole("button", { name: "retour" }));

    expect(await screen.findByText("Accueil")).toBeInTheDocument();
  });
});
