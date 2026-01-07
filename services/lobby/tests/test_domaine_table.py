# services/lobby/tests/test_domaine_table.py
from __future__ import annotations
import pytest

from services.lobby.domaine import Table, StatutTable


def test_prendre_siege_et_statut_en_preparation():
    table = Table(
        id_table="T000001",
        nom_table="Table test",
        nb_sieges=2,
        id_hote="J000001",
    )

    assert table.statut == StatutTable.OUVERTE

    joueur_siege = table.prendre_siege("J000002", role="invite")

    assert joueur_siege.id_joueur == "J000002"
    assert joueur_siege.role == "invite"
    assert table.joueurs_assis == ["J000002"]
    # Quand la table devient complète (hôte inclus) → en_preparation
    assert table.statut == StatutTable.EN_PREPARATION

def test_statut_reste_ouverte_tant_qu_il_reste_place():
    # hôte fait partie des joueurs : table 1/4 à la création
    table = Table(
        id_table="T000001",
        nom_table="Table test",
        nb_sieges=4,
        id_hote="J000001",
    )
    assert table.statut == StatutTable.OUVERTE

    # 2/4 -> reste ouverte
    table.prendre_siege("J000002", role="invite")
    assert table.statut == StatutTable.OUVERTE

    # 3/4 -> reste ouverte
    table.prendre_siege("J000003", role="invite")
    assert table.statut == StatutTable.OUVERTE

    # 4/4 -> devient en_preparation
    table.prendre_siege("J000004", role="invite")
    assert table.statut == StatutTable.EN_PREPARATION



def test_marquer_joueurs_prets_et_tous_les_joueurs_prets():
    table = Table(
        id_table="T000001",
        nom_table="Table test",
        nb_sieges=2,
        id_hote="J000001",
    )

    table.prendre_siege("J000002", role="invite")

    # Au départ, personne prêt
    assert table.tous_les_joueurs_prets() is False

    # On marque l'hôte prêt
    table.marquer_joueur_pret("J000001")
    assert table.tous_les_joueurs_prets() is False

    # On marque le joueur 2 prêt
    table.marquer_joueur_pret("J000002")
    assert table.tous_les_joueurs_prets() is True


def test_prendre_siege_refuse_joueur_deja_assis():
    table = Table(
        id_table="T000001",
        nom_table="Table test",
        nb_sieges=2,
        id_hote="J000001",
    )
    table.prendre_siege("J000002", role="invite")

    # même joueur tente de se rasseoir
    try:
        table.prendre_siege("J000002", role="invite")
        assert False, "devrait lever ValueError"
    except ValueError as e:
        assert str(e) == "joueur_deja_assis"


def test_prendre_siege_refuse_si_plus_de_place():
    table = Table(
        id_table="T000001",
        nom_table="Table test",
        nb_sieges=2,
        id_hote="J000001",
    )
    # 1er invité : table pleine (hôte + invité)
    table.prendre_siege("J000002", role="invite")

    # 2e invité : plus de place
    with pytest.raises(ValueError) as exc:
        table.prendre_siege("J000003", role="invite")
    assert str(exc.value) == "plus_de_place_disponible"

    try:
        table.prendre_siege("J000003", role="invite")
        assert False, "devrait lever ValueError"
    except ValueError as e:
        assert str(e) == "plus_de_place_disponible"


def test_prendre_siege_refuse_hote_incoherent():
    table = Table(
        id_table="T000001",
        nom_table="Table test",
        nb_sieges=2,
        id_hote="J000001",
    )

    try:
        table.prendre_siege("J000002", role="hote")
        assert False, "devrait lever ValueError"
    except ValueError as e:
        assert str(e) == "hote_incoherent"


def test_marquer_joueur_pret_refuse_joueur_non_assis():
    table = Table(
        id_table="T000001",
        nom_table="Table test",
        nb_sieges=2,
        id_hote="J000001",
    )

    # J000002 n'est ni hôte ni assis
    try:
        table.marquer_joueur_pret("J000002")
        assert False, "devrait lever ValueError"
    except ValueError as e:
        assert str(e) == "joueur_non_assis"

