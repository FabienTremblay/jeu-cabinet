// src/api/moteurApi.test.ts
import { describe, it, expect, vi, beforeEach } from "vitest";
import type { RequeteAction } from "../types/game";

// IMPORTANT : on définit le mock AVANT d'importer moteurApi.ts
vi.mock("./apiClient", () => {
  // ces fonctions seront les "vraies" implémentations utilisées par moteurApi.ts
  const getJson = vi.fn();
  const postJson = vi.fn();

  const makeGetJson = vi.fn((_envKey: string, _defaultUrl: string) => {
    // moteurApi.ts va appeler makeGetJson(...), qui retourne getJson
    return getJson;
  });

  const makePostJson = vi.fn((_envKey: string, _defaultUrl: string) => {
    // idem pour postJson
    return postJson;
  });

  return {
    makeGetJson,
    makePostJson,
    // on expose aussi directement getJson/postJson pour les assertions
    getJson,
    postJson,
  };
});

// Maintenant qu'on a posé le mock, on peut importer ce dont on a besoin
import {
  makeGetJson,
  makePostJson,
  getJson,
  postJson,
} from "./apiClient";

import {
  lireEtatPartie,
  soumettreAction,
  jouerCarteDirectement,
} from "./moteurApi";

describe("api/moteurApi", () => {
  beforeEach(() => {
    getJson.mockReset();
    postJson.mockReset();
  });

  it("initialise makeGetJson et makePostJson avec VITE_MOTEUR_BASE_URL et l'URL par défaut", () => {
    // Ces appels ont eu lieu à l'import de moteurApi.ts
    expect(makeGetJson).toHaveBeenCalledTimes(1);
    expect(makePostJson).toHaveBeenCalledTimes(1);

    const [envKeyGet, defaultUrlGet] = makeGetJson.mock.calls[0];
    const [envKeyPost, defaultUrlPost] = makePostJson.mock.calls[0];

    expect(envKeyGet).toBe("VITE_MOTEUR_BASE_URL");
    expect(defaultUrlGet).toBe("http://moteur-api.localhost");

    expect(envKeyPost).toBe("VITE_MOTEUR_BASE_URL");
    expect(defaultUrlPost).toBe("http://moteur-api.localhost");
  });

  it("lireEtatPartie appelle getJson avec le bon chemin et relaie la réponse", async () => {
    const fakeResponse = { partie_id: "P000001", etat: { tour: 1 } };
    getJson.mockResolvedValueOnce(fakeResponse);

    const res = await lireEtatPartie("P000001");

    expect(getJson).toHaveBeenCalledTimes(1);
    expect(getJson).toHaveBeenCalledWith("/parties/P000001/etat");
    expect(res).toEqual(fakeResponse);
  });

  it("soumettreAction poste l'action au bon endpoint", async () => {
    const fakeResponse = { ok: true };
    postJson.mockResolvedValueOnce(fakeResponse);

    const action: RequeteAction = {
      acteur: "J000001",
      type_action: "programme.engager_carte",
      donnees: {
        joueur_id: "J000001",
        carte_id: "MES-001",
      },
    };

    const res = await soumettreAction("P000001", action);

    expect(postJson).toHaveBeenCalledTimes(1);
    expect(postJson).toHaveBeenCalledWith(
      "/parties/P000001/actions",
      action
    );
    expect(res).toEqual(fakeResponse);
  });

  it("jouerCarteDirectement construit la bonne RequeteAction et l'envoie via POST", async () => {
    const fakeResponse = { ok: true };
    postJson.mockResolvedValueOnce(fakeResponse);

    const partieId = "P000123";
    const acteurId = "J000999";
    const carteId = "MES-777";

    const res = await jouerCarteDirectement(partieId, acteurId, carteId);

    expect(postJson).toHaveBeenCalledTimes(1);

    const [path, payload] = postJson.mock.calls[0];

    // 1) endpoint correct
    expect(path).toBe(`/parties/${partieId}/actions`);

    // 2) payload correct
    const sent = payload as RequeteAction;

    expect(sent.acteur).toBe(acteurId);
    expect(sent.type_action).toBe("joueur.jouer_carte");
    expect(sent.donnees).toBeDefined();
    expect(sent.donnees!.joueur_id).toBe(acteurId);
    expect(sent.donnees!.carte_id).toBe(carteId);

    expect(res).toEqual(fakeResponse);
  });
});
