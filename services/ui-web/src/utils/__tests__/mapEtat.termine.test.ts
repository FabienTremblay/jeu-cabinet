// src/utils/__tests__/mapEtat.termine.test.ts
// Test unitaire ciblé sur la gestion de la fin de partie par mapEtatToGameState.

import { describe, it, expect } from 'vitest'
import { mapEtatToGameState } from '../mapEtat'

function repEtatBase() {
  return {
    partie_id: 'P000001',
    etat: {
      tour: 1,
      phase: 'PHASE_PROGRAMME',
      sous_phase: 'PHASE_ENGAGER',
      axes: {},
      joueurs: {},
      cartes_def: {},
      programme: { cartes: [] },
      capital_collectif: 0,
      opposition: 0,
      historiques: [],
      attente: null as any,
      termine: false,
      raison_fin: null as string | null,
      palmares: undefined as any
    }
  }
}

describe('mapEtatToGameState — terminaison', () => {
  it('reflète termine=false et raison_fin=null', () => {
    const rep = repEtatBase()
    rep.etat.termine = false
    rep.etat.raison_fin = null

    const vue = mapEtatToGameState(rep as any, 'J000001')

    expect(vue.termine).toBe(false)
    expect(vue.raison_fin).toBeNull()
  })

  it('reflète termine=true et copie la raison de fin', () => {
    const rep = repEtatBase()
    rep.etat.termine = true
    rep.etat.raison_fin = 'CRISE'

    const vue = mapEtatToGameState(rep as any, 'J000001')

    expect(vue.termine).toBe(true)
    expect(vue.raison_fin).toBe('CRISE')
  })
})

