import { describe, expect, it, vi } from "vitest";

const getJson = vi.hoisted(() => vi.fn());
const patchJson = vi.hoisted(() => vi.fn());

vi.mock("./apiClient", () => ({
  makeGetJson: vi.fn(() => getJson),
  makePostJson: vi.fn(() => vi.fn()),
  makePatchJson: vi.fn(() => patchJson),
}));

import { lireContexteRepriseJoueur, modifierConfigurationTable } from "./lobbyApi";

describe("lobbyApi", () => {
  it("appelle PATCH /api/tables/{id_table}/configuration avec la politique modifiable", async () => {
    patchJson.mockResolvedValueOnce({
      id_table: "T000001",
      nom_table: "Table",
      nb_sieges: 2,
      id_hote: "J000001",
      statut: "ouverte",
      politique_timeout_partie: {
        version: 1,
        active: false,
        delai_inactivite_secondes: 900,
      },
    });

    await modifierConfigurationTable({
      id_table: "T000001",
      id_hote: "J000001",
      politique_timeout_partie: {
        active: false,
        delai_inactivite_secondes: 900,
      },
    });

    expect(patchJson).toHaveBeenCalledWith(
      "/api/tables/T000001/configuration",
      {
        id_hote: "J000001",
        politique_timeout_partie: {
          active: false,
          delai_inactivite_secondes: 900,
        },
      }
    );
  });

  it("appelle GET /api/joueurs/{id_joueur}/contexte pour le contexte de reprise", async () => {
    getJson.mockResolvedValueOnce({
      id_joueur: "J000001",
      id_table: "T000001",
      id_partie: null,
      statut_table: "ouverte",
      skin_jeu: "minimal",
    });

    await lireContexteRepriseJoueur("J000001");

    expect(getJson).toHaveBeenCalledWith("/api/joueurs/J000001/contexte");
  });
});
