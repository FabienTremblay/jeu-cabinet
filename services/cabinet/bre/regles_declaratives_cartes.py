from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

from ..moteur.regles_interfaces import Command


@dataclass(frozen=True)
class ResultatValidationCarte:
    ok: bool
    cmd_cout: List[Command]
    raisons: List[str]


class ReglesDeclarativesCartes:
    """
    Mini-interpréteur YAML pour la validation de cartes.

    Périmètre volontairement limité à BRE T23 :
    - sélection d'une règle par op ;
    - chemins simples de type joueur.attention_dispo ou carte.cout_cp ;
    - opérateur >= ;
    - production de commandes delta.
    """

    def __init__(self, donnees: Dict[str, Any]) -> None:
        self.donnees = donnees
        self.regles = list(donnees.get("validation_cartes", []) or [])

    @classmethod
    def depuis_fichier(cls, chemin: str | Path) -> "ReglesDeclarativesCartes":
        with Path(chemin).open("r", encoding="utf-8") as fh:
            donnees = yaml.safe_load(fh) or {}
        if not isinstance(donnees, dict):
            raise ValueError("Le fichier de règles déclaratives doit contenir un objet YAML")
        return cls(donnees)

    def valider(self, *, etat_min: Dict[str, Any], cmd: Command) -> Optional[ResultatValidationCarte]:
        op = cmd.get("op")
        regle = self._regle_pour_op(op)
        if regle is None:
            return None

        joueur_id = cmd.get("joueur_id")
        carte_id = cmd.get("carte_id")
        joueurs = etat_min.get("joueurs", {}) or {}
        cartes_def = etat_min.get("cartes_def", {}) or {}
        joueur = joueurs.get(joueur_id)
        carte = cartes_def.get(carte_id)

        if not isinstance(joueur, dict):
            return ResultatValidationCarte(False, [], ["joueur_introuvable"])
        if carte_id not in list(joueur.get("main", []) or []):
            return ResultatValidationCarte(False, [], ["carte_absente_main"])
        if not isinstance(carte, dict):
            return ResultatValidationCarte(False, [], ["carte_introuvable"])

        contexte = {"joueur": joueur, "carte": carte, "cmd": cmd}
        for condition in regle.get("conditions", []) or []:
            if not self._condition_respectee(condition, contexte):
                return ResultatValidationCarte(
                    False,
                    [],
                    [self._raison_condition(condition)],
                )

        return ResultatValidationCarte(
            True,
            self._commandes_cout(regle, contexte, str(joueur_id)),
            [],
        )

    def _regle_pour_op(self, op: Any) -> Optional[Dict[str, Any]]:
        for regle in self.regles:
            if isinstance(regle, dict) and regle.get("op") == op:
                return regle
        return None

    def _condition_respectee(self, condition: Dict[str, Any], contexte: Dict[str, Any]) -> bool:
        operateur = condition.get("operateur")
        gauche = self._evaluer(condition.get("champ"), contexte)
        droite = self._evaluer(condition.get("valeur"), contexte)

        if operateur == ">=":
            return self._nombre(gauche) >= self._nombre(droite)

        raise ValueError(f"Opérateur non supporté dans les règles déclaratives: {operateur}")

    def _commandes_cout(
        self,
        regle: Dict[str, Any],
        contexte: Dict[str, Any],
        joueur_id: str,
    ) -> List[Command]:
        commandes: List[Command] = []
        for cout in regle.get("cout", []) or []:
            if not isinstance(cout, dict):
                continue
            delta = self._evaluer(cout.get("delta"), contexte)
            if self._nombre(delta) == 0:
                continue
            commandes.append(
                {
                    "op": str(cout.get("op")),
                    "joueur_id": joueur_id,
                    "delta": self._nombre(delta),
                }
            )
        return commandes

    def _evaluer(self, expression: Any, contexte: Dict[str, Any]) -> Any:
        if not isinstance(expression, str):
            return expression

        if expression.startswith("-"):
            return -self._nombre(self._evaluer(expression[1:], contexte))

        morceaux = expression.split(".")
        if morceaux[0] not in contexte:
            return expression

        valeur: Any = contexte[morceaux[0]]
        for morceau in morceaux[1:]:
            if isinstance(valeur, dict):
                valeur = valeur.get(morceau)
            else:
                valeur = getattr(valeur, morceau, None)
        return valeur

    def _nombre(self, valeur: Any) -> int:
        if valeur is None:
            return 0
        return int(valeur)

    def _raison_condition(self, condition: Dict[str, Any]) -> str:
        champ = condition.get("champ")
        if champ == "joueur.attention_dispo":
            return "attention_insuffisante"
        if champ == "joueur.capital_politique":
            return "capital_politique_insuffisant"
        return "condition_non_respectee"
