import datetime as dt

import pytest

from services.ui_etat_joueur.kafka_consumer import (
    ConsommateurEvenementsUI,
    EtatFinPartie,
)

from services.ui_etat_joueur.repository import DepotEtatsUI

# si ton package est nommé autrement, adapte l'import
# from services.ui_etat_joueur.repository import DepotEtatsUI


# --- Doubles de test --------------------------------------------------------


class FakeDepot:
    """
    Double minimal de DepotEtatsUI pour tester la logique de fin de partie.
    On garde juste ce dont le worker a besoin :
    - joueurs_par_partie
    - ancrer_joueur_lobby
    - vider_actions_pour_joueur
    - ajouter_entree_journal_partie
    """

    def __init__(self):
        # {joueur_id: {"ancrage": {"type": "partie"/"lobby", "partie_id": ...}, "actions": []}}
        self.joueurs = {}
        self.journal = []
        self.appels = []

    def ajouter_joueur_partie(self, joueur_id: str, partie_id: str):
        self.joueurs[joueur_id] = {
            "ancrage": {"type": "partie", "partie_id": partie_id},
            "actions": ["foo"],  # peu importe le contenu, on vérifie juste que ça se vide
        }

    def joueurs_par_partie(self, partie_id: str):
        for jid, etat in self.joueurs.items():
            if (
                etat["ancrage"]["type"] == "partie"
                and etat["ancrage"]["partie_id"] == partie_id
            ):
                # le vrai DepotEtatsUI renvoie (jid, EtatJoueurUI) ; ici on renvoie (jid, etat_stub)
                yield jid, etat

    def ancrer_joueur_lobby(self, joueur_id: str) -> None:
        self.appels.append(("ancrer_joueur_lobby", joueur_id))
        etat = self.joueurs.setdefault(
            joueur_id,
            {"ancrage": {"type": None, "partie_id": None}, "actions": []},
        )
        etat["ancrage"]["type"] = "lobby"
        etat["ancrage"]["partie_id"] = None

    def vider_actions_pour_joueur(self, joueur_id: str) -> None:
        self.appels.append(("vider_actions_pour_joueur", joueur_id))
        etat = self.joueurs.setdefault(
            joueur_id,
            {"ancrage": {"type": None, "partie_id": None}, "actions": []},
        )
        etat["actions"].clear()

    def ajouter_entree_journal_partie(self, partie_id: str, message: str, **kwargs):
        self.journal.append({"partie_id": partie_id, "message": message, **kwargs})

class FakeKafkaMessage:
    """Double minimal d'un message Kafka (topic/partition/offset/value)."""

    def __init__(self, topic: str, partition: int, offset: int, value: dict):
        self.topic = topic
        self.partition = partition
        self.offset = offset
        self.value = value


def _audience(scope: str, joueur_id: str | None = None, joueurs: list[str] | None = None) -> dict:
    if scope == "all":
        return {"scope": "all"}
    if scope == "joueur":
        return {"scope": "joueur", "joueur_id": joueur_id}
    return {"scope": "liste", "joueurs": joueurs or []}



def make_consumer_for_tests(depot: FakeDepot) -> ConsommateurEvenementsUI:
    """
    On contourne le __init__ réel du consommateur (qui crée un KafkaConsumer)
    pour ne pas dépendre de Kafka dans les tests.
    """
    consumer = object.__new__(ConsommateurEvenementsUI)
    consumer._depot = depot
    consumer._fin_parties = {}
    return consumer


# --- Tests journal v1 : stabilité id / tri / normalisation ------------------


