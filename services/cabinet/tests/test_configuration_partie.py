# rôle        : vérifie la conservation de configuration dans l'état moteur
# usage       : tests pytest du noyau cabinet
# contexte    : configuration effective de partie
# statut      : actif
from __future__ import annotations


def test_manager_conserve_configuration_partie(pm):
    configuration = {
        "politique_timeout_partie": {
            "version": 1,
            "active": False,
            "delai_inactivite_secondes": 600,
        }
    }

    etat = pm.creer(
        "minimal",
        "G-CONFIG",
        {"J1": {"nom": "Alice"}},
        configuration_partie=configuration,
    )

    assert etat.configuration_partie == configuration


def test_manager_sans_configuration_reste_compatible(pm):
    etat = pm.creer("minimal", "G-SANS-CONFIG", {"J1": {"nom": "Alice"}})

    assert etat.configuration_partie == {}
