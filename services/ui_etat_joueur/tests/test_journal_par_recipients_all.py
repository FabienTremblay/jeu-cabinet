import datetime as dt

from services.ui_etat_joueur.repository import DepotEtatsUI


def test_journal_par_recipients_all_stocke_audience_joueur():
    depot = DepotEtatsUI()
    # Deux joueurs ancrés sur la même partie (condition pour joueurs_par_partie)
    depot.ancrer_joueur_partie("J000001", "P000001")
    depot.ancrer_joueur_partie("J000002", "P000001")

    audience = {"scope": "all"}
    depot.journal_par_recipients(
        aggregate_id="P000001",
        recipients=["ALL"],
        message="Message global",
        event_id="E-ALL-1",
        occurred_at=dt.datetime(2025, 1, 1, tzinfo=dt.timezone.utc),
        category="DEROULEMENT",
        severity="info",
        code="phase.tour",
        meta={"x": 1},
        audience=audience,
        op_code="phase.tour",
        raw={"event_id": "E-ALL-1"},
    )

    e1 = depot.obtenir_ou_creer("J000001").journal_recent[-1]
    e2 = depot.obtenir_ou_creer("J000002").journal_recent[-1]

    assert e1.event_id == "E-ALL-1"
    assert e1.audience == {"scope": "joueur", "joueur_id": "J000001"}
    assert e2.audience == {"scope": "joueur", "joueur_id": "J000002"}
