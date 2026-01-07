// src/utils/__tests__/mapEtat.programme.test.ts
// Vérifie que `mapEtatToGameState` projette correctement le programme du cabinet.

import { describe, it, expect } from 'vitest'
import { mapEtatToGameState } from '../mapEtat'

function repEtatAvecProgramme() {
  return {
    partie_id: 'P000001',
    etat: {
      tour: 1,
      phase: 'PHASE_PROGRAMME',
      sous_phase: 'PHASE_VOTE',
      joueurs: {},
      cartes_def: {
        'MES-001': {
          id: 'MES-001',
          nom: 'Mesure 1',
          type: 'mesure',
          cout_attention: 2,
          cout_cp: 1,
          commandes: [
            { op: 'axes.delta', axe: 'social', delta: +2 },
            { op: 'dette.delta', delta: +1 },
          ],
        },
      },
      // 👇 aligné sur l’état brut réel : programme.entrees
      programme: {
        version: 1,
        entrees: [
          {
            uid: 'EP-1',
            carte_id: 'MES-001',
            auteur_id: 'J000001',
            type: 'mesure',
            params: {},
            tags: [],
            attention_engagee: 1,
          },
        ],
        votes: {},
        verdict: true,
      },
      axes: {},
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

describe('mapEtatToGameState — programme du cabinet', () => {
  it('projette les cartes du programme avec leurs métadonnées', () => {
    const rep = repEtatAvecProgramme()

    const vue = mapEtatToGameState(rep as any, 'J000001')

    // 1) un programme projeté existe
    expect(vue.programme_cabinet).toBeDefined()
    expect(Array.isArray(vue.programme_cabinet)).toBe(true)
    expect(vue.programme_cabinet.length).toBe(1)

    const carte = vue.programme_cabinet[0]

    // 2) métadonnées correctes
    expect(carte.id).toBe('MES-001')
    expect(carte.nom).toBe('Mesure 1')
    expect(carte.type).toBe('mesure')
    expect(carte.cout_attention).toBe(2)
    expect(carte.cout_cp).toBe(1)

    // 3) résumé et détails existent
    expect(typeof carte.resume).toBe('string')

    expect(Array.isArray(carte.details)).toBe(true)
    expect(carte.details.length).toBeGreaterThan(0)

    // 4) détails lisibles : on parle de l’axe, pas de l’op interne
    const texte = carte.details.join(' ')
    expect(texte).toContain('social')
    expect(texte).toContain('(+2)')
    expect(texte).not.toContain('axes.delta')
  })
})

