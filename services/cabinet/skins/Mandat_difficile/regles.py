# services/cabinet/skins/debut_mandat/regles.py
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

from ...moteur.etat import Etat
from ...moteur.regles_interfaces import ReglesInterface

Command = Dict[str, Any]

# -----------------------------------------------------
#  Fabrique attendue par __init__.py : get_regles()
# -----------------------------------------------------
from .config import SKIN_CONFIG

def get_regles() -> ReglesInterface:
    return ReglesDebutMandat(config=SKIN_CONFIG)


# -----------------------------------------------------
#  Implémentation des règles du skin "début_mandat"
# -----------------------------------------------------

@dataclass
class MissionOpposition:
    id: str
    axe: Optional[str]          # "social", "economique", etc. ou None pour global
    intitule: str
    description: str
    priorite: int               # 1=haute, 2=moyenne, 3=basse
    critere_reussite: Dict[str, Any]  # ex: {"axe": "social", "min_valeur": 1}


@dataclass
class ResultatAnalysePartie:
    delta_cabinet: int
    delta_opposition: int
    missions_opposition: List[MissionOpposition]

@dataclass
class ReglesDebutMandat(ReglesInterface):

    config: Dict[str, Any]

    # =========================================================================
    #    1. REGLE PRINCIPALE : Gestion des signaux de phase
    # =========================================================================
    def regle_sous_phase(self, etat: Etat, signal: str) -> List[Command]:
        """
        "Router" principal : selon le signal émis par le moteur,
        on retourne une liste de Command.
        """

        if signal == "signal.init_tour":
            return self._regle_init_tour(etat)

        elif signal == "signal.evenement_mondial":
            return self._regle_evenement_mondial(etat)

        elif signal == "signal.programme_ouvert":
            return self._regle_programme_ouvert(etat)

        elif signal == "signal.vote_ouvert":
            return self._regle_ouverture_vote(etat)

        elif signal == "signal.perturbation_vote" :
            return self._regle_perturbation_vote(etat)

        elif signal == "signal.saison_tranquille":
            return self._regle_saison_tranquille(etat)

        elif signal == "signal.agitation":
            return self._regle_agitation(etat)

        elif signal == "signal.resolution_programme":
            return self._regle_resolution_programme(etat)

        elif signal == "signal.fin_tour":
            return self._regle_fin_tour(etat)

        # signal inconnu → aucune commande
        return []

    def determiner_sous_phase(self, etat : Etat) -> List[Command] :
        """
        """
        cmds: List[Command] = []
        if not etat.phase == "tour" :
            return cmds
        sous_phase = etat.sous_phase
        if sous_phase == "init_tour" :
            # Passer à la phase "EVENEMENT_MONDIAL"
            etat.sous_phase = "EVENEMENT_MONDIAL"
            cmds.extend(self._regle_evenement_mondial(etat))
        elif sous_phase == "EVENEMENT_MONDIAL" :
            # Enchaîner vers PHASE_PROGRAMME
            etat.sous_phase = "PHASE_PROGRAMME"
            cmds.extend(self._regle_programme_ouvert(etat))
        elif sous_phase in ["PHASE_PROGRAMME", "PHASE_VOTE", "PHASE_PERTURBATION_VOTE", "PHASE_TRANQUILLE"] :
            if etat.attente.est_active :
                # Initiative reviens dans les mains des joueurs
                pass;
            elif etat.attente.type == "ENGAGER_CARTE" :
                cmds.append({"op": "attente.terminer"})
                etat.sous_phase = "PHASE_VOTE"
                cmds.extend(self._regle_ouverture_vote(etat))
            elif etat.attente.type == "VOTE" :
                cmds.append({"op": "attente.terminer"})
                verdict = etat.programme.verdict
                if verdict :
                    # on passe à la phase de perturbation de vote.
                    etat.sous_phase = "PHASE_PERTURBATION_VOTE"
                    cmds.extend(self._regle_perturbation_vote(etat))
                else :
                    # On reprends la PHASE_PROGRAMME
                    etat.sous_phase = "PHASE_PROGRAMME"
                    cmds.extend(self._regle_programme_ouvert(etat))
            elif etat.attente.type == "PERTURBATION_VOTE":
                cmds.append({"op": "attente.terminer"})

                verdict = etat.programme.verdict
                if verdict or verdict is None :
                    # on passe à la phase de perturbation de vote.
                    etat.sous_phase = "PHASE_RESOLUTION"
                    cmds.extend(self._regle_resolution_programme(etat))
                else:
                    cmds.append({"op": "programme.rejeter"})
                    # On reprends la PHASE_PROGRAMME
                    etat.sous_phase = "PHASE_PROGRAMME"
                    cmds.extend(self._regle_programme_ouvert(etat))

            pass;
        elif sous_phase == "PHASE_RESOLUTION" :
            # Retourner directement vers FIN_TOUR
            etat.sous_phase = "FIN_TOUR"
            cmds.extend(self._regle_fin_tour(etat))
        elif sous_phase == "FIN_TOUR" :
            # Retourner directement vers init_tour
            etat.sous_phase = "init_tour"
            cmds.extend(self._regle_init_tour(etat))

        return cmds

    # =========================================================================
    #    2. RÈGLES PAR PHASE
    # =========================================================================

    # ---- init_tour ----------------------------------------------------------
    def _regle_init_tour(self, etat: Etat) -> List[Command]:
        cmds: List[Command] = []

        # Reset attention de tous les joueurs
        for jid in etat.joueurs.keys():
            cmds.append({
                "op": "joueur.reset_attention",
                "joueur_id": jid,
            })

            # Reset / nouvelle main (main_init dans la config)
            cmds.append({
                "op": "deck.defausser_main",
                "nb_nouvelle_main": self.config.get("main_init", 5),
                "joueur_id": jid,
            })

        cmds.append({
            "op": "journal",
            "payload": {"message": "Début du tour : remise des cartes et attention."},
        })

        cmds.extend(self.determiner_sous_phase(etat))
        return cmds

    # ---- EVENEMENT_MONDIAL --------------------------------------------------
    def _regle_evenement_mondial(self, etat: Etat) -> List[Command]:
        cmds: List[Command] = []

        # Piocher un événement
        cmds.append({ "op": "evt.piocher", "nombre": 2})

        # Piocher les joueurs
        for jid in etat.joueurs.keys():
            cmds.append({"op": "joueur.piocher", "joueur_id": jid, "nb" : self.config.get("main_init", 5)})

        # On peut mettre ici de l'analyse d’état lente ou générique :
        cmds.extend(self.analyse_etat(etat))

        cmds.append({
            "op": "programme.reset",
        })
        cmds.extend(self.determiner_sous_phase(etat))
        return cmds

    # ---- PHASE_PROGRAMME ----------------------------------------------------
    def _regle_programme_ouvert(self, etat: Etat) -> List[Command]:
        cmds: List[Command] = []

        # Ici, aucune automatisation : on attend que les joueurs engagent des cartes.
        # Donc on initialise une attente de tous les joueurs.
        cmds.append(self._attente_engager_cartes(etat))

        cmds.append({
            "op": "journal",
            "payload": {"message": "Programme ouvert : chaque joueur peut engager une carte."},
        })

        return cmds

    # ---- PHASE_VOTE ---------------------------------------------------------
    def _regle_ouverture_vote(self, etat: Etat) -> List[Command]:
        cmds: List[Command] = []

        # Seuls les joueurs avec assez de capital_politique peuvent voter
        joueurs_habiletes = []
        for jid in etat.joueurs.keys():
            if etat.joueurs[jid].capital_politique > 0 :
                joueurs_habiletes.append(jid)
                cmds.append({"op": "joueur.vote_droit.set", "joueur_id": jid, "peut_voter": True})
            else :
                cmds.append({"op": "joueur.vote_droit.set", "joueur_id": jid, "peut_voter": False})

        # Déclencher l'attente de vote
        cmds.append(self._attente_vote_programme(etat, joueurs_habiletes))

        cmds.append({
            "op": "journal",
            "payload": {"message": "Vote ouvert : chaque joueur doit voter."},
        })

        return cmds

    # ---- PHASE_RESOLUTION ---------------------------------------------------
    def _regle_resolution_programme(self, etat: Etat) -> List[Command]:
        cmds: List[Command] = []

        if etat.programme is None or not etat.programme.entrees:
            cmds.append({
                "op": "journal",
                "payload": {"message": "Aucun programme à résoudre."},
            })
            etat.sous_phase = "PHASE_PROGRAMME"
            cmds.extend(self._regle_programme_ouvert(etat))
            return cmds

        cmds.append({
            "op": "journal",
            "payload": {"message": "Résolution du programme en cours."},
        })

        contributions: Dict[str, int] = {}

        # 1) exécuter les cartes du programme
        for entree in etat.programme.entrees:
            carte_id = entree.carte_id

            # sécurité : carte inconnue côté noyau
            if carte_id not in etat.cartes_def:
                cmds.append({
                    "op": "journal",
                    "payload": {
                        "type": "warning",
                        "message": f"Carte inconnue dans le programme: {carte_id}",
                    },
                })
                continue

            # on réutilise EXACTEMENT le pipeline 'jouer immédiatement' pour les commandes
            commandes_carte = etat.preparer_commandes_carte(
                entree.auteur_id,
                carte_id,
                **(entree.params or {}),
            )
            cmds.extend(commandes_carte)

            # comptabiliser la contribution politique de l'auteur
            auteur = entree.auteur_id
            contributions[auteur] = contributions.get(auteur, 0) + 1

        # 2) attribuer le capital politique individuel pour les cartes passées
        total_cartes = 0
        for jid, nb in contributions.items():
            total_cartes += nb
            cmds.append({
                "op": "joueur.capital.delta",
                "joueur_id": jid,
                "delta": nb,
            })

        # 3) capital collectif au cabinet (exemple simple : 1 par carte)
        if total_cartes > 0:
            cmds.append({
                "op": "capital_collectif.delta",
                "delta": total_cartes,
            })

        # 4) défausser toutes les cartes du programme dans le deck global
        cmds.append({"op": "programme.reset"})

        # 5) journalisation de synthèse
        cmds.append({
            "op": "journal",
            "payload": {
                "message": "Programme exécuté.",
                "nb_cartes": total_cartes,
                "contributions": contributions,
            },
        })
        cmds.extend(self.determiner_sous_phase(etat))
        return cmds

    # ---- Phase tranquille ---------------------------------------------------
    def _regle_saison_tranquille(self, etat: Etat) -> List[Command]:
        cmds: List[Command] = []
        cmds.append({"op": "journal", "payload": {"message": "On sort du parlement pour faire chacun sa besogne avec ses fonctionnaires."}})

        return cmds

    # ---- FIN_TOUR -----------------------------------------------------------
    def _regle_fin_tour(self, etat: Etat) -> List[Command]:
        cmds: List[Command] = []

        cmds.append({"op": "journal", "payload": {"message": "Fin du tour."}})
        self.condition_fin_partie(etat);
        if not etat.termine :
            # Passer au tour suivant :
            cmds.append({"op": "tour.increment"})

            cmds.extend(self.determiner_sous_phase(etat))
        return cmds

    # =========================================================================
    #    4. PERTURBATIONS AU VOTE (procédures spéciales)
    # =========================================================================
    def _regle_perturbation_vote(self, etat: Etat) -> List[Command]:
        """
        Dans ce skin minimal : aucune procédure spéciale automatique.
        Cette méthode est prête pour recevoir des cartes du type 'procedure'.
        """
        cmds: List[Command] = []

        # Ici, aucune automatisation : on attend que les joueurs engagent des cartes.
        # Donc on initialise une attente de tous les joueurs.
        cmds.append(self._attente_perturbation_vote(etat))

        cmds.append({
            "op": "journal",
            "payload": {"message": "Perturbations de vote ?  Vous avez une mauvaise intention ?  Jouez une carte."},
        })
        return cmds

    # =========================================================================
    #    5. ANALYSE D'ÉTAT
    # =========================================================================
    def analyse_etat(self, etat: Etat) -> List[Command]:
        cmds: List[Command] = []

        # indicateurs précédents éventuellement mémorisés dans analyse_skin
        indicateurs_prec = etat.analyse_skin.get("indicateurs", {}) if etat.analyse_skin else {}

        # 1) lire les axes courants
        social = etat.axes["social"].valeur
        eco = etat.axes["economique"].valeur
        inst = etat.axes["institutionnel"].valeur
        env = etat.axes["environnement"].valeur

        # 2) calculer quelques agrégats simples
        score_axes = sum(a.valeur * a.poids for a in etat.axes.values())

        recettes_totales = sum(p.valeur for p in etat.eco.recettes.values())
        depenses_totales = sum(p.valeur for p in etat.eco.depenses.values())
        solde = recettes_totales - depenses_totales

        indicateurs = {
            "social": social,
            "economique": eco,
            "institutionnel": inst,
            "environnement": env,
            "score_axes": score_axes,
            "solde": solde,
        }

        # 3) mémoriser les indicateurs pour le prochain tour
        cmds.append({
            "op": "analyse.data.set",
            "cle": "indicateurs",
            "valeur": indicateurs,
        })

        # 2) on évalue les missions existantes et on récupère un bonus momentum
        missions_maj, bonus_opp_momentum = self.evaluer_missions_opposition(
            etat,
            cmds,
            indicateurs,
            indicateurs_prec,
        )

        # on remet à jour le stockage des missions
        cmds.append({
            "op": "opposition.data.set",
            "cle": "missions",
            "valeur": missions_maj,
        })
        # journal “Institut de la statistique”
        cmds.append(self._journal_analyse_etat(etat, indicateurs, indicateurs_prec))

        # 3) on applique le bonus momentum à l'opposition s'il y en a
        if bonus_opp_momentum:
            cmds.append({
                "op": "opposition.capital.delta",
                "delta": bonus_opp_momentum,
            })

        # 4) on peut ensuite appliquer le reste de ta logique (solde, score_axes, etc.)
        #    pour un delta_cabinet / delta_opp "structurel"
        delta_cabinet, delta_opp = self._calculer_delta_capitaux(
            etat, indicateurs, indicateurs_prec
        )

        if delta_cabinet:
            cmds.append({"op": "capital_collectif.delta", "delta": delta_cabinet})
        if delta_opp:
            cmds.append({"op": "opposition.capital.delta", "delta": delta_opp})

        # 5) enfin, on génère de NOUVELLES missions (si certaines n'existent pas déjà),
        #    et on les fusionne à missions_maj (sans les dupliquer).
        nouvelles = self.generer_missions_opposition(
            etat=etat,
            indicateurs=indicateurs,
            missions_existantes=missions_maj,
        )

        if nouvelles:
            missions_maj.extend(nouvelles)
            cmds.append({
                "op": "opposition.data.set",
                "cle": "missions",
                "valeur": missions_maj,
            })
            for m in nouvelles:
                cmds.append(self._journal_declaration_mission(etat, m, nouveaute=True))

        return cmds

    def _calculer_delta_capitaux(
        self,
        etat: Etat,
        indicateurs: Dict[str, Any],
        indicateurs_prec: Optional[Dict[str, Any]],
    ) -> Tuple[int, int]:
        """
        Calcule un petit ajustement de capital politique cabinet / opposition
        en fonction de l'évolution des indicateurs agrégés.

        - Si le score des axes s'améliore fortement => bonus au cabinet
        - Si le score des axes se dégrade fortement => bonus à l'opposition
        - Si on passe d'un solde négatif à positif => petit bonus au cabinet
        - Si on passe d'un solde positif à négatif => petit bonus à l'opposition
        """

        if indicateurs_prec is None:
            # Pas d’historique : pas de delta structurel
            return 0, 0

        score = indicateurs.get("score_axes", 0)
        score_prec = indicateurs_prec.get("score_axes", 0)

        solde = indicateurs.get("solde", 0.0)
        solde_prec = indicateurs_prec.get("solde", 0.0)

        delta_cabinet = 0
        delta_opp = 0

        # 1) Choc sur le score des axes
        diff_score = score - score_prec
        if diff_score >= 2:
            # net mieux perçu sur les axes
            delta_cabinet += 1
        elif diff_score <= -2:
            # net moins bien : l'opposition en profite
            delta_opp += 1

        # 2) Changement de signe du solde budgétaire
        if solde_prec < 0 <= solde:
            # retour dans le vert
            delta_cabinet += 1
        elif solde_prec > 0 >= solde:
            # on tombe dans le rouge
            delta_opp += 1

        return delta_cabinet, delta_opp


    def evaluer_missions_opposition(
        self,
        etat: Etat,
        cmds: List[Command],
        indicateurs: Dict[str, Any],
        indicateurs_prec: Dict[str, Any],
    ) -> Tuple[List[Dict[str, Any]], int]:
        """
        Retourne (missions_mises_a_jour, bonus_opposition)
        """
        missions: List[Dict[str, Any]] = etat.opposition.donnees_skin.get("missions", [])
        missions_maj: List[Dict[str, Any]] = []
        bonus_opp = 0

        social = indicateurs["social"]
        eco = indicateurs["economique"]
        inst = indicateurs["institutionnel"]
        env = indicateurs["environnement"]

        social_prec = indicateurs_prec.get("social")
        eco_prec = indicateurs_prec.get("economique")
        inst_prec = indicateurs_prec.get("institutionnel")
        env_prec = indicateurs_prec.get("environnement")

        for m in missions:
            etat_m = m.get("etat", "en_cours")
            renouv = int(m.get("renouvellements", 0))
            axe = m.get("axe")
            crit = m.get("critere_reussite", {})

            # valeur actuelle de l'axe ciblé
            val_actuelle = None
            val_prec = None
            if axe == "social":
                val_actuelle, val_prec = social, social_prec
            elif axe == "economique":
                val_actuelle, val_prec = eco, eco_prec
            elif axe == "institutionnel":
                val_actuelle, val_prec = inst, inst_prec
            elif axe == "environnement":
                val_actuelle, val_prec = env, env_prec

            # on ne gère ici que les missions basées sur un min_valeur
            min_valeur = None
            if isinstance(crit, dict):
                min_valeur = crit.get("min_valeur")

            mission_atteinte = False
            mission_empiuree = False

            if min_valeur is not None and val_actuelle is not None:
                if val_actuelle >= min_valeur:
                    mission_atteinte = True
                else:
                    # non atteinte, on regarde la tendance
                    if val_prec is not None and val_actuelle < val_prec:
                        mission_empiuree = True

            # mise à jour de l'état de la mission
            if mission_atteinte:
                m["etat"] = "atteinte"
            else:
                # mission toujours non atteinte → renouvellement
                renouv += 1
                m["renouvellements"] = renouv
                m["etat"] = "en_cours"

                if mission_empiuree:
                    m["etat"] = "empiree"
                    # momentum : si elle empire et qu'elle est renouvelée depuis au moins 2 tours,
                    # on donne un bonus à l'opposition
                    if renouv >= 2:
                        bonus_opp += 1
                        cmds.append({
                            "op": "journal",
                            "source": "opposition",
                            "categorie": "momentum",
                            "payload": {
                                "message": (
                                    f"L’opposition souligne que la situation liée à « {m['intitule']} » "
                                    f"s'est encore détériorée malgré ses avertissements répétés."
                                ),
                                "mission_id": m["id"],
                                "renouvellements": renouv,
                            },
                        })

            m["tour_dernier_suivi"] = etat.tour
            missions_maj.append(m)

        return missions_maj, bonus_opp


    def generer_missions_opposition(
        self,
        etat: Etat,
        indicateurs: Dict[str, Any],
        missions_existantes: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """
        Génère de nouvelles missions d'opposition à partir de l'état courant
        et des indicateurs, en évitant de recréer des missions déjà présentes.

        Retourne une liste de dicts prêt à être stockés dans opposition.data.
        """
        nouvelles: List[Dict[str, Any]] = []

        # ids déjà utilisés pour éviter les doublons
        ids_existants = {m.get("id") for m in missions_existantes}

        social = indicateurs["social"]
        eco = indicateurs["economique"]
        inst = indicateurs["institutionnel"]
        env = indicateurs["environnement"]
        score_axes = indicateurs["score_axes"]
        solde = indicateurs["solde"]

        # helper pour construire un dict mission homogène
        def mk_mission(
            mid: str,
            axe: Optional[str],
            intitule: str,
            description: str,
            priorite: int,
            critere_reussite: Dict[str, Any],
        ) -> Dict[str, Any]:
            return {
                "id": mid,
                "axe": axe,
                "intitule": intitule,
                "description": description,
                "priorite": priorite,
                "critere_reussite": critere_reussite,
                "etat": "en_cours",
                "renouvellements": 0,
                "tour_creation": etat.tour,
                "tour_dernier_suivi": etat.tour,
            }

        # 1) mission sociale si social <= 0 ou s'il y a eu un mouvement social récent
        if ("OPP-M1" not in ids_existants) and (
            social <= 0 or self._historique_contient(etat, "EVT-002")
        ):
            nouvelles.append(mk_mission(
                mid="OPP-M1",
                axe="social",
                intitule="Réparer la fracture sociale",
                description=(
                    "Mettre de l'avant une alternative qui répond aux grèves, "
                    "aux manifestations et au sentiment d'abandon des citoyens."
                ),
                priorite=1,
                critere_reussite={
                    "axe": "social",
                    "min_valeur": 1,
                },
            ))

        # 2) mission institutionnelle si inst <= 0
        if ("OPP-M2" not in ids_existants) and inst <= 0:
            nouvelles.append(mk_mission(
                mid="OPP-M2",
                axe="institutionnel",
                intitule="Rétablir la confiance dans les institutions",
                description=(
                    "Proposer des réformes pour renforcer la transparence, "
                    "la responsabilité des élus et la qualité de la démocratie."
                ),
                priorite=2,
                critere_reussite={
                    "axe": "institutionnel",
                    "min_valeur": 1,
                },
            ))

        # 3) mission économique si eco <= 0
        if ("OPP-M3" not in ids_existants) and eco <= 0:
            nouvelles.append(mk_mission(
                mid="OPP-M3",
                axe="economique",
                intitule="Donner une direction économique claire",
                description=(
                    "Sortir du pilotage à vue entre crises et booms, en "
                    "proposant une trajectoire économique cohérente."
                ),
                priorite=2,
                critere_reussite={
                    "axe": "economique",
                    "min_valeur": 1,
                },
            ))

        # 4) mission globale si capital_collectif < capital_opposition
        if ("OPP-M4" not in ids_existants) and (
            etat.capital_collectif < etat.opposition.capital_politique
        ):
            nouvelles.append(mk_mission(
                mid="OPP-M4",
                axe=None,
                intitule="Se présenter comme l'alternative crédible",
                description=(
                    "Convaincre qu'un changement de gouvernement permettrait "
                    "de mieux répondre aux crises et de clarifier le cap."
                ),
                priorite=1,
                critere_reussite={
                    "avantage_opposition": ">0",
                },
            ))

        # 5) mission environnementale si env < 0
        if ("OPP-M5" not in ids_existants) and env < 0:
            nouvelles.append(mk_mission(
                mid="OPP-M5",
                axe="environnement",
                intitule="Reprendre le leadership écologique",
                description=(
                    "Proposer un plan environnemental plus cohérent et moins "
                    "contradictoire pour l'économie."
                ),
                priorite=3,
                critere_reussite={
                    "axe": "environnement",
                    "min_valeur": 1,
                },
            ))

        return nouvelles


    def _historique_contient(self, etat: Etat, evenement_id: str) -> bool:
        for ev in etat.historiques:
            if ev.get("evenement_id") == evenement_id:
                return True
        return False

    def _journal_analyse_etat(
        self,
        etat: Etat,
        indicateurs: dict,
        indicateurs_prec: dict | None = None,
    ) -> Command:
        social = indicateurs["social"]
        eco = indicateurs["economique"]
        inst = indicateurs["institutionnel"]
        env = indicateurs["environnement"]
        score_axes = indicateurs["score_axes"]
        solde = indicateurs["solde"]

        # petit texte synthétique façon communiqué de l’institut
        msg_parts: list[str] = []
        msg_parts.append(
            f"Institut de la statistique : au tour {etat.tour}, "
            f"le score global des axes est de {score_axes}."
        )

        if social <= 0:
            msg_parts.append("La cohésion sociale demeure fragile.")
        if inst <= 0:
            msg_parts.append("La confiance institutionnelle reste limitée.")
        if env > 0:
            msg_parts.append("La transition écologique progresse.")
        if solde > 0:
            msg_parts.append("Les finances publiques sont en léger excédent.")
        elif solde < 0:
            msg_parts.append("Les finances publiques sont en déficit.")

        message = " ".join(msg_parts)

        return {
            "op": "journal",
            "source": "institut_stats",
            "categorie": "bilan_tour",
            "payload": {
                "message": message,
                "indicateurs": indicateurs,
            },
        }

    def _journal_declaration_mission(
        self,
        etat: Etat,
        mission: Dict[str, Any],
        nouveaute: bool,
        momentum: bool = False,
    ) -> Command:
        mid = mission.get("id")
        intitule = mission.get("intitule", "(mission sans titre)")

        if nouveaute:
            message = (
                f"L’opposition annonce une nouvelle priorité : « {intitule} »."
            )
        elif momentum:
            message = (
                f"L’opposition rappelle que la mission « {intitule} » "
                f"reste sans réponse et que la situation se dégrade."
            )
        else:
            message = (
                f"L’opposition réaffirme sa mission : « {intitule} »."
            )

        return {
            "op": "journal",
            "source": "opposition",
            "categorie": "missions",
            "payload": {
                "message": message,
                "mission_id": mid,
                "axe": mission.get("axe"),
                "priorite": mission.get("priorite"),
                "etat_mission": mission.get("etat", "en_cours"),
            },
        }


    # =========================================================================
    #    6. CONDITIONS DE FIN DE PARTIE
    # =========================================================================
    def condition_fin_partie(self, etat: Etat) -> List[Command]:
        cmds: List[Command] = []

        # Exemple simple : fin après N tours
        max_tours = self.config.get("nb_tours_max", 8)
        if etat.tour >= max_tours:
            cmds.append({"op": "partie.terminer", "raison": "TOURS_MAX"})
            cmds.append({"op": "journal", "payload": {"message": "Fin de mandat."}})

        # Exemple crise multiple sur axes
        crises = [a for a in etat.axes.values() if a.valeur <= a.seuil_crise]
        if len(crises) >= 2:
            cmds.append({"op": "partie.terminer", "raison": "CRISE_MULTIPLE"})
            cmds.append({
                "op": "journal",
                "payload": {"message": "Le gouvernement tombe en raison de crises multiples."},
            })

        return cmds

    # -----------------------------------------------------------------
    # Traitement des validations
    # ------------------------------------------------------------------

    def _valider_programme_engager_carte(self, etat: Etat, cmd: Command) -> tuple[bool, List[Command]]:
        """
            Seule les cartes de type Mesure sont acceptées
        """
        
        op = cmd.get("op")
        if op != "programme.engager_carte":
            # par défaut, on ne s'occupe que de ce cas pour l'instant
            return True, []

        joueur_id = cmd["joueur_id"]
        carte_id = cmd["carte_id"]

        j = etat.joueurs.get(joueur_id)
        if j is None:
            return False, []

        # On va chercher la définition de la carte dans le skin
        def_carte = etat.cartes_def.get(carte_id, {})
        cout_att = int(def_carte.get("cout_attention", 0))
        cout_capital = int(def_carte.get("cout_capital", 0))

        cmds: List[Command] = []

        # Exemple: on suppose que j.attention et j.capital existent
        if cout_att:
            attention_dispo = getattr(j, "attention", 0)
            if attention_dispo < cout_att:
                # pas assez de points d'attention → refus
                return False, []
            cmds.append({
                "op": "joueur.attention.delta",
                "joueur_id": joueur_id,
                "delta": -cout_att,
            })

        if cout_capital:
            capital_dispo = getattr(j, "capital_politique", 0)
            if capital_dispo < cout_capital:
                return False, []
            cmds.append({
                "op": "joueur.capital.delta",
                "joueur_id": joueur_id,
                "delta": -cout_capital,
            })

        return True, cmds
        
    def valider_usage_carte(self, etat: Etat, cmd: Command) -> tuple[bool, List[Command]]:
        """
        Validation et coût des cartes.

        Exemple simple:
          - chaque carte a un champ "cout_attention" dans cartes_def
          - on débite les points d'attention du joueur
          - si le joueur n'a pas assez, on refuse
        """
        op = cmd.get("op")
        if op != "programme.engager_carte":
            # par défaut, on ne s'occupe que de ce cas pour l'instant
            return True, []

        joueur_id = cmd["joueur_id"]
        carte_id = cmd["carte_id"]

        j = etat.joueurs.get(joueur_id)
        if j is None:
            return False, []

        # On va chercher la définition de la carte dans le skin
        def_carte = etat.cartes_def.get(carte_id, {})
        cout_att = int(def_carte.get("cout_attention", 0))
        cout_capital = int(def_carte.get("cout_capital", 0))

        cmds: List[Command] = []

        # Exemple: on suppose que j.attention et j.capital existent
        if cout_att:
            attention_dispo = getattr(j, "attention", 0)
            if attention_dispo < cout_att:
                # pas assez de points d'attention → refus
                return False, []
            cmds.append({
                "op": "joueur.attention.delta",
                "joueur_id": joueur_id,
                "delta": -cout_att,
            })

        if cout_capital:
            capital_dispo = getattr(j, "capital_politique", 0)
            if capital_dispo < cout_capital:
                return False, []
            cmds.append({
                "op": "joueur.capital.delta",
                "joueur_id": joueur_id,
                "delta": -cout_capital,
            })

        return True, cmds

    # -----------------------------------------------------------------
    # Helpers d'attente / protocole d'interaction
    # ------------------------------------------------------------------

    def _mk_procedure(
        self,
        code: str,
        titre: str,
        description: str,
        ui_ecran: str | None = None,
        ui_actions: list[dict] | None = None,
        extra: dict | None = None,
    ) -> dict:
        """
        Construit un dict 'procedure' pour meta/attente.
        Le moteur ne l'interprète pas, c'est uniquement pour le TUI.
        """
        procedure: dict = {
            "code": code,
            "titre": titre,
            "description": description,
        }

        ui: dict = {}
        if ui_ecran is not None:
            ui["ecran"] = ui_ecran
        if ui_actions:
            ui["actions"] = ui_actions
        if ui:
            procedure["ui"] = ui

        if extra:
            procedure.update(extra)

        return procedure


    def _attente_joueurs(
        self,
        etat: Etat,
        type_attente: str,
        joueurs: list[str] | None = None,
        procedure: dict | None = None,
    ) -> Command:
        """
        Helper générique pour fabriquer l'op 'attente.joueurs'.
        """
        cmd: Command = {
            "op": "attente.joueurs",
            "type": type_attente,
            "joueurs": list(joueurs or etat.joueurs.keys()),
        }
        if procedure:
            cmd["procedure"] = procedure
        return cmd


    def _attente_engager_cartes(self, etat: Etat) -> Command:
            """
            Attente ENGAGER_CARTE pendant PHASE_PROGRAMME.
            Tous les joueurs sont concernés.
            """
            procedure = self._mk_procedure(
                code="ENGAGER_PROGRAMME",
                titre="Confection du programme du cabinet",
                description="Engagez des cartes de votre main dans le programme, puis confirmez.",
                ui_ecran="programme",
                ui_actions=[
                    {
                        "op": "programme.engager_carte",
                        "label": "Engager une carte au programme",
                        "fields": [
                            {
                                "name": "joueur_id",
                                "label": "Joueur",
                                "required": True,
                                "domain": "joueur_id",
                            },
                            {
                                "name": "carte_id",
                                "label": "Carte à engager",
                                "required": True,
                                "domain": "carte_main",
                            },
                        ],
                    },
                    {
                        "op": "attente.joueur_recu",
                        "label": "Terminer mes engagements",
                        "fields": [
                            {
                                "name": "joueur_id",
                                "label": "Joueur",
                                "required": True,
                                "domain": "joueur_id",
                            },
                            {
                                "name": "type",
                                "label": "Type d'attente",
                                "required": True,
                                "domain": "attente_type",  # interprété par le TUI comme valeur imposée: "ENGAGER_CARTE"
                            },
                        ],
                    },
                ],
            )
            return self._attente_joueurs(
                etat=etat,
                type_attente="ENGAGER_CARTE",
                procedure=procedure,
            )

    def _attente_vote_programme(
            self,
            etat: Etat,
            joueurs_habiletes: list[str],
        ) -> Command:
            """
            Attente VOTE pour le programme, limitée aux joueurs habilités.
            """
            procedure = self._mk_procedure(
                code="VOTE_PROGRAMME",
                titre="Vote sur le programme",
                description="Votez pour ou contre le programme, puis confirmez.",
                ui_ecran="vote_programme",
                ui_actions=[
                    {
                        "op": "joueur.vote.set",
                        "label": "Voter",
                        "fields": [
                            {
                                "name": "joueur_id",
                                "label": "Joueur",
                                "required": True,
                                "domain": "joueur_id",
                            },
                            {
                                "name": "valeur",
                                "label": "Votre vote",
                                "required": True,
                                "domain": {
                                    "kind": "choice",
                                    "values": [
                                        {"value": 1, "label": "Pour"},
                                        {"value": 0, "label": "Abstention"},
                                        {"value": -1, "label": "Contre"},
                                    ],
                                },
                            },
                        ],
                    },
                    {
                        "op": "attente.joueur_recu",
                        "label": "Enregistrer mon vote",
                        "fields": [
                            {
                                "name": "joueur_id",
                                "label": "Joueur",
                                "required": True,
                                "domain": "joueur_id",
                            },
                            {
                                "name": "type",
                                "label": "Type d'attente",
                                "required": True,
                                "domain": "attente_type",  # valeur imposée: "VOTE"
                            },
                        ],
                    },
                ],
            )
            return self._attente_joueurs(
                etat=etat,
                type_attente="VOTE",
                joueurs=joueurs_habiletes,
                procedure=procedure,
            )

    def _attente_perturbation_vote(self, etat: Etat) -> Command:
            """
            Attente PERTURBATION_VOTE.
            À enrichir quand les cartes de perturbation seront codées.
            """
            procedure = self._mk_procedure(
                code="PERTURBATION_VOTE",
                titre="Perturbations du vote",
                description="Vous pouvez jouer des cartes qui perturbent le vote, puis confirmer.",
                ui_ecran="perturbation_vote",
                ui_actions=[
                    {
                        "op": "attente.joueur_recu",
                        "label": "Aucune carte à jouer",
                        "fields": [
                            {
                                "name": "joueur_id",
                                "label": "Joueur",
                                "required": True,
                                "domain": "joueur_id",
                            },
                            {
                                "name": "type",
                                "label": "Type d'attente",
                                "required": True,
                                "domain": "attente_type",  # valeur imposée: "PERTURBATION_VOTE"
                            },
                        ],
                    },
                ],
            )
            return self._attente_joueurs(
                etat=etat,
                type_attente="PERTURBATION_VOTE",
                procedure=procedure,
            )



    # =========================================================================
    #    Gestion des réponses des joueurs.
    # =========================================================================
    def regle_attente_terminee(self, etat: Etat, type_attente: str) -> List[Command]:
        cmds: List[Command] = []

        if type_attente == "ENGAGER_CARTE":
            # On applique les cartes du programme si adoptées.
            # La procédure de vote est séparée : elle sera appelée par le moteur au bon moment.
            cmds.append({"op": "journal", "payload": {"message": "Le programme du cabinet a été confectionné. On passe au vote maintenant."}})

            cmds.extend(self.determiner_sous_phase(etat))
            return cmds

        elif type_attente == "VOTE":
            if etat.programme is None:
                cmds.append({
                    "op": "journal",
                    "payload": {"message": "Impossible de calculer le verdict : aucun programme en cours."},
                })
            else :
                # Obtenir le verdict 
                etat.programme.verdict = etat.programme.resultat_vote()
                cmds.append({"op":"programme.verdict.set", "adopte" : etat.programme.verdict})

                cmds.append({
                    "op": "journal",
                    "payload": {"message": f"Adoption du programme : {etat.programme.verdict}"},
                })

                cmds.extend(self.determiner_sous_phase(etat))
                return cmds

        elif type_attente == "PERTURBATION_VOTE":
            if etat.programme is None:
                cmds.append({
                    "op": "journal",
                    "payload": {"message": "Impossible de calculer le verdict : aucun programme en cours."},
                })
            else :
                cmds.extend(self.determiner_sous_phase(etat))
                return cmds


        cmds.extend(self.determiner_sous_phase(etat))
        return cmds

