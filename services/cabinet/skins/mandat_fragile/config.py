from __future__ import annotations

import copy

from ..debut_mandat_bre.config import SKIN_CONFIG as SKIN_CONFIG_BRE


SKIN_CONFIG = copy.deepcopy(SKIN_CONFIG_BRE)
SKIN_CONFIG["id"] = "mandat_fragile"
SKIN_CONFIG["nom"] = "Conseil des ministres - Mandat fragile"
SKIN_CONFIG["description"] = (
    "Skin dérivée de debut_mandat_bre démontrant des règles plus strictes "
    "par configuration déclarative."
)

# Gouvernement plus instable : moins de marge politique au départ.
SKIN_CONFIG["capital_init"] = max(0, int(SKIN_CONFIG.get("capital_init", 0)) - 2)
SKIN_CONFIG["capital_opposition_init"] = int(SKIN_CONFIG.get("capital_opposition_init", 0)) + 1
SKIN_CONFIG["moteur_regles"] = {
    "type": "bre",
    "version_regles": "v1",
}
