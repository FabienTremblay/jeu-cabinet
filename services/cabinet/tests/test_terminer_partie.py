# rôle        : vérifie la terminaison de partie par le manager
# usage       : tests pytest du noyau cabinet
# contexte    : commande partie.terminer et événement domaine D600
# statut      : actif
from __future__ import annotations


def test_manager_terminer_reutilise_commande_et_preserve_raison(pm):
    etat = pm.creer("minimal", "P-TIMEOUT", {"J1": {"nom": "Alice"}})

    etat = pm.terminer("P-TIMEOUT", raison="TIMEOUT_INACTIVITE")

    assert etat.termine is True
    assert etat.raison_fin == "TIMEOUT_INACTIVITE"
    assert etat.phase == "fin_jeu"

    evenements = etat.vider_evenements()
    evt = next(e for e in evenements if e.op_code == "partie.terminer")
    assert evt.event_type == "cab.D600.partie.terminer"
    assert evt.op_family == "D600"
    assert evt.data["raison"] == "TIMEOUT_INACTIVITE"


def test_manager_terminer_est_idempotent_apres_fin(pm):
    etat = pm.creer("minimal", "P-DEJA-FINIE", {"J1": {"nom": "Alice"}})

    pm.terminer("P-DEJA-FINIE", raison="TIMEOUT_INACTIVITE")
    premiers_evenements = etat.vider_evenements()
    pm.terminer("P-DEJA-FINIE", raison="TIMEOUT_INACTIVITE")
    seconds_evenements = etat.vider_evenements()

    assert any(e.op_code == "partie.terminer" for e in premiers_evenements)
    assert seconds_evenements == []
