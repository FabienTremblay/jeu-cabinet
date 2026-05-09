import { describe, expect, it, vi } from "vitest";

const patchJson = vi.hoisted(() => vi.fn());

vi.mock("./apiClient", () => ({
  makeGetJson: vi.fn(() => vi.fn()),
  makePostJson: vi.fn(() => vi.fn()),
  makePatchJson: vi.fn(() => patchJson),
}));

import { modifierConfigurationTable } from "./lobbyApi";

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
});
