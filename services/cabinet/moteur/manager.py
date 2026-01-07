# services/cabinet/moteur/manager.py
from __future__ import annotations
from threading import RLock
from typing import Dict, Optional, List, Any
from .etat import Etat, ProgrammeTour, EntreeProgramme, Command
from .config_loader import construire_etat
from .events import EvenementDomaine, make_evt_from_op


class PartieManager:
    """Gère plusieurs parties en parallèle en mémoire."""
    def __init__(self) -> None:
        self._lock = RLock()
        self._parties: Dict[str, Etat] = {}

    def creer(self, skin: str, partie_id: str, joueurs: Dict[str, Any], seed: int | None = None) -> Etat:
        with self._lock:
            if partie_id in self._parties:
                raise ValueError(f"partie {partie_id} existe déjà")
            etat = construire_etat(skin, partie_id, joueurs, seed=seed)
            self._parties[partie_id] = etat
            return etat

    def get(self, partie_id: str) -> Etat:
        with self._lock:
            if partie_id in self._parties :
                return self._parties[partie_id]
            else :
                return None

    def liste(self) -> List[str]:
        with self._lock:
            return list(self._parties.keys())

    def demarrer_partie(self, partie_id: str) -> None:
        with self._lock:
            etat = self._parties[partie_id]
            etat.demarrer_partie()

    def appliquer_action(
        self,
        partie_id: str,
        acteur: str,
        type_action: str,
        donnees: dict | None = None,
    ):
        donnees = donnees or {}

        with self._lock:
            etat = self._parties[partie_id]

            cmd = {"op": type_action, **donnees}
            etat.appliquer_commandes([cmd])

            # Événement de domaine pour cette op si elle est mappée
            try:
                evt = make_evt_from_op(partie_id, type_action, cmd)
            except ValueError:
                # op non mappée → éventuellement un evt "journal" ou équivalent
                evt = make_evt_from_op(
                    partie_id,
                    "journal",
                    {"op": type_action, **donnees},
                )

            return etat, evt

    def terminer(self, partie_id: str, raison: str = "terminee") -> None:
        with self._lock:
            etat = self._parties.get(partie_id)
            if etat:
                etat.termine = True
                etat.raison_fin = raison
                etat.phase = "fin_jeu"


