from __future__ import annotations

import os
from pathlib import Path
from typing import Any, List

from ...bre.regles_bre_proxy import ReglesBreProxy
from ...moteur.regles_interfaces import Command, ReglesInterface


class _ReglesPythonInterdites(ReglesInterface):
    """Fallback volontairement interdit : les règles attendues viennent du BRE."""

    def regle_sous_phase(self, etat: Any, signal: str) -> List[Command]:
        raise RuntimeError("skin mandat_fragile cassé: fallback Python interdit")

    def regle_attente_terminee(self, etat: Any, type_attente: str) -> List[Command]:
        raise RuntimeError("skin mandat_fragile cassé: fallback Python interdit")

    def valider_usage_carte(self, etat: Any, cmd: Command) -> tuple[bool, List[Command]]:
        raise RuntimeError("skin mandat_fragile cassé: fallback Python interdit")


def get_regles() -> ReglesInterface:
    rules_url = os.getenv("CAB_RULES_BRE_URL", "").strip() or "http://rules-service:8081"
    version = os.getenv("CAB_RULES_VERSION", "").strip() or "v1"
    timeout_s = float(os.getenv("CAB_RULES_TIMEOUT_S", "2.0"))
    validation_cartes_path = (
        Path(__file__).parent / "regles" / "validation_cartes.yaml"
    )

    return ReglesBreProxy(
        fallback=_ReglesPythonInterdites(),
        rules_url=rules_url,
        skin="mandat_fragile",
        version_regles=version,
        timeout_s=timeout_s,
        validation_cartes_path=str(validation_cartes_path),
        fallback_sur_erreur=False,
    )
