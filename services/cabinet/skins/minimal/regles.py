# services/cabinet/skins/minimal/regles.py

from __future__ import annotations
from typing import List, Dict, Any, Iterable

from ...moteur.regles_interfaces import ReglesInterface, Command
from ...moteur.etat import Etat


class ReglesMinimal(ReglesInterface):
    """
    Version embarquée des règles, équivalent de l'ancien `mock_decide`.

    Hypothèses :
      - Les événements 'monde' sont des IDs dans deck_events.pioche.
      - Si un event_id est présent dans cartes_def avec un champ 'effet',
        on applique ses delta_axes.
      - Le vote est pondéré par somme(signaux) déjà stockée
        dans etat.programme.votes (positif => passe; négatif/0 => amendements).
      - L’exécution applique les effets des cartes référencées par programme.entrees.
    """

    def regle_sous_phase(self, etat: Etat, signal: str) -> List[Command]:
        cmds: List[Command] = []
        # --- Détection de fin de partie : d’effondrement (crise globale) ---
        # si un axe dépasse son seuil → terminer la partie
        for axe in etat.axes.values():
            if axe.valeur <= axe.seuil_crise:
                return [{
                    "op": "partie.terminer",
                    "raison": f"crise_sur_{axe.id}",
                }]

        # --- Détection de fin de partie : Retour en élection ---
        tour_max = getattr(etat, "tour_max", None)
        if tour_max is not None and etat.tour > tour_max:
            return [{
                "op": "partie.terminer",
                "raison": "Retour en élection - fin de la partie",
            }]

        # --- Monde -----------------------------------------------------------
        if signal == "on_start_monde":
            # tirer un éventuel événement
            evt_id = etat.deck_events.prochain() if etat.deck_events else None
            if evt_id:
                # commandes de l'événement monde (issues du skin)
                cmds_evt = self._commandes_pour_carte(
                    etat,
                    evt_id,
                    auteur_id=None,
                    sous_phase="monde",
                )
                cmds.extend(cmds_evt)

                # journaliser l’événement
                cmds.append({
                    "op": "journal",
                    "type": "evt_monde",
                    "payload": {
                        "event_id": evt_id,
                        "commandes": cmds_evt,
                    },
                })
            else:
                cmds.append({
                    "op": "journal",
                    "type": "evt_monde_none",
                    "payload": {},
                })

            # --- distribution initiale des mains (une seule fois) ---
            main_voulue = etat.main_init
            for jid in etat.joueurs:
                cmds.append({
                    "op": "joueur.piocher",
                    "joueur_id": jid,
                    "nb": main_voulue,
                })
            cmds.append({
                "op": "journal",
                "type": "distribution_initiale",
                "payload": {"main_init": main_voulue},
            })
            # passer au conseil
            cmds.append({"op": "phase.set", "sous_phase": "conseil"})

        # --- Conseil ---------------------------------------------------------
        elif signal == "on_conseil":
            cmds.append({
                "op": "journal",
                "type": "conseil_ouvert",
                "payload": {},
            })
            # D600 : le BRE “réel” pourrait décider qui doit voter; ici : tous les joueurs
            cmds.append({
                "op": "attente.init",
                "type": "vote",
                "joueurs": list(etat.joueurs.keys()),
            })
            # on passe en phase vote
            cmds.append({"op": "phase.set", "sous_phase": "vote_programme"})


        # --- Vote ------------------------------------------------------------
        elif signal == "on_vote_programme":
            somme = 0
            if etat.programme and etat.programme.votes:
                for jid, v in etat.programme.votes.items():
                    j = etat.joueurs.get(jid)
                    if not j:
                        continue
                    if not getattr(j, "peut_voter", True):
                        continue
                    poids = getattr(j, "poids_vote", 1)
                    somme += int(v) * poids

            cmds.append({
                "op": "journal",
                "type": "vote_synthese",
                "payload": {"somme": somme},
            })

            if somme > 0:
                cmds.append({"op": "phase.set", "sous_phase": "execution_programme"})
            else:
                cmds.append({"op": "phase.set", "sous_phase": "amendements"})

        # --- Amendements -----------------------------------------------------
        elif signal == "on_amendements":
            # mock: un seul aller-retour d’amendements puis on revote
            cmds.append({
                "op": "journal",
                "type": "amendements_termine",
                "payload": {},
            })
            cmds.append({
                "op": "phase.set",
                "sous_phase": "vote_programme",
            })

        # --- Exécution du programme ------------------------------------------
        elif signal == "on_execution_programme":
            # Exécution séquentielle du programme :
            # on construit d'abord les commandes au niveau de l'État, puis on
            # les renvoie au moteur D001.
            if etat.programme:
                cmds_exec = self._regle_resolution_programme(etat)
                cmds.extend(cmds_exec)

                cmds.append({
                    "op": "journal",
                    "type": "programme_execute",
                    "payload": {
                        "nb_entrees": len(etat.programme.entrees),
                        "nb_commandes": len(cmds_exec),
                    },
                })

            # on enchaîne vers la cloture du tour
            cmds.append({
                "op": "phase.set",
                "sous_phase": "cloture_tour",
            })

        # --- Clôture du tour -------------------------------------------------
        elif signal == "on_cloture_tour":
            # clore un éventuel événement encore actif
            cmds.append({"op": "evt.clore"})

            # reset d’attention (si le champ existe sur Joueur)
            for jid, j in etat.joueurs.items():
                if hasattr(j, "attention_max") and hasattr(j, "attention_dispo"):
                    cmds.append({
                        "op": "joueur.reset_attention",
                        "joueur_id": jid,
                    })

            cmds.append({
                "op": "journal",
                "type": "cloture_tour",
                "payload": {},
            })
            cmds.append({"op": "tour.increment"})              # tour += 1
            cmds.append({"op": "phase.set", "sous_phase": "monde"})

        # --- Défaut ----------------------------------------------------------
        else:
            # signal inconnu: ne rien casser, juste journaliser
            cmds.append({
                "op": "journal",
                "type": "signal_inconnu",
                "payload": {"signal": signal},
            })

        return cmds


    def _regle_resolution_programme(self, etat: Etat) -> List[Command]:
        cmds: List[Command] = []

        # --- cas trivial : aucun programme ---
        if etat.programme is None or not etat.programme.entrees:
            cmds.append({
                "op": "journal",
                "type": "programme_vide",
                "payload": {"message": "Aucun programme à exécuter."},
            })
            cmds.append({"op": "phase.set", "sous_phase": "cloture_tour"})
            return cmds

        cmds.append({
            "op": "journal",
            "type": "programme_execution_debut",
            "payload": {
                "nb_cartes": len(etat.programme.entrees),
            },
        })

        contributions: Dict[str, int] = {}

        # ------------------------------------------------------------------
        # 1) exécuter les cartes du programme via le pipeline noyau
        # ------------------------------------------------------------------
        for entree in etat.programme.entrees:
            carte_id = entree.carte_id
            auteur_id = entree.auteur_id
            params = entree.params or {}

            # sécurité : carte inconnue
            if carte_id not in etat.cartes_def:
                cmds.append({
                    "op": "journal",
                    "type": "warning",
                    "payload": {
                        "message": f"Carte inconnue dans le programme: {carte_id}",
                        "auteur": auteur_id,
                    },
                })
                continue

            # pipeline noyau (identique à jouer_carte, sans coûts)
            commandes_carte = etat.preparer_commandes_carte(
                auteur_id,
                carte_id,
                **params,
            )
            cmds.extend(commandes_carte)

            # contribution politique
            contributions[auteur_id] = contributions.get(auteur_id, 0) + 1

        # ------------------------------------------------------------------
        # 2) capital politique individuel
        # ------------------------------------------------------------------
        total_cartes = 0
        for jid, nb in contributions.items():
            total_cartes += nb
            cmds.append({
                "op": "joueur.capital.delta",
                "joueur_id": jid,
                "delta": nb,
            })

        # ------------------------------------------------------------------
        # 3) capital collectif du cabinet
        # ------------------------------------------------------------------
        if total_cartes > 0:
            cmds.append({
                "op": "capital_collectif.delta",
                "delta": total_cartes,
            })

        # ------------------------------------------------------------------
        # 4) reset du programme (défausse + nettoyage)
        # ------------------------------------------------------------------
        cmds.append({"op": "programme.reset"})

        # ------------------------------------------------------------------
        # 5) synthèse
        # ------------------------------------------------------------------
        cmds.append({
            "op": "journal",
            "type": "programme_execution_fin",
            "payload": {
                "nb_cartes": total_cartes,
                "contributions": contributions,
            },
        })

        # ------------------------------------------------------------------
        # 6) enchaînement minimal
        # ------------------------------------------------------------------
        cmds.append({"op": "phase.set", "sous_phase": "cloture_tour"})
        return cmds

    def _commandes_pour_carte(
        self,
        etat: Etat,
        carte_id: str,
        auteur_id: str | None = None,
        sous_phase: str | None = None,
    ) -> List[Command]:
        """
        Construit la liste de commandes D001 pour une carte donnée,
        à partir du skin (champ 'commandes') avec fallback sur l'ancien
        champ 'effet.delta_axes' si nécessaire.
        """
        defn: Dict[str, Any] = etat.cartes_def.get(carte_id, {})
        base_cmds = defn.get("commandes")

        if base_cmds is None:
            # Fallback legacy: effet.delta_axes -> axes.delta
            effet = defn.get("effet", {})
            delta_axes = effet.get("delta_axes", {})
            base_cmds = [
                {
                    "op": "axes.delta",
                    "axe": axe,
                    "delta": int(delta),
                }
                for axe, delta in delta_axes.items()
            ]

        result: List[Command] = []
        for c in base_cmds:
            cmd: Command = dict(c)  # shallow copy
            # enrichissement contextuel
            cmd.setdefault("carte_id", carte_id)
            if auteur_id is not None:
                cmd.setdefault("joueur_id", auteur_id)
            if sous_phase is not None:
                cmd.setdefault("sous_phase", sous_phase)
            result.append(cmd)

        return result


# instance unique utilisée comme fallback pour les skins
regles_minimal = ReglesMinimal()

def get_regles():
    """Retourne l'implémentation des règles pour le skin minimal."""
    return regles_minimal
