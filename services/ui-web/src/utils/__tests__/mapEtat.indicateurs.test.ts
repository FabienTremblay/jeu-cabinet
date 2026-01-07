// src/utils/__tests__/mapEtat.indicateurs.test.ts
// Vérifie que `mapEtatToGameState` projette correctement les indicateurs globaux.

import { describe, it, expect } from 'vitest'
import { mapEtatToGameState } from '../mapEtat'

function repEtatAvecIndicateurs() {
  return {
    partie_id: 'P000001',
    etat: {
      tour: 3,
      phase: 'PHASE_PROGRAMME',
      sous_phase: 'PHASE_ENGAGER',
      // axes tels que renvoyés par le moteur
      axes: {
        social: { id: 'social', valeur: 2, seuil_crise: -5, poids: 1 },
        economique: { id: 'economique', valeur: -1, seuil_crise: -5, poids: 1 },
      },
      joueurs: {},
      cartes_def: {},
      programme: { cartes: [] },
      capital_collectif: 4,
      opposition: 7,
      historiques: [],
      attente: null,
      termine: false,
      raison_fin: null,
      palmares: undefined,
    },
  }
}

describe('mapEtatToGameState — indicateurs globaux', () => {
  it('projette capital_collectif, opposition et axes', () => {
    const rep = repEtatAvecIndicateurs()

    const vue = mapEtatToGameState(rep as any, 'J000001')

    // 1) indicateurs présents
    expect(vue.indicateurs).toBeDefined()

    // 2) capital_collectif et opposition recopiés
    expect(vue.indicateurs.capital_collectif).toBe(4)
    expect(vue.indicateurs.opposition).toBe(7)

    // 3) axes projetés en valeurs numériques
    expect(vue.indicateurs.axes).toBeDefined()
    expect(vue.indicateurs.axes.social).toBe(2)
    expect(vue.indicateurs.axes.economique).toBe(-1)

  })
})


it("normalise capital_collectif et opposition quand envoyés sous forme d'objet capital_politique", () => {
  const repEtat = {
    partie_id: "P000001",
    etat: {
      tour: 1,
      phase: "PHASE_PROGRAMME",
      sous_phase: "PHASE_ENGAGER",
      axes: {},
      joueurs: {},

      capital_collectif: {
        capital_politique: 10,
        donnees_skin: { label: "collectif" },
      },
      opposition: {
        capital_politique: 5,
        donnees_skin: { label: "opposition" },
      },

      cartes_def: {},
      programme: { cartes: [] },
      historiques: [],
      attente: null,
      termine: false,
      raison_fin: null,
      palmares: undefined,
    },
  };

  const vue = mapEtatToGameState(repEtat as any, "J000001");

  expect(vue.indicateurs.capital_collectif).toBe(10);
  expect(vue.indicateurs.opposition).toBe(5);

  expect(typeof vue.indicateurs.capital_collectif).toBe("number");
  expect(typeof vue.indicateurs.opposition).toBe("number");
});

it("normalise capital_politique du joueur quand il est encapsulé dans un objet", () => {
  const repEtat = {
    partie_id: "P000001",
    etat: {
      tour: 1,
      phase: "PHASE_PROGRAMME",
      sous_phase: "PHASE_ENGAGER",
      axes: {},
      joueurs: {
        J000001: {
          id: "J000001",
          alias: "Georges",
          capital_politique: {
            capital_politique: 12,
            donnees_skin: { couleur: "bleu" },
          },
          main: [],
        },
      },

      capital_collectif: 0,
      opposition: 0,

      cartes_def: {},
      programme: { cartes: [] },
      historiques: [],
      attente: null,
      termine: false,
      raison_fin: null,
      palmares: undefined,
    },
  };

  const vue = mapEtatToGameState(repEtat as any, "J000001");

  const j = vue.joueurs["J000001"];
  expect(j).toBeDefined();
  expect(j.capital_politique).toBe(12);
  expect(typeof j.capital_politique).toBe("number");
});

