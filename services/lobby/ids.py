# services/lobby/ids.py
from __future__ import annotations

import uuid
from dataclasses import dataclass


@dataclass(frozen=True)
class GenerateurIds:
    """
    Génère des ids d'agrégats (joueur/table/partie).

    - mode sequentiel : utilisé par les dépôts mémoire (préserve les essais)
    - mode uuid : ids robustes, non collisionnels (recommandé en prod)
    """
    mode: str = "sequentiel"

    def id_joueur(self, numero: int | None = None) -> str:
        return self._id("J", numero)

    def id_table(self, numero: int | None = None) -> str:
        return self._id("T", numero)

    def id_partie(self, numero: int | None = None) -> str:
        return self._id("P", numero)

    def _id(self, prefixe: str, numero: int | None) -> str:
        mode = (self.mode or "sequentiel").lower().strip()
        if mode == "sequentiel":
            if numero is None:
                raise ValueError("numero requis en mode sequentiel")
            return f"{prefixe}{numero:06d}"
        if mode == "uuid":
            return f"{prefixe}{uuid.uuid4().hex}"
        raise ValueError(f"id_mode_invalide: {self.mode}")
