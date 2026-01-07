# services/cabinet/moteur/events.py
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Literal, Mapping, Dict, List

# Familles d'opérations (groupes D100–D600)
OpFamily = Literal["D100", "D200", "D300", "D400", "D500", "D600", "D700"]

# Catégories d'agrégats / vues pour la consommation
Category = Literal["AXES", "JOUEUR", "DECK", "MONDE", "PROGRAMME", "DEROULEMENT", "ANALYSE"]


# Matrice de déduction (op_code -> (famille, catégorie))
OP_MATRIX: Dict[str, tuple[OpFamily, Category]] = {
    # D100 – Axes, économie
    "axes.": ("D100", "AXES"),
    "eco.": ("D100", "AXES"),

    # D200 – Joueurs (capital, attention, main, vote)
    "joueur.": ("D200", "JOUEUR"),

    # D300 – Decks / échanges
    "deck.": ("D300", "DECK"),

    # D400 – Événements mondiaux
    "evt.": ("D400", "MONDE"),

    # D500 – Programme
    "programme.": ("D500", "PROGRAMME"),

    # D600 – Déroulement / attentes / notifications / journal
    "phase.": ("D600", "DEROULEMENT"),
    "tour.": ("D600", "DEROULEMENT"),
    "partie.": ("D600", "DEROULEMENT"),
    "attente.": ("D600", "DEROULEMENT"),
    "notif.": ("D600", "DEROULEMENT"),
    "journal": ("D600", "DEROULEMENT"),

    # D700 – Analyse du jeu (cabinet vs opposition)
    "capital_collectif.": ("D700", "ANALYSE"),
    "analyse.": ("D700", "ANALYSE"),
    "opposition.": ("D700", "ANALYSE"),
}



@dataclass
class EvenementDomaine:
    """
    Événement de domaine produit par le moteur.

    Il est agnostique de Kafka : l'adapter (api_moteur) se charge de
    le transformer en message pour cab.events.
    """
    event_type: str
    op_family: OpFamily
    op_code: str
    category: Category

    aggregate_type: str
    aggregate_id: str

    data: Dict[str, Any]
    metadata: Dict[str, Any] = field(default_factory=dict)

    # Hints UI / vigilance
    requires_action: bool = False
    recipients: List[str] = field(default_factory=lambda: ["ALL"])
    severity: str = "info"  # "info", "warning", "critical"

    # Processus CAB.* (optionnel)
    process_code: str | None = None
    process_instance_id: str | None = None

    # Horodatage interne (domaine)
    occurred_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )


def make_evt_from_op(
    partie_id: str,
    op_code: str,
    data: Dict[str, Any],
    *,
    requires_action: bool = False,
    recipients: List[str] | None = None,
    severity: str = "info",
    metadata: Mapping[str, Any] | None = None,
) -> EvenementDomaine:
    """
    Fabrique un EvenementDomaine à partir d'un op_code et de sa commande/data.

    - Déduit automatiquement:
      - op_family (D100–D600)
      - category (AXES / JOUEUR / DECK / MONDE / PROGRAMME / DEROULEMENT)
      - event_type = "cab.<op_family>.<op_code>"
    - data = commande brute (typiquement {"op": "...", ...})
    """

    # 1. Déduire famille + catégorie à partir du préfixe de op_code
    op_family: OpFamily | None = None
    category: Category | None = None

    for prefix, (fam, cat) in OP_MATRIX.items():
        if op_code.startswith(prefix):
            op_family = fam
            category = cat
            break

    if op_family is None or category is None:
        raise ValueError(f"Impossible de déduire la famille pour op_code={op_code!r}")

    # 2. Construire event_type automatiquement
    event_type = f"cab.{op_family}.{op_code}"

    return EvenementDomaine(
        event_type=event_type,
        op_family=op_family,
        op_code=op_code,
        category=category,
        aggregate_type="partie",
        aggregate_id=partie_id,
        data=data,
        metadata=dict(metadata or {}),
        recipients=recipients or ["ALL"],
        requires_action=requires_action,
        severity=severity,
    )

