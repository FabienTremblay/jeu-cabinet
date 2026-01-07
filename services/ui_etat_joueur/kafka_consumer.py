# services/ui_etat_joueur/kafka_consumer.py
from __future__ import annotations

import json
import logging
import os
from urllib.request import urlopen
from urllib.error import URLError

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone

from typing import Iterable, List, Dict, Set, Optional

from kafka import KafkaConsumer

from .projection import appliquer_projection_evenement_domaine
from .repository import DepotEtatsUI

logger = logging.getLogger(__name__)


DELAI_FERMETURE = timedelta(minutes=2)
DEFAULT_LOBBY_BASE_URL = "http://lobby:8000"


@dataclass
class EtatFinPartie:
    partie_id: str
    terminee_at: datetime
    joueurs_participants: Set[str] = field(default_factory=set)
    joueurs_quittes: Set[str] = field(default_factory=set)

    def est_delai_depasse(self, now: datetime) -> bool:
        return now >= self.terminee_at + DELAI_FERMETURE

    def tous_joueurs_ont_quitte(self) -> bool:
        return bool(self.joueurs_participants) and (
            self.joueurs_quittes >= self.joueurs_participants
        )

class ConsommateurEvenementsUI:
    """
    Consomme les événements Kafka (moteur + lobby) pour construire l'état UI des joueurs.
    """

    def __init__(
        self,
        depot: DepotEtatsUI,
        bootstrap_servers: Iterable[str] | str,
        group_id: str,
        topic_moteur: str,
        topics_lobby: Iterable[str],
    ) -> None:
        self._depot = depot
        self._topic_moteur = topic_moteur
        self._topics_lobby = list(topics_lobby)
        self._fin_parties: Dict[str, EtatFinPartie] = {}
        self._lobby_base_url = os.getenv("UI_ETAT_LOBBY_BASE_URL", DEFAULT_LOBBY_BASE_URL).rstrip("/")
        self._lobby_timeout = float(os.getenv("UI_ETAT_LOBBY_TIMEOUT_SECONDES", "1.0"))

        if isinstance(bootstrap_servers, str):
            bootstrap = [b.strip() for b in bootstrap_servers.split(",") if b.strip()]
        else:
            bootstrap = list(bootstrap_servers)

        logger.info(
            "Initialisation du consommateur UI-etat: moteur=%s, lobby=%s",
            topic_moteur,
            self._topics_lobby,
        )

        self._consumer = KafkaConsumer(
            *([topic_moteur] + self._topics_lobby),
            bootstrap_servers=bootstrap,
            group_id=group_id,
            enable_auto_commit=True,
            auto_offset_reset="earliest",
            value_deserializer=lambda m: json.loads(m.decode("utf-8")),
        )

        logger.info(
            "Consommateur UI-etat abonné aux topics: %s",
            [topic_moteur] + self._topics_lobby,
        )

    # --- boucle principale ---

    def boucle(self) -> None:
        logger.info("Boucle de consommation UI-etat démarrée")
        for message in self._consumer:
            enveloppe = message.value
            topic = message.topic

            # ------------------------------------------------------------------
            # Stabiliser l'event_id (idempotence) : indispensable pour le dédoublonnage UI
            # ------------------------------------------------------------------
            try:
                kafka_id = f"k:{topic}:{message.partition}:{message.offset}"
                enveloppe.setdefault("_kafka", {"topic": topic, "partition": message.partition, "offset": message.offset})
                # nouveau format
                enveloppe.setdefault("event_id", kafka_id)
                # ancien format historique (utilise "id")
                enveloppe.setdefault("id", enveloppe.get("event_id"))
            except Exception:
                # ne pas bloquer le consumer pour un souci d'attribut Kafka
                pass

            type_evt = enveloppe.get("event_type") or enveloppe.get("type")
            logger.info("UI-etat: événement reçu topic=%s type=%s", topic, type_evt)

            try:
                if topic == self._topic_moteur:
                    self._traiter_evenement_moteur(enveloppe)
                else:
                    self._traiter_evenement_lobby(topic, enveloppe)
            except Exception:
                logger.exception("Erreur en traitant un message UI-etat")

    # --- moteur ---

    def _traiter_evenement_moteur(self, enveloppe: dict) -> None:
        # Nouveau format EvenementDomaine ?
        if "event_type" in enveloppe and "op_code" in enveloppe:
            # ------------------------------------------------------------------
            # Notifications ciblées / messages importants (notif.*)
            # ------------------------------------------------------------------
            # But : alimenter journal_recent (toast côté UI) avec audience correcte
            # sans polluer tous les joueurs.
            #
            # Règles :
            # - recipients=["ALL"] => audience scope=partie
            # - recipients=[jid,...] => audience scope=joueur + joueur_id
            # - severity moteur: info|warning|critical => UI: info|warn|error
            # ------------------------------------------------------------------
            try:
                op_code = (enveloppe.get("op_code") or "").strip()
                recipients = enveloppe.get("recipients") or []
                partie_id = enveloppe.get("aggregate_id")
                data = enveloppe.get("data", {}) or {}
                sev = (enveloppe.get("severity") or "").strip().lower()

                def map_sev(v: str) -> str:
                    if v == "warning":
                        return "warn"
                    if v == "critical":
                        return "error"
                    return "info"

                if op_code.startswith("notif."):
                    # On supporte 2 formes :
                    # 1) data: { op, joueur_id, code, payload:{message, refs,...} }
                    # 2) data: { message, code, ... } (fallback)
                    code = data.get("code") or (data.get("metadata") or {}).get("code")
                    payload = data.get("payload") or {}
                    message = payload.get("message") or data.get("message") or ""
                    refs = payload.get("refs") or {}

                    # Audience : par défaut, se déduit des recipients
                    def audience_for(jid: Optional[str]) -> dict:
                        if jid:
                            return {"scope": "joueur", "joueur_id": jid}
                        return {"scope": "partie", "partie_id": partie_id}

                    # on journalise *uniquement* pour les recipients (ou la partie si ALL)
                    if recipients == ["ALL"]:
                        self._depot.journal_par_recipients(
                            aggregate_id=partie_id,
                            recipients=["ALL"],
                            message=message or "Notification",
                            event_id=enveloppe.get("event_id"),
                            occurred_at=datetime.now(timezone.utc),
                            category="MESSAGE",
                            severity=map_sev(sev),
                            code=code,
                            meta={"refs": refs, "op_code": op_code},
                            audience=audience_for(None),
                            op_code=op_code,
                            raw=enveloppe,
                        )
                    else:
                        for jid in recipients:
                            if not jid:
                                continue
                            self._depot.journal_par_recipients(
                                aggregate_id=partie_id,
                                recipients=[jid],
                                message=message or "Notification",
                                event_id=enveloppe.get("event_id"),
                                occurred_at=datetime.now(timezone.utc),
                                category="MESSAGE",
                                severity=map_sev(sev),
                                code=code,
                                meta={"refs": refs, "op_code": op_code},
                                audience=audience_for(jid),
                                op_code=op_code,
                                raw=enveloppe,
                            )

                    # Important : on ne laisse pas la projection générique retraiter
                    # ces notifs si vous voulez un contrôle strict du format.
                    # (Sinon, retire ce 'return'.)
                    return
            except Exception:
                logger.exception("UI-etat: erreur projection notif.*")
 
            try:
                op_code = (enveloppe.get("op_code") or "").strip()
                partie_id = enveloppe.get("aggregate_id")
                data = enveloppe.get("data", {}) or {}

                if partie_id and op_code in {"attente.joueurs", "attente.init"}:
                    # La liste peut être dans data.joueurs (format actuel),
                    # ou dans data.payload.joueurs (fallback prudente).
                    joueurs = data.get("joueurs")
                    if joueurs is None:
                        joueurs = (data.get("payload") or {}).get("joueurs")

                    if joueurs:
                        if isinstance(joueurs, dict):
                            iterable_ids = joueurs.keys()
                        else:
                            iterable_ids = joueurs

                        for jid in iterable_ids:
                            if jid:
                                self._depot.ancrer_joueur_partie(jid, partie_id)
                    else:
                        # Dernier recours : si recipients = liste de joueurs (pas ALL)
                        recipients = enveloppe.get("recipients") or []
                        if recipients and recipients != ["ALL"]:
                            for jid in recipients:
                                self._depot.ancrer_joueur_partie(jid, partie_id)
            except Exception:
                # Ne jamais casser le traitement d'un événement si l'auto-ancrage échoue.
                pass

            appliquer_projection_evenement_domaine(self._depot, enveloppe)
            self._mettre_a_jour_fin_partie(enveloppe)
            return

        # Ancien format historique: type/payload
        type_evt = enveloppe.get("type")
        payload = enveloppe.get("payload", {}) or {}

        if type_evt == "event.partie.creee":
            partie_id = payload.get("partie_id")
            joueurs = payload.get("joueurs") or {}

            if not partie_id:
                return

            # joueurs est un dict: { "J000002": {...}, "J000001": {...} }
            if isinstance(joueurs, dict):
                iterable_ids = joueurs.keys()
            else:
                # fallback pour compat éventuelle si un jour c'est une liste
                iterable_ids = []
                for j in joueurs:
                    if isinstance(j, dict) and "id" in j:
                        iterable_ids.append(j["id"])

            for jid in iterable_ids:
                self._depot.ancrer_joueur_partie(jid, partie_id)
                self._depot.ajouter_entree_journal(
                    joueur_id=jid,
                    message=f"Vous entrez dans la partie {partie_id}",
                    event_id=enveloppe.get("id"),
                )

        elif type_evt == "phase":
            partie_id = payload.get("partie_id")
            phase = payload.get("phase")
            sous_phase = payload.get("sous_phase")
            tour = payload.get("tour")
            if partie_id:
                self._depot.maj_etat_partie_par_partie(
                    partie_id=partie_id,
                    phase=phase,
                    sous_phase=sous_phase,
                    tour=tour,
                )

        elif type_evt == "attente":
            partie_id = payload.get("partie_id")
            joueurs = payload.get("joueurs") or []
            actions_ui = (payload.get("meta") or {}).get("ui", {}).get("actions", [])

            from .domaine import ActionDisponible

            action_objs: List[ActionDisponible] = []
            for a in actions_ui:
                action_objs.append(
                    ActionDisponible(
                        code=a.get("code", ""),
                        label=a.get("label", a.get("code", "")),
                        payload=a.get("payload") or {},
                        requires_confirmation=a.get("requires_confirmation", False),
                    )
                )
            for jid in joueurs:
                self._depot.definir_actions_pour_joueur(jid, action_objs)

        elif type_evt == "journal":
            message = payload.get("message")
            joueurs = payload.get("joueurs") or []
            for jid in joueurs:
                self._depot.ajouter_entree_journal(
                    joueur_id=jid,
                    message=message,
                    event_id=enveloppe.get("id"),
                )

        else:
            logger.debug(
                "Événement moteur ignoré (ancien format): type=%s payload=%s",
                type_evt,
                payload,
            )

    # --- lobby ---

    def _recuperer_contexte_reprise(self, joueur_id: str) -> Optional[dict]:
        """
        Appel best-effort au lobby pour savoir si le joueur est déjà assis dans une table/partie.
        Ne doit jamais casser la consommation Kafka.
        """
        try:
            url = f"{self._lobby_base_url}/api/joueurs/{joueur_id}/contexte"
            with urlopen(url, timeout=self._lobby_timeout) as resp:
                raw = resp.read().decode("utf-8")
            return json.loads(raw)
        except (URLError, TimeoutError, ValueError):
            return None
        except Exception:
            logger.exception("UI-etat: erreur en récupérant le contexte lobby pour joueur=%s", joueur_id)
            return None

    def _traiter_evenement_lobby(self, topic: str, enveloppe: dict) -> None:
        # Supporter les deux formats:
        # - ancien: { "type": "...", "payload": {...} }
        # - nouveau: { "event_type": "...", "data": {...} }
        type_evt = (enveloppe.get("event_type") or enveloppe.get("type") or "").strip()
        payload = (enveloppe.get("data") or enveloppe.get("payload") or {}) or {}

        def est(evt: str) -> bool:
            # tolérer différentes conventions de nommage
            if type_evt == evt:
                return True
            return type_evt.endswith("." + evt) or type_evt.endswith("." + evt.lower()) or type_evt == evt.lower()

        if est("JoueurConnecte") or est("joueur.connecte"):
            joueur_id = payload.get("joueur_id") or payload.get("id_joueur")
            if joueur_id:
                self._depot.obtenir_ou_creer(joueur_id)
                # IMPORTANT: après un redémarrage, il peut ne pas y avoir de JoueurARejointTable.
                # On réconcilie donc l'ancrage via le contexte persistant du lobby.
                ctx = self._recuperer_contexte_reprise(joueur_id)
                if ctx:
                    id_partie = ctx.get("id_partie")
                    id_table = ctx.get("id_table")
                    if id_partie:
                        self._depot.ancrer_joueur_partie(joueur_id, id_partie)
                    elif id_table:
                        self._depot.ancrer_joueur_table(joueur_id, id_table)
                    else:
                        self._depot.ancrer_joueur_lobby(joueur_id)

        elif est("JoueurARejointTable") or est("joueur.rejoint_table"):
            joueur_id = payload.get("joueur_id") or payload.get("id_joueur")
            table_id = payload.get("table_id") or payload.get("id_table")
            if joueur_id and table_id:
                self._depot.ancrer_joueur_table(joueur_id, table_id)

        else:
            logger.debug(
                "Événement lobby ignoré: topic=%s type=%s payload=%s",
                topic,
                type_evt,
                payload,
            )

    def _mettre_a_jour_fin_partie(self, enveloppe: dict) -> None:
        event_type: str = enveloppe.get("event_type", "")
        op_code: str = enveloppe.get("op_code", "")
        aggregate_id: str = enveloppe.get("aggregate_id")
        data: dict = enveloppe.get("data") or {}

        # on ne garde que les op du moteur liées à l'agrégat "partie"
        if not event_type.startswith("cab.D600.partie."):
            return

        partie_id = aggregate_id
        if not partie_id:
            return

        occurred_at = enveloppe.get("occurred_at")
        if isinstance(occurred_at, str):
            # adapter au format réel (ISO, etc.)
            try:
                occurred_at = datetime.fromisoformat(occurred_at)
                if occurred_at.tzinfo is None or occurred_at.tzinfo.utcoffset(occurred_at) is None:
                    occurred_at = occurred_at.replace(tzinfo=timezone.utc)
            except Exception:
                occurred_at = None
        if occurred_at is None:
            occurred_at = datetime.now(timezone.utc)

        # 1) fin de partie : on initialise l'état de suivi
        if op_code == "partie.terminer":
            joueurs_ids = [
                jid for jid, _ in self._depot.joueurs_par_partie(partie_id)
            ]
            etat_fin = EtatFinPartie(
                partie_id=partie_id,
                terminee_at=occurred_at,
                joueurs_participants=set(joueurs_ids),
            )
            self._fin_parties[partie_id] = etat_fin
            logger.info(
                "Partie %s terminée à %s (joueurs=%s)",
                partie_id,
                etat_fin.terminee_at,
                etat_fin.joueurs_participants,
            )

        # 2) un joueur quitte explicitement
        elif op_code == "partie.joueur_quitte_definitivement":
            joueur_id = data.get("joueur_id")
            if not joueur_id:
                return
            etat_fin = self._fin_parties.get(partie_id)
            if etat_fin is None:
                # sécurité : on initialise si on ne l'avait pas encore vue comme terminée
                etat_fin = EtatFinPartie(
                    partie_id=partie_id,
                    terminee_at=occurred_at,
                )
                self._fin_parties[partie_id] = etat_fin
            etat_fin.joueurs_quittes.add(joueur_id)
            # UX : dès qu’un joueur quitte, on le renvoie immédiatement au lobby.
            # La fermeture globale de la partie (2 minutes / tous les joueurs) reste gérée
            # par la boucle _boucle_fermeture, mais le joueur n’attend plus.
            self._depot.ancrer_joueur_lobby(joueur_id)
            self._depot.vider_actions_pour_joueur(joueur_id)

            # journal côté "partie" (API du dépôt)
            self._depot.ajouter_entree_journal_partie(
                partie_id=partie_id,
                message="Joueur quitte la partie (retour au lobby).",
                event_id=enveloppe.get("event_id"),
                occurred_at=occurred_at,
                op_code=op_code,
                raw=enveloppe,
            )

            logger.info(
                "Joueur %s quitte définitivement la partie %s",
                joueur_id,
                partie_id,
            )

    def _fermer_partie_definitivement(self, partie_id: str) -> None:
        """
        Appliqué quand le délai est dépassé ou que tous les joueurs ont quitté.

        Ici on s'occupe seulement de la projection UI :
        - les joueurs ne sont plus ancrés sur la partie,
        - leurs actions sont effacées,
        - un message est ajouté dans le journal.
        """
        logger.info("Fermeture définitive de la partie %s côté UI", partie_id)

        # renvoyer les joueurs au lobby + vider leurs actions
        for jid, _ in self._depot.joueurs_par_partie(partie_id):
            self._depot.ancrer_joueur_lobby(jid)
            self._depot.vider_actions_pour_joueur(jid)

        # message commun à tous les joueurs de cette partie
        self._depot.ajouter_entree_journal_partie(
            partie_id=partie_id,
            message=f"La partie {partie_id} est archivée. Retour au lobby.",
        )

    def _boucle_fermeture(self) -> None:
        """
        Boucle périodique qui vérifie les parties terminées et applique la
        logique '2 minutes' ou 'tous les joueurs ont quitté'.
        """
        import time

        while True:
            try:
                now = datetime.now(timezone.utc)
                a_archiver: List[str] = []
                for partie_id, etat_fin in list(self._fin_parties.items()):
                    if etat_fin.est_delai_depasse(now) or etat_fin.tous_joueurs_ont_quitte():
                        a_archiver.append(partie_id)

                for partie_id in a_archiver:
                    self._fermer_partie_definitivement(partie_id)
                    self._fin_parties.pop(partie_id, None)

            except Exception:
                logger.exception("Erreur dans la boucle de fermeture des parties UI")

            time.sleep(5)  # à ajuster si tu veux plus ou moins de réactivité

