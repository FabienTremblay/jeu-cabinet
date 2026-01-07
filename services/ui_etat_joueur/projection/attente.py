# services/ui_etat_joueur/projection/attente.py
from __future__ import annotations

from typing import List

from .utils import parse_occurred_at, audience_depuis_recipients
from ..domaine import ActionDisponible


def _construire_actions_depuis_procedure(data: dict) -> List[ActionDisponible]:
    """
    Construit les ActionDisponible à partir de data["procedure"]["ui"]["actions"].
    """
    procedure = data.get("procedure") or {}
    ui_cfg = (procedure.get("ui") or {})
    actions_cfg = ui_cfg.get("actions") or []

    type_attente = data.get("type") or data.get("type_attente")
    procedure_code = procedure.get("code")
    procedure_titre = procedure.get("titre")
    procedure_description = procedure.get("description")
    ecran = ui_cfg.get("ecran")

    actions: List[ActionDisponible] = []

    for a in actions_cfg:
        op = a.get("op", "")
        label = a.get("label") or op
        fields = a.get("fields") or []

        # On garde dans payload tout ce dont l’UI a besoin pour construire le formulaire
        payload = {
            "op": op,
            "fields": fields,
            "procedure_code": procedure_code,
            "procedure_titre": procedure_titre,
            "procedure_description": procedure_description,
            "type_attente": type_attente,
            "ecran": ecran,
        }

        actions.append(
            ActionDisponible(
                code=op,  # identifiant stable côté UI
                label=label,
                payload=payload,
                requires_confirmation=a.get("requires_confirmation", False),
            )
        )

    return actions


def _construire_actions_depuis_data_ui(data: dict) -> List[ActionDisponible]:
    """
    Version plus simple pour l’ancien format data["ui"]["actions"].
    Gardée pour compat éventuelle.
    """
    actions_ui = (data.get("ui") or {}).get("actions") or []
    type_attente = data.get("type") or data.get("type_attente")

    actions: List[ActionDisponible] = []

    for a in actions_ui:
        code = a.get("code", "")
        label = a.get("label", code)
        payload = a.get("payload") or {}
        # On ajoute le type d'attente dans le payload pour contexte
        payload.setdefault("type_attente", type_attente)

        actions.append(
            ActionDisponible(
                code=code,
                label=label,
                payload=payload,
                requires_confirmation=a.get("requires_confirmation", False),
            )
        )

    return actions


