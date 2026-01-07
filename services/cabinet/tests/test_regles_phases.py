from __future__ import annotations
from typing import List, Dict, Any
from copy import deepcopy

import pytest

from services.cabinet.skins.minimal.config import SKIN_CONFIG
from services.cabinet.moteur.config_loader import construire_etat
from services.cabinet.moteur.regles_interfaces import ReglesInterface, Command


# -------------------------------------------------------------------------
# Skin de test — Config dérivée de SKIN_CONFIG + règles spéciales
# -------------------------------------------------------------------------

def make_test_skin_config(**overrides):
    """Fabrique une config de skin pour les tests, basée sur le skin minimal."""
    cfg = deepcopy(SKIN_CONFIG)
    cfg.update(overrides)
    return cfg


class ReglesTestPhases(ReglesInterface):
    """Moteur de règles de test : uniquement pour vérifier l'enchaînement des phases."""

    def regle_sous_phase(self, etat, signal: str) -> List[Command]:
        # Ici, chaque signal force un passage explicite vers une sous-phase suivante
        if signal == "on_start_monde":
            return [{"op": "phase.set", "sous_phase": "cabinet"}]

        if signal == "on_conseil":
            return [{"op": "phase.set", "sous_phase": "vote"}]

        if signal == "on_vote_programme":
            return [{"op": "phase.set", "sous_phase": "cloture"}]

        if signal == "on_cloture_tour":
            return [
                {"op": "tour.increment"},
                {"op": "phase.set", "sous_phase": "monde"},
            ]

        # fallback
        return [{"op": "journal", "payload": {"signal": signal}}]

    def procedure_vote(self, etat) -> List[Command]:
        return []

    def regle_attente_terminee(self, etat, type_attente: str) -> List[Command]:
        return []

# -------------------------------------------------------------------------
# Monkeypatch pour charger la skin de test
# -------------------------------------------------------------------------

@pytest.fixture
def skin_test_phases(monkeypatch):
    """Installe une skin 'test_phases' pendant le test via monkeypatch."""

    cfg = make_test_skin_config(
        phases_tour=["monde", "cabinet", "vote", "cloture"],
        phases_signals={
            "monde": "on_start_monde",
            "cabinet": "on_conseil",
            "vote": "on_vote_programme",
            "cloture": "on_cloture_tour",
        },
        cartes=[],
        events=[],
        capital_init=0,
        capital_collectif_init=0,
        main_init=0,
    )

    regles = ReglesTestPhases()

    # On monkeypatch la fonction de chargement
    def fake_loader(skin: str):
        if skin == "test_phases":
            return cfg, regles
        raise ValueError(f"Skin inattendue : {skin}")

    monkeypatch.setattr(
        "services.cabinet.moteur.config_loader.charger_config_et_regles",
        fake_loader
    )

    return "test_phases"


# -------------------------------------------------------------------------
# Tests
# -------------------------------------------------------------------------


def test_cycle_phases_simple(skin_test_phases):
    etat = construire_etat(
        skin=skin_test_phases,
        partie_id="P1",
        joueurs={"J1": {"nom": "Joueur 1"}},
    )

    # début
    assert etat.sous_phase is None
    assert etat.tour == 1

    # monde → cabinet
    cmds = etat.regles.regle_sous_phase(etat, "on_start_monde")
    etat.appliquer_commandes(cmds)
    assert etat.sous_phase == "cabinet"

    # cabinet → vote
    cmds = etat.regles.regle_sous_phase(etat, "on_conseil")
    etat.appliquer_commandes(cmds)
    assert etat.sous_phase == "vote"

    # vote → cloture
    cmds = etat.regles.regle_sous_phase(etat, "on_vote_programme")
    etat.appliquer_commandes(cmds)
    assert etat.sous_phase == "cloture"

    # cloture → monde + tour.increment
    cmds = etat.regles.regle_sous_phase(etat, "on_cloture_tour")
    etat.appliquer_commandes(cmds)
    assert etat.sous_phase == "monde"
    assert etat.tour == 2


def test_ops_phase_set_et_tour_increment(skin_test_phases):
    etat = construire_etat(
        skin=skin_test_phases,
        partie_id="P2",
        joueurs={"J1": {"nom": "Joueur 1"}},
    )

    etat.appliquer_commandes([
        {"op": "phase.set", "sous_phase": "monde"},
        {"op": "tour.increment"},
        {"op": "phase.set", "sous_phase": "vote"},
    ])

    assert etat.sous_phase == "vote"
    assert etat.tour == 2

