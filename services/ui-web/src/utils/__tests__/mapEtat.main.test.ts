// src/utils/__tests__/mapEtat.main.test.ts
// Vérifie que `mapEtatToGameState` projette correctement la main du joueur courant.

import { describe, it, expect } from 'vitest'
import { mapEtatToGameState } from '../mapEtat'

function repEtatAvecMain() {
  return {
    partie_id: 'P000001',
    etat: {
      tour: 1,
      phase: 'PHASE_PROGRAMME',
      sous_phase: 'PHASE_ENGAGER',
      axes: {},
      // joueur courant J000001 avec une main contenant 2 cartes
      joueurs: {
        J000001: {
          id: 'J000001',
          alias: 'Georges',
          attention_dispo: 3,
          attention_max: 3,
          main: ['MES-001', 'MES-002'],
        },
      },
      // définitions des cartes
      cartes_def: {
        'MES-001': {
          id: 'MES-001',
          nom: 'Mesure 1',
          type: 'mesure',
          cout_attention: 1,
          cout_cp: 2,
          commandes: [
            { op: 'axes.delta', axe: 'social', delta: +1 },
          ],
        },
        'MES-002': {
          id: 'MES-002',
          nom: 'Mesure 2',
          type: 'mesure',
          cout_attention: 0,
          cout_cp: 0,
          commandes: [],
        },
      },
      programme: { cartes: [] },
      capital_collectif: 0,
      opposition: 0,
      historiques: [],
      attente: null,
      termine: false,
      raison_fin: null,
      palmares: undefined,
    },
  }
}

describe('mapEtatToGameState — main du joueur courant', () => {
  it('projette les cartes de la main avec leurs métadonnées', () => {
    const rep = repEtatAvecMain()

    const vue = mapEtatToGameState(rep as any, 'J000001')

    // 1) la main contient bien 2 cartes
    expect(vue.main_joueur_courant).toBeDefined()
    expect(vue.main_joueur_courant.length).toBe(2)

    const [c1, c2] = vue.main_joueur_courant

    // 2) première carte : MES-001
    expect(c1.id).toBe('MES-001')
    expect(c1.nom).toBe('Mesure 1')
    expect(c1.type).toBe('mesure')
    expect(c1.cout_attention).toBe(1)
    expect(c1.cout_cp).toBe(2)
    expect(typeof c1.resume).toBe('string')
    expect(c1.details).toBeDefined()
    expect(Array.isArray(c1.details)).toBe(true)
    expect(c1.details.length).toBeGreaterThan(0)
    // on s'assure que les détails mentionnent au moins l'opération axes.delta
    const texte = c1.details.join(" ");
    expect(texte).toContain("social");
    expect(texte).toContain("(+1)");
    expect(texte).not.toContain("axes.delta");


    // 3) deuxième carte : MES-002
    expect(c2.id).toBe('MES-002')
    expect(c2.nom).toBe('Mesure 2')
    expect(c2.type).toBe('mesure')
    expect(c2.cout_attention).toBe(0)
    expect(c2.cout_cp).toBe(0)
  })
})

