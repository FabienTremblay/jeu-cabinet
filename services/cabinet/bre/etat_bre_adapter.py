# source_fichier: services/cabinet/bre/etat_bre_adapter.py
from __future__ import annotations

from typing import Any, Dict


class EtatBreAdapter:
    """
    Convertit l'état Python (Etat) en dictionnaire JSON stable pour le BRE.
    """

    def etat_vers_facts(self, etat: Any) -> Dict[str, Any]:
        joueurs = getattr(etat, "joueurs", {}) or {}
        cartes_def = getattr(etat, "cartes_def", {}) or {}

        return {
            "phase": getattr(etat, "phase", None),
            "sous_phase": getattr(etat, "sous_phase", None),
            "tour": getattr(etat, "tour", None),
            "joueurs": {
                jid: self._joueur_vers_fact(j)
                for jid, j in joueurs.items()
            },
            "cartes_def": {
                cid: self._carte_vers_fact(cid, carte)
                for cid, carte in cartes_def.items()
            },
        }

    def _joueur_vers_fact(self, joueur: Any) -> Dict[str, Any]:
        return {
            "id": getattr(joueur, "id", None),
            "attention_dispo": getattr(joueur, "attention_dispo", None),
            "capital_politique": getattr(joueur, "capital_politique", None),
            "main": list(getattr(joueur, "main", []) or []),
        }

    def _carte_vers_fact(self, carte_id: str, carte: Any) -> Dict[str, Any]:
        if isinstance(carte, dict):
            return {
                "id": carte.get("id", carte_id),
                "type": carte.get("type"),
                "cout_attention": carte.get("cout_attention", 0),
                "cout_cp": carte.get("cout_cp", 0),
            }

        return {
            "id": getattr(carte, "id", carte_id),
            "type": getattr(carte, "type", None),
            "cout_attention": getattr(carte, "cout_attention", 0),
            "cout_cp": getattr(carte, "cout_cp", 0),
        }

    @staticmethod
    def to_facts(etat: Any) -> Dict[str, Any]:
        """
        API stable utilisée par le proxy BRE.
        """
        return EtatBreAdapter().etat_vers_facts(etat)
