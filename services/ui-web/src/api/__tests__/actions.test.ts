// src/api/__tests__/actions.test.ts
import { describe, it, expect } from "vitest";
import { construireRequeteAction } from "../actions";
import type { RequeteAction } from "../../types/game";

describe("construireRequeteAction", () => {
  it("construit une requête standard pour programme.engager_carte", () => {
    const req: RequeteAction = construireRequeteAction(
      "programme.engager_carte",
      "J000001",
      "P000001",
      { carte_id: "MES-001" }
    );

    // acteur
    expect(req.acteur).toBe("J000001");

    // type_action dérivé de l'op (upper + remplacement des points)
    expect(req.type_action).toBe("PROGRAMME_ENGAGER_CARTE");

    // donnees
    expect(req.donnees).toBeDefined();
    expect(req.donnees!.partie_id).toBe("P000001");
    expect(req.donnees!.op).toBe("programme.engager_carte");
    expect(req.donnees!.carte_id).toBe("MES-001");
  });

  it("supporte d'autres actions (ex. programme.vote) avec le même schéma", () => {
    const req: RequeteAction = construireRequeteAction(
      "programme.vote",
      "J000002",
      "P000123",
      { vote: "POUR" }
    );

    expect(req.acteur).toBe("J000002");
    expect(req.type_action).toBe("PROGRAMME_VOTE");

    expect(req.donnees).toBeDefined();
    expect(req.donnees!.partie_id).toBe("P000123");
    expect(req.donnees!.op).toBe("programme.vote");
    expect(req.donnees!.vote).toBe("POUR");
  });

  it("ajoute un payload vide si non fourni (partie_id + op uniquement)", () => {
    const req: RequeteAction = construireRequeteAction(
      "programme.terminer_engagement",
      "J000003",
      "P000999"
    );

    expect(req.acteur).toBe("J000003");
    expect(req.type_action).toBe("PROGRAMME_TERMINER_ENGAGEMENT");

    expect(req.donnees).toBeDefined();
    expect(req.donnees!.partie_id).toBe("P000999");
    expect(req.donnees!.op).toBe("programme.terminer_engagement");

    // il ne devrait pas y avoir d'autre clé que partie_id et op
    const keys = Object.keys(req.donnees!);
    expect(keys.sort()).toEqual(["op", "partie_id"].sort());
  });
});
