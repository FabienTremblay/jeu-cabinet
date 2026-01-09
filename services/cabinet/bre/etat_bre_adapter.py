# source_fichier: services/cabinet/bre/etat_bre_adapter.py

 from __future__ import annotations
 
 from dataclasses import asdict
 from typing import Any, Dict
 
 
 class EtatBreAdapter:
     """
     Convertit l'état Python (Etat) en dictionnaire JSON stable pour le BRE.
     """
 
     def etat_vers_facts(self, etat: Any) -> Dict[str, Any]:
         attente = getattr(etat, "attente", None)
 
         return {
             "etat": {
                 "phase": getattr(etat, "phase", None),
                 "sous_phase": getattr(etat, "sous_phase", None),
                 "tour": getattr(etat, "tour", None),
                 "id_joueur_courant": getattr(etat, "id_joueur_courant", None),
                "joueurs": [
                    {
                        "id_joueur": j.id_joueur,
                        "role": getattr(j, "role", None),
                        "actif": getattr(j, "actif", None),
                        "pret": getattr(j, "pret", None),
                        # Champs attendus par certains DMN (valider_action, etc.)
                        "attention": getattr(j, "attention", None),
                        "capital_politique": getattr(j, "capital_politique", None),
                        "prestige": getattr(j, "prestige", None),
                    }
                    for j in etat.joueurs.values()
                ],
                 "attente": None
                 if not attente
                 else {
                     "statut": getattr(attente, "statut", None),
                     "type": getattr(attente, "type", None),
                     "joueurs": list(getattr(attente, "joueurs", []) or []),
                     "recus": list(getattr(attente, "recus", []) or []),
                     "meta": getattr(attente, "meta", None),
                 },
             }
         }

    @staticmethod
    def to_facts(etat: Any) -> Dict[str, Any]:
        """
        API stable utilisée par le proxy BRE.
        """
        return EtatBreAdapter().etat_vers_facts(etat)
