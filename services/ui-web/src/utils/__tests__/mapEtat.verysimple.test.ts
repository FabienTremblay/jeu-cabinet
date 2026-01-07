// src/utils/__tests__/mapEtat.test.ts
// Test unitaire ultra-minimal pour `mapEtatToGameState`.
// Objectif: vérifier que la fonction retourne un objet cohérent
// sans faire d'hypothèse forte sur la structure interne.

import { describe, it, expect } from 'vitest'
import { mapEtatToGameState } from '../mapEtat'

describe('mapEtatToGameState', () => {
  it('retourne un objet avec quelques propriétés de base', () => {
    const etatBrut: any = {
      id: 'P000001',
      tour: 1,
      phase: 'PHASE_PROGRAMME',
      sous_phase: 'PHASE_ENGAGER',
      axes: {
        social: { id: 'social', valeur: 2, seuil_crise: -5, poids: 1 },
        economique: { id: 'economique', valeur: 3, seuil_crise: -5, poids: 1 }
      },
      joueurs: [
        {
          id: 'J000001',
          alias: 'Georges',
          capital_politique: 5,
          voix: 1,
          role: 'hote'
        }
      ],
      programme_cabinet: [],
      main_joueur_courant: [
        {
          id: 'C001',
          code: 'MES-001',
          nom: 'Mesure 1',
          cout_attention: 1
        }
      ],
      attente: null,
      termine: false,
      raison_fin: null
    }

    const vue = mapEtatToGameState(etatBrut, 'J000001')

    // La vue doit être définie et de type objet
    expect(vue).toBeDefined()
    expect(typeof vue).toBe('object')

    // Propriétés de base attendues par GamePage / GameLayout
    expect(vue).toHaveProperty('tour')
    expect(vue).toHaveProperty('phase')
    expect(vue).toHaveProperty('sous_phase')

    // Propriétés de contexte "jeu"
    expect(vue).toHaveProperty('indicateurs')
    expect(vue).toHaveProperty('joueurs')
    expect(vue).toHaveProperty('main_joueur_courant')

    // Propriété de fin de partie
    expect(vue).toHaveProperty('termine')
  })
})
