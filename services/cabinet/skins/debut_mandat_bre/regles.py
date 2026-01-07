# services/cabinet/skins/debut_mandat_bre/regles.py
from __future__ import annotations

import os
from typing import Any, List

from ...bre.regles_bre_proxy import ReglesBreProxy
from ...moteur.regles_interfaces import ReglesInterface, Command


class _ReglesPythonInterdites(ReglesInterface):
    """Fallback volontairement interdit : si on arrive ici, le skin est cassé."""

    def regle_sous_phase(self, etat: Any, signal: str) -> List[Command]:
        raise RuntimeError(
            "skin debut_mandat_bre cassé: fallback Python interdit (règles attendues du BRE)"
        )

    def regle_attente_terminee(self, etat: Any, type_attente: str) -> List[Command]:
        raise RuntimeError(
            "skin debut_mandat_bre cassé: fallback Python interdit (règles attendues du BRE)"
        )

    def valider_usage_carte(self, etat: Any, cmd: Command) -> tuple[bool, List[Command]]:
        raise RuntimeError(
            "skin debut_mandat_bre cassé: fallback Python interdit (règles attendues du BRE)"
        )


def get_regles() -> ReglesInterface:
    """
    Règles du skin via rules-service (BRE).

    Variables attendues :
      - CAB_RULES_BRE_URL (ex: http://rules-service:8081)
      - CAB_RULES_VERSION (ex: debut_mandat_bre.v1) [optionnel]
      - CAB_RULES_TIMEOUT_S [optionnel]
    """
    rules_url = os.getenv("CAB_RULES_BRE_URL", "").strip() or "http://rules-service:8081"
    version = os.getenv("CAB_RULES_VERSION", "").strip() or "debut_mandat_bre.v1"
    timeout_s = float(os.getenv("CAB_RULES_TIMEOUT_S", "2.0"))

    return ReglesBreProxy(
        fallback=_ReglesPythonInterdites(),
        rules_url=rules_url,
        skin="debut_mandat_bre",
        version_regles=version,
        timeout_s=timeout_s,
        fallback_sur_erreur=False,
    )
