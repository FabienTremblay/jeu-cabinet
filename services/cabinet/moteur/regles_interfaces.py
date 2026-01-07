# services/cabinet/moteur/regles_interfaces.py
from __future__ import annotations

from typing import List, Dict, Any, Protocol, TYPE_CHECKING

if TYPE_CHECKING:
    # import uniquement pour le type-checking, pas à l'exécution
    from ..moteur.etat import Etat

Command = Dict[str, Any]


class ReglesInterface(Protocol):
    """interface commune de tous les moteurs de règles (mock ou vrai bre)."""

    def regle_sous_phase(self, etat: "Etat", signal: str) -> List[Command]:
        """CAB.B103 – règle de sous-phase (monde / cabinet / vote / ...)."""
        raise NotImplementedError

    def regle_attente_terminee(self, etat: "Etat", type_attente: str) -> List[Command]:
        """
        appelée quand une attente (attente.type) est complétée.
        le type d'attente (ex: 'ENGAGER_CARTE', 'VOTE', ...) permet de décider
        quelles commandes enchaîner (ouverture vote, résolution, etc.).
        """
        return []

    def valider_usage_carte(self, etat: "Etat", cmd: Command) -> tuple[bool, List[Command]]:
        """
        CAB.D510 – Validation de l'usage d'une carte.

        cmd contient au minimum:
          - "op"
          - "joueur_id"
          - "carte_id"

        Retourne:
          - ok: True si la carte peut être utilisée dans le contexte courant.
          - commandes_cout: commandes à appliquer pour payer le coût
            (capital politique, points d'attention, etc.) AVANT l'effet.
        """
        return True, []

    def valider_usage_carte(self, etat: "Etat", cmd: Command) -> tuple[bool, List[Command]]:
        """
        CAB.D510 – Validation de l'usage d'une carte.

        cmd contient au minimum:
          - "op"
          - "joueur_id"
          - "carte_id"

        Retourne:
          - ok: True si la carte peut être utilisée dans le contexte courant.
          - commandes_cout: commandes à appliquer pour payer le coût
            (capital politique, points d'attention, etc.) AVANT l'effet.
        """
        return True, []