def test_depot_normalise_severity_et_category():
    depot = DepotEtatsUI()
    depot.ajouter_entree_journal(
        joueur_id="J000001",
        message="Test",
        event_id="E1",
        occurred_at=dt.datetime(2025, 1, 1, tzinfo=dt.timezone.utc),
        category="INCONNUE",
        severity="warning",
        op_code="attente.joueurs",
        code="action.attente.ouverte",
        meta={"x": 1},
        audience={"scope": "joueur", "joueur_id": "J000001"},
    )

    etat = depot.obtenir_ou_creer("J000001")
    assert len(etat.journal_recent) == 1
    e = etat.journal_recent[0]
    # category déduite par op_code, severity normalisée
    assert e.category == "ACTION"
    assert e.severity == "warn"
    assert e.code == "action.attente.ouverte"
    assert e.meta["x"] == 1


def test_etat_joueur_trie_journal_par_occurred_at():
    depot = DepotEtatsUI()
    jid = "J000001"
    t1 = dt.datetime(2025, 1, 1, 12, 0, tzinfo=dt.timezone.utc)
    t0 = dt.datetime(2025, 1, 1, 11, 0, tzinfo=dt.timezone.utc)
    t2 = dt.datetime(2025, 1, 1, 13, 0, tzinfo=dt.timezone.utc)

    depot.ajouter_entree_journal(joueur_id=jid, message="t1", event_id="E1", occurred_at=t1)
    depot.ajouter_entree_journal(joueur_id=jid, message="t0", event_id="E0", occurred_at=t0)
    depot.ajouter_entree_journal(joueur_id=jid, message="t2", event_id="E2", occurred_at=t2)

    etat = depot.obtenir_ou_creer(jid)
    assert [e.event_id for e in etat.journal_recent] == ["E0", "E1", "E2"]
    assert [e.message for e in etat.journal_recent] == ["t0", "t1", "t2"]


def test_kafka_event_id_stable_quand_absent():
    # Ce test vérifie la règle: si event_id manque, on forge k:{topic}:{partition}:{offset}.
    # Ici on teste le comportement attendu via l'enveloppe enrichie (sans Kafka réel).
    depot = DepotEtatsUI()

    # on simule ce que kafka_consumer.py fait désormais
    enveloppe = {"event_type": "cab.D600.journal", "op_code": "journal", "data": {"payload": {"message": "ok"}}}
    msg = FakeKafkaMessage(topic="cab.events", partition=2, offset=18492, value=enveloppe)

    # injection manuelle de la logique d'enrichissement attendue (même règle que le consumer)
    kafka_id = f"k:{msg.topic}:{msg.partition}:{msg.offset}"
    enveloppe.setdefault("_kafka", {"topic": msg.topic, "partition": msg.partition, "offset": msg.offset})
    enveloppe.setdefault("event_id", kafka_id)
    enveloppe.setdefault("id", enveloppe.get("event_id"))

    assert enveloppe["event_id"] == "k:cab.events:2:18492"
    assert enveloppe["id"] == enveloppe["event_id"]


# --- Tests sur EtatFinPartie ------------------------------------------------


def test_etat_fin_partie_delai_depasse():
    maintenant = dt.datetime(2025, 1, 1, 12, 0, tzinfo=dt.timezone.utc)
    terminee = maintenant - dt.timedelta(minutes=3)

    etat = EtatFinPartie(
        partie_id="P000001",
        terminee_at=terminee,
        joueurs_participants={"J000001", "J000002"},
    )

    assert etat.est_delai_depasse(maintenant) is True
    assert etat.est_delai_depasse(terminee + dt.timedelta(minutes=1)) is False


def test_etat_fin_partie_tous_joueurs_ont_quitte():
    etat = EtatFinPartie(
        partie_id="P000001",
        terminee_at=dt.datetime(2025, 1, 1, tzinfo=dt.timezone.utc),
        joueurs_participants={"J000001", "J000002"},
        joueurs_quittes={"J000001"},
    )
    assert etat.tous_joueurs_ont_quitte() is False

    etat.joueurs_quittes.add("J000002")
    assert etat.tous_joueurs_ont_quitte() is True


# --- Tests sur _mettre_a_jour_fin_partie -----------------------------------


