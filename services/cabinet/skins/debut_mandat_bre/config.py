# services/cabinet/skins/debut_mandat_bre/config.py
from __future__ import annotations

import copy

from ..debut_mandat.config import SKIN_CONFIG as SKIN_CONFIG_PYTHON


# on repart d'un skin testé, mais on le considère comme une "réalisation BRE"
SKIN_CONFIG = copy.deepcopy(SKIN_CONFIG_PYTHON)
SKIN_CONFIG["id"] = "debut_mandat_bre"
SKIN_CONFIG["nom"] = "Conseil des ministres – Début de mandat (BRE)"
SKIN_CONFIG["description"] = (
    "Variante du skin debut_mandat, dont les règles sont évaluées par le rules-service (BRE)."
)

# déclaration locale au skin (pas de variable globale CAB_RULES_VERSION)
SKIN_CONFIG["moteur_regles"] = {
    "type": "bre",
    "version_regles": "debut_mandat_bre.v1",
}
