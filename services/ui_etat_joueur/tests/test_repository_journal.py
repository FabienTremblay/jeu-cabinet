import datetime as dt
import pytest

from services.ui_etat_joueur.repository import DepotEtatsUI


def test_normalisation_severity_et_category_depuis_op_code_et_audience_joueur():
    depot = DepotEtatsUI()
    depot.ajouter_entree_journal(
        joueur_id="J000001",
        message="refus",
        event_id="E1",
        occurred_at=dt.datetime(2025, 1, 1, tzinfo=dt.timezone.utc),
        category="INCONNUE",
        severity="warning",
        op_code="attente.joueurs",  # doit déduire ACTION
        code="action.attente.ouverte",
        meta={"x": 1},
        audience={"scope": "joueur", "joueur_id": "J000001"},
    )

    etat = depot.obtenir_ou_creer("J000001")
    assert len(etat.journal_recent) == 1
    e = etat.journal_recent[0]
    assert e.category == "ACTION"
    assert e.severity == "warn"
    assert e.code == "action.attente.ouverte"
    assert e.meta["x"] == 1
    assert e.audience == {"scope": "joueur", "joueur_id": "J000001"}


def test_audience_incoherente_scope_joueur_leve():
    depot = DepotEtatsUI()
    with pytest.raises(ValueError):
        depot.ajouter_entree_journal(
            joueur_id="J000001",
            message="m",
            event_id="E2",
            occurred_at=dt.datetime(2025, 1, 1, tzinfo=dt.timezone.utc),
            category="ACTION",
            severity="info",
            audience={"scope": "joueur", "joueur_id": "J000002"},
        )


def test_audience_scope_all_interdite_dans_journal_joueur():
    depot = DepotEtatsUI()
    with pytest.raises(ValueError):
        depot.ajouter_entree_journal(
            joueur_id="J000001",
            message="m",
            event_id="E3",
            occurred_at=dt.datetime(2025, 1, 1, tzinfo=dt.timezone.utc),
            category="ACTION",
            severity="info",
            audience={"scope": "all"},
        )


def test_tri_chrono_ascendant():
    depot = DepotEtatsUI()
    jid = "J000001"

    t0 = dt.datetime(2025, 1, 1, 11, 0, tzinfo=dt.timezone.utc)
    t1 = dt.datetime(2025, 1, 1, 12, 0, tzinfo=dt.timezone.utc)
    t2 = dt.datetime(2025, 1, 1, 13, 0, tzinfo=dt.timezone.utc)

    depot.ajouter_entree_journal(
        joueur_id=jid,
        message="t1",
        event_id="E1",
        occurred_at=t1,
        audience={"scope": "joueur", "joueur_id": jid},
    )
    depot.ajouter_entree_journal(
        joueur_id=jid,
        message="t0",
        event_id="E0",
        occurred_at=t0,
        audience={"scope": "joueur", "joueur_id": jid},
    )
    depot.ajouter_entree_journal(
        joueur_id=jid,
        message="t2",
        event_id="E2",
        occurred_at=t2,
        audience={"scope": "joueur", "joueur_id": jid},
    )

    etat = depot.obtenir_ou_creer(jid)
    assert [e.event_id for e in etat.journal_recent] == ["E0", "E1", "E2"]


def test_limite_max_items():
    depot = DepotEtatsUI()
    jid = "J000001"

    base = dt.datetime(2025, 1, 1, tzinfo=dt.timezone.utc)
    for i in range(60):
        depot.ajouter_entree_journal(
            joueur_id=jid,
            message=f"m{i}",
            event_id=f"E{i}",
            occurred_at=base + dt.timedelta(seconds=i),
            raw={},
            audience={"scope": "joueur", "joueur_id": jid},
        )

    etat = depot.obtenir_ou_creer(jid)
    assert len(etat.journal_recent) <= 50
    # garde la fin
    assert etat.journal_recent[-1].event_id == "E59"