def traiter_attente(depot, evt: dict) -> None:
    aggregate_id = evt.get("aggregate_id")
    data = evt.get("data", {}) or {}
    recipients = evt.get("recipients", ["ALL"])
    audience = audience_depuis_recipients(recipients)

    op_code = evt.get("op_code") or data.get("op") or ""
    when = parse_occurred_at(evt.get("occurred_at"))

    # ------------------------------------------------------------------
    # 1) DÉBUT D’ATTENTE : cab.D600.attente.joueurs / attente.init
    # ------------------------------------------------------------------
    if op_code in {"attente.joueurs", "attente.init"}:
        joueurs = data.get("joueurs") or []
        type_attente = data.get("type_attente") or data.get("type")

        # Construction des actions depuis la procédure (nouveau format)
        actions: List[ActionDisponible] = []
        if data.get("procedure"):
            actions = _construire_actions_depuis_procedure(data)
        else:
            # fallback sur ancien format data["ui"]["actions"]
            actions = _construire_actions_depuis_data_ui(data)

        # Affecter les actions aux joueurs concernés
        for jid in joueurs:
            depot.definir_actions_pour_joueur(jid, actions)

        # Marqueur "actions" : intervention requise
        if joueurs:
            depot.maj_marqueur_actions_pour_joueurs(joueurs, when)
        elif aggregate_id:
            depot.maj_marqueur_actions_par_partie(aggregate_id, when)

        # Message pour le journal
        procedure = data.get("procedure") or {}
        titre = procedure.get("titre")
        message = data.get("ui_message")
        if not message:
            if titre:
                message = f"Une décision est attendue : {titre}"
            else:
                message = f"Une décision est attendue ({type_attente})."

        # Événement fort : journal pour les joueurs ciblés
        if joueurs:
            for jid in joueurs:
                depot.ajouter_entree_journal(
                    joueur_id=jid,
                    message=message,
                    event_id=evt.get("event_id"),
                    occurred_at=when,
                    category="ACTION",
                    severity="info",
                    code="action.attente.ouverte",
                    meta={
                        "aggregate_id": aggregate_id,
                        "op_family": evt.get("op_family"),
                        "op_code": op_code,
                        "type_attente": type_attente,
                        "joueurs": joueurs,
                        "procedure_code": (data.get("procedure") or {}).get("code"),
                        "procedure_titre": (data.get("procedure") or {}).get("titre"),
                        "ecran": ((data.get("procedure") or {}).get("ui") or {}).get("ecran"),
                    },
                    audience={"scope": "joueur", "joueur_id": jid},
                    op_code=op_code,
                    raw=evt,
                )
        else:
            depot.journal_par_recipients(
                aggregate_id=aggregate_id,
                recipients=recipients,
                message=message,
                event_id=evt.get("event_id"),
                occurred_at=when,
                category="ACTION",
                severity="info",
                code="action.attente.ouverte",
                meta={
                    "aggregate_id": aggregate_id,
                    "op_family": evt.get("op_family"),
                    "op_code": op_code,
                    "type_attente": type_attente,
                    "procedure_code": (data.get("procedure") or {}).get("code"),
                    "procedure_titre": (data.get("procedure") or {}).get("titre"),
                    "ecran": ((data.get("procedure") or {}).get("ui") or {}).get("ecran"),
                },
                audience=audience,
                op_code=op_code,
                raw=evt,
            )

    # ------------------------------------------------------------------
    # 2) ACK D’UN JOUEUR : attente.recu
    # ------------------------------------------------------------------
    elif op_code == "attente.joueur_recu" or op_code == "attente.recu":
        joueur_id = data.get("joueur_id")
        if joueur_id:
            type_attente = data.get("type_attente") or data.get("type")
            depot.ajouter_entree_journal(
                joueur_id=joueur_id,
                message="Votre réponse a été reçue.",
                event_id=evt.get("event_id"),
                occurred_at=when,
                category="ACTION",
                severity="info",
                code="action.attente.recue",
                meta={
                    "aggregate_id": aggregate_id,
                    "op_family": evt.get("op_family"),
                    "op_code": op_code,
                    "type_attente": type_attente,
                },
                audience={"scope": "joueur", "joueur_id": joueur_id},
                op_code=op_code,
                raw=evt,
            )

    # ------------------------------------------------------------------
    # 3) FIN D’ATTENTE : attente.terminer
    # ------------------------------------------------------------------
    elif op_code == "attente.terminer":
        joueurs = data.get("joueurs") or []

        if joueurs:
            depot.vider_actions_pour_joueurs(joueurs)
            depot.maj_marqueur_actions_pour_joueurs(joueurs, when)
        elif aggregate_id:
            joueurs_ids = [jid for jid, _ in depot.joueurs_par_partie(aggregate_id)]
            depot.vider_actions_pour_joueurs(joueurs_ids)
            depot.maj_marqueur_actions_par_partie(aggregate_id, when)

        message = data.get("ui_message") or "L'attente est terminée."
        depot.journal_par_recipients(
            aggregate_id=aggregate_id,
            recipients=recipients if recipients else ["ALL"],
            message=message,
            event_id=evt.get("event_id"),
            occurred_at=when,
            category="ACTION",
            severity="info",
            code="action.attente.terminee",
            meta={
                "aggregate_id": aggregate_id,
                "op_family": evt.get("op_family"),
                "op_code": op_code,
                "joueurs": joueurs,
            },
            audience=audience,
            op_code=op_code,
            raw=evt,
        )

