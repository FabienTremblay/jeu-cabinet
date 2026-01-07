import { describe, expect, it } from "vitest";
import {
  mapHistoriqueToUiEvents,
  mapJournalRecentToUiEvents,
  computePhaseBanner,
} from "../mapHistoriqueToUiEvent";

describe("mapHistoriqueToUiEvents", () => {
  it("mappe un journal story avec indicateurs en 'Institut de la statistique'", () => {
    const events = mapHistoriqueToUiEvents([
      {
        tour: 1,
        type: "journal",
        message: "Institut ...",
        indicateurs: { social: 0 },
      },
    ]);

    expect(events).toHaveLength(1);
    expect(events[0].kind).toBe("story");
    expect(events[0].title).toBe("Institut de la statistique");
    expect(events[0].severity).toBe("info");
  });

  it("mappe programme_carte_engagee en action success", () => {
    const events = mapHistoriqueToUiEvents([
      { tour: 1, type: "programme_carte_engagee", joueur_id: "J1", carte_id: "C1" },
    ]);

    expect(events[0].kind).toBe("action");
    expect(events[0].severity).toBe("success");
    expect(events[0].message).toContain("J1 engage C1");
  });

  it("mappe partie_terminee en system error", () => {
    const events = mapHistoriqueToUiEvents([
      { tour: 2, type: "partie_terminee", raison: "Fin forcée" },
    ]);

    expect(events[0].kind).toBe("system");
    expect(events[0].severity).toBe("error");
    expect(events[0].message).toContain("Fin forcée");
  });

  it("computePhaseBanner retourne la dernière phase", () => {
    const events = mapHistoriqueToUiEvents([
      { tour: 1, type: "phase", phase: "tour" },
      { tour: 1, type: "phase", phase: "tour", sous_phase: "PHASE_PROGRAMME" },
    ]);

    expect(computePhaseBanner(events)).toBe("tour / PHASE_PROGRAMME");
  });
});

describe("mapJournalRecentToUiEvents", () => {
  it("mappe DEROULEMENT en phase", () => {
    const events = mapJournalRecentToUiEvents([
      {
        event_id: "e1",
        occurred_at: "2025-12-11T20:16:15Z",
        category: "DEROULEMENT",
        severity: "info",
        message: "Phase tour",
      },
    ]);

    expect(events[0].source).toBe("ui-etat");
    expect(events[0].kind).toBe("phase");
    expect(events[0].severity).toBe("info");
  });

  it("mappe une sévérité null en info", () => {
    const events = mapJournalRecentToUiEvents([
      {
        event_id: "e2",
        occurred_at: "2025-12-11T20:16:15Z",
        category: null,
        severity: null,
        message: "Vous entrez dans la partie",
      },
    ]);

    expect(events[0].severity).toBe("info");
  });
});
