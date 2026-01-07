/* @vitest-environment happy-dom */

// src/hooks/useSituationPolling.test.tsx
import React from "react";
import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import TestRenderer, { act } from "react-test-renderer";

import { useSituationPolling } from "./useSituationPolling";
import type { SituationUI } from "../types/uiEtat";

// On mocke l'API ui-etat-joueur utilisée par le hook
vi.mock("../api/uiEtatJoueur", () => {
  return {
    lireSituationJoueur: vi.fn(),
  };
});

import { lireSituationJoueur } from "../api/uiEtatJoueur";

describe("useSituationPolling", () => {
  beforeEach(() => {
    vi.useFakeTimers();
    (lireSituationJoueur as unknown as vi.Mock).mockReset();
  });

  afterEach(() => {
    vi.clearAllTimers();
    vi.useRealTimers();
  });

  it("ne lance pas de polling si joueurId est null", () => {
    let hookState: any = null;

    const TestComp: React.FC<{ joueurId: string | null }> = ({ joueurId }) => {
      hookState = useSituationPolling(joueurId, { intervalMs: 1000 });
      return null;
    };

    act(() => {
      TestRenderer.create(<TestComp joueurId={null} />);
    });

    // état initial
    expect(hookState).not.toBeNull();
    expect(hookState.situation).toBeNull();
    expect(hookState.loading).toBe(false);
    expect(hookState.error).toBeNull();
    expect(hookState.marqueurs).toEqual({});
    expect(hookState.ancrage).toBeUndefined();

    // aucun appel réseau
    expect(lireSituationJoueur).not.toHaveBeenCalled();
  });

  it("appelle lireSituationJoueur quand joueurId est défini et met à jour situation/marqueurs/ancrage", async () => {
    const fakeSituation: SituationUI = {
      version: 1,
      joueur_id: "J000001",
      ancrage: { type: "partie", table_id: "T000001", partie_id: "P000001" },
      etat_partie: {
        phase: "PHASE_PROGRAMME",
        sous_phase: "PHASE_TEST",
        tour: 1,
      },
      actions_disponibles: [],
      journal_recent: [],
      marqueurs: {
        partie: 10,
        actions: 3,
        info_axes: 1,
        info_cartes: 0,
      },
    };

    (lireSituationJoueur as unknown as vi.Mock).mockResolvedValue(
      fakeSituation
    );

    let hookState: any = null;

    const TestComp: React.FC = () => {
      hookState = useSituationPolling("J000001", { intervalMs: 1000 });
      return null;
    };

    await act(async () => {
      TestRenderer.create(<TestComp />);
      // on laisse la micro-tâche de la promesse se résoudre
      await Promise.resolve();
    });

    // 1) l’API a bien été appelée
    expect(lireSituationJoueur).toHaveBeenCalledTimes(1);
    expect(lireSituationJoueur).toHaveBeenCalledWith("J000001");

    // 2) le hook reflète la situation renvoyée
    expect(hookState).not.toBeNull();
    expect(hookState.loading).toBe(false);
    expect(hookState.error).toBeNull();
    expect(hookState.situation).toEqual(fakeSituation);

    // 3) les données dérivées sont bien exposées
    expect(hookState.marqueurs).toEqual(fakeSituation.marqueurs);
    expect(hookState.ancrage).toEqual(fakeSituation.ancrage);
  });

  it("relance périodiquement le polling tant que le composant est monté", async () => {
    (lireSituationJoueur as unknown as vi.Mock).mockResolvedValue({
      version: 1,
      joueur_id: "J000001",
      ancrage: { type: "partie", table_id: "T000001", partie_id: "P000001" },
      etat_partie: null,
      actions_disponibles: [],
      journal_recent: [],
      marqueurs: { partie: 1, actions: 0, info_axes: 0, info_cartes: 0 },
    } satisfies SituationUI);

    const TestComp: React.FC = () => {
      useSituationPolling("J000001", { intervalMs: 1000 });
      return null;
    };

    await act(async () => {
      TestRenderer.create(<TestComp />);
      await Promise.resolve();
    });

    // premier appel immédiat
    expect(lireSituationJoueur).toHaveBeenCalledTimes(1);

    // on avance le temps de 1s pour déclencher le setInterval
    await act(async () => {
      vi.advanceTimersByTime(1000);
      await Promise.resolve();
    });

    expect(lireSituationJoueur).toHaveBeenCalledTimes(2);

    // encore 2 intervalles
    await act(async () => {
      vi.advanceTimersByTime(2000);
      await Promise.resolve();
    });

    expect(lireSituationJoueur).toHaveBeenCalledTimes(4);
  });

  it("remonte une erreur quand l'appel à lireSituationJoueur échoue", async () => {
    (lireSituationJoueur as unknown as vi.Mock).mockRejectedValue(
      new Error("Boom réseau")
    );

    let hookState: any = null;

    const TestComp: React.FC = () => {
      hookState = useSituationPolling("J000001", { intervalMs: 1000 });
      return null;
    };

    await act(async () => {
      TestRenderer.create(<TestComp />);
      await Promise.resolve();
    });

    expect(lireSituationJoueur).toHaveBeenCalledTimes(1);
    expect(hookState).not.toBeNull();
    expect(hookState.loading).toBe(false);
    expect(hookState.error).toBeInstanceOf(Error);
    expect((hookState.error as Error).message).toBe("Boom réseau");
  });
});
