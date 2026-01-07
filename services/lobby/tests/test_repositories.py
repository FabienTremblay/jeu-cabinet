# services/lobby/tests/test_repositories.py
from __future__ import annotations

from services.lobby.domaine import Table, StatutTable
from services.lobby.repositories import TableRepository


def test_trouver_table_active_du_joueur_consider_statuts_et_roles():
    repo = TableRepository()

    # table 1 : ouverte, joueur hôte
    t1 = Table(
        id_table="T000001",
        nom_table="Table 1",
        nb_sieges=2,
        id_hote="J000001",
    )
    repo.ajouter(t1)

    # table 2 : en_cours, joueur invité
    t2 = Table(
        id_table="T000002",
        nom_table="Table 2",
        nb_sieges=2,
        id_hote="J000010",
        joueurs_assis=["J000001"],
        statut=StatutTable.EN_COURS,
    )
    repo.ajouter(t2)

    # table 3 : terminee, ne doit pas compter
    t3 = Table(
        id_table="T000003",
        nom_table="Table 3",
        nb_sieges=2,
        id_hote="J000001",
        statut=StatutTable.TERMINEE,
    )
    repo.ajouter(t3)

    # on doit trouver une table "active" pour ce joueur
    t_active = repo.trouver_table_active_du_joueur("J000001")
    assert t_active is not None
    assert t_active.id_table in {"T000001", "T000002"}

    # joueur inconnu -> None
    assert repo.trouver_table_active_du_joueur("J999999") is None