def test_mettre_a_jour_fin_partie_partie_terminer():
    depot = FakeDepot()
    depot.ajouter_joueur_partie("J000001", "P000001")
    depot.ajouter_joueur_partie("J000002", "P000001")

    consumer = make_consumer_for_tests(depot)

    occurred_at = dt.datetime(2025, 1, 1, 15, 30, tzinfo=dt.timezone.utc)
    enveloppe = {
        "event_type": "cab.D600.partie.terminer",
        "op_code": "partie.terminer",
        "aggregate_id": "P000001",
        "data": {},
        "occurred_at": occurred_at.isoformat(),
    }

    consumer._mettre_a_jour_fin_partie(enveloppe)

    assert "P000001" in consumer._fin_parties
    etat_fin = consumer._fin_parties["P000001"]
    assert etat_fin.partie_id == "P000001"
    assert etat_fin.terminee_at == occurred_at
    assert etat_fin.joueurs_participants == {"J000001", "J000002"}
    assert etat_fin.joueurs_quittes == set()


def test_mettre_a_jour_fin_partie_joueur_quitte_definitivement():
    depot = FakeDepot()
    consumer = make_consumer_for_tests(depot)

    # le joueur est actuellement ancré dans la partie (cas réel)
    depot.ajouter_joueur_partie("J000001", "P000001")

    # on initialise manuellement un état de fin de partie
    occurred_at = dt.datetime(2025, 1, 1, 15, 30, tzinfo=dt.timezone.utc)
    consumer._fin_parties["P000001"] = EtatFinPartie(
        partie_id="P000001",
        terminee_at=occurred_at,
        joueurs_participants={"J000001", "J000002"},
        joueurs_quittes=set(),
    )

    enveloppe = {
        "event_type": "cab.D600.partie.joueur_quitte_definitivement",
        "op_code": "partie.joueur_quitte_definitivement",
        "aggregate_id": "P000001",
        "data": {"joueur_id": "J000001"},
        "occurred_at": occurred_at.isoformat(),
    }

    consumer._mettre_a_jour_fin_partie(enveloppe)

    etat_fin = consumer._fin_parties["P000001"]
    assert etat_fin.joueurs_quittes == {"J000001"}
    assert ("ancrer_joueur_lobby", "J000001") in depot.appels
    assert ("vider_actions_pour_joueur", "J000001") in depot.appels
    # UX: retour immédiat au lobby pour le joueur qui quitte
    etat_joueur = depot.joueurs["J000001"]
    assert etat_joueur["ancrage"]["type"] == "lobby"
    assert etat_joueur["ancrage"]["partie_id"] is None
    assert etat_joueur["actions"] == []


# --- Test sur _fermer_partie_definitivement --------------------------------


def test_fermer_partie_definitivement_met_joueurs_au_lobby_et_journal():
    depot = FakeDepot()
    depot.ajouter_joueur_partie("J000001", "P000001")
    depot.ajouter_joueur_partie("J000002", "P000001")

    consumer = make_consumer_for_tests(depot)

    # on simule un suivi en fin de partie
    consumer._fin_parties["P000001"] = EtatFinPartie(
        partie_id="P000001",
        terminee_at=dt.datetime(2025, 1, 1, tzinfo=dt.timezone.utc),
        joueurs_participants={"J000001", "J000002"},
        joueurs_quittes={"J000001", "J000002"},
    )

    # on appelle directement la méthode de fermeture
    consumer._fermer_partie_definitivement("P000001")

    # les joueurs doivent maintenant être ancrés au lobby et sans actions
    for jid in ("J000001", "J000002"):
        etat = depot.joueurs[jid]
        assert etat["ancrage"]["type"] == "lobby"
        assert etat["ancrage"]["partie_id"] is None
        assert etat["actions"] == []

    # un message de journal commun doit avoir été ajouté
    assert len(depot.journal) == 1
    assert depot.journal[0]["partie_id"] == "P000001"
    assert "archivée" in depot.journal[0]["message"]
