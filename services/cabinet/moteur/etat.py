# services/cabinet/moteur/etat.py
from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import TypedDict, Dict, List, Literal, Optional, Any, Deque, Tuple, Set, Mapping
from collections import deque
import copy

import random

from .regles_interfaces import ReglesInterface

from .events import EvenementDomaine, make_evt_from_op

__version__ = "0.3.0"

AxeId = str
JoueurId = str
CarteId = str

# --- Axes --------------------------------------------------------------------

@dataclass
class Axe:
    id: AxeId
    valeur: int          # 0..10
    seuil_crise: int
    poids: float = 1.0

    def clamp(self) -> None:
        self.valeur = max(0, min(10, self.valeur))

    def delta(self, d: int) -> None:
        self.valeur += d
        self.clamp()

    @property
    def en_crise(self) -> bool:
        return self.valeur <= self.seuil_crise

# --- Économie ----------------------------------------------------------------

@dataclass
class PosteBudgetaire:
    """Un poste de recettes/dépenses avec impacts sur les axes."""
    nom: str
    valeur: float
    poids_axes: Dict[str, int] = field(default_factory=dict)
    # métadonnées libres pour le skin (environnement, tags, etc.)
    meta: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_cfg(cls, nom: str, cfg: Mapping[str, Any]) -> "PosteBudgetaire":
        valeur = float(cfg.get("valeur", 0.0))
        poids_axes = dict(cfg.get("poids_axes", {}))
        meta = {
            k: v
            for k, v in cfg.items()
            if k not in ("valeur", "poids_axes")
        }
        return cls(nom=nom, valeur=valeur, poids_axes=poids_axes, meta=meta)


@dataclass
class PosteEfficience:
    """Efficience appliquée à un thème/poste (santé, éducation, etc.)."""
    nom: str
    valeur: float
    meta: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_cfg(cls, nom: str, cfg: Mapping[str, Any]) -> "PosteEfficience":
        valeur = float(cfg.get("valeur", 1.0))
        meta = {k: v for k, v in cfg.items() if k != "valeur"}
        return cls(nom=nom, valeur=valeur, meta=meta)


class Economie:
    """
    Budget de l'État.
    Structure minimale :
      - recettes : dict[nom_poste -> PosteBudgetaire]
      - depenses : dict[nom_poste -> PosteBudgetaire]
      - efficience : dict[theme/poste -> PosteEfficience]
      - dette, taux_interet

    Les skins peuvent ajouter tout ce qu'ils veulent dans la section economie :
      - clés supplémentaires au niveau racine
      - champs supplémentaires dans chaque poste (meta).
    """

    def __init__(
        self,
        *,
        recettes: Mapping[str, Mapping[str, Any]] | None = None,
        depenses: Mapping[str, Mapping[str, Any]] | None = None,
        efficience: Mapping[str, Mapping[str, Any]] | None = None,
        dette: float = 0.0,
        taux_interet: float = 0.0,
        **cfg: Any,  # autres champs libres définis par le skin
    ) -> None:
        # postes de recettes / dépenses
        self.recettes: Dict[str, PosteBudgetaire] = {}
        self.depenses: Dict[str, PosteBudgetaire] = {}
        self.efficience: Dict[str, PosteEfficience] = {}

        for nom, cfg_poste in (recettes or {}).items():
            self.recettes[nom] = PosteBudgetaire.from_cfg(nom, cfg_poste)

        for nom, cfg_poste in (depenses or {}).items():
            self.depenses[nom] = PosteBudgetaire.from_cfg(nom, cfg_poste)

        for nom, cfg_eff in (efficience or {}).items():
            self.efficience[nom] = PosteEfficience.from_cfg(nom, cfg_eff)

        # finances publiques génériques
        self.dette: float = float(dette)
        self.taux_interet: float = float(taux_interet)

        # tous les champs supplémentaires définis par le skin
        # deviennent des attributs libres sur Economie
        for k, v in cfg.items():
            if not hasattr(self, k):
                setattr(self, k, v)

    # --- méthodes génériques que le noyau peut utiliser ---

    def total_recettes(self) -> float:
        return sum(p.valeur for p in self.recettes.values())

    def total_depenses(self) -> float:
        return sum(p.valeur for p in self.depenses.values())

    def charge_financiere(self) -> float:
        return self.taux_interet * self.dette

    def solde_brut(self) -> float:
        """Solde simple sans appliquer de logique fine de skin."""
        return self.total_recettes() - self.total_depenses() - self.charge_financiere()

# --- Joueurs -----------------------------------------------------------------

@dataclass
class Joueur:
    id: JoueurId
    nom: str
    alias: str = ""       # alias public dans la partie
    role: str = ""        # hote, invite, spectateur, ...
    capital_politique: int = 0
    attention_max: int = 2
    attention_dispo: int = 2
    main: List[CarteId] = field(default_factory=list)

    # --- nouveau pour le vote ---
    poids_vote: int = 1          # nombre de voix “normales”
    peut_voter: bool = True      # carte spéciale peut le passer à False

    def pioche_en_main(self, cartes: List[CarteId]) -> None:
        self.main.extend(cartes)

    def defausser(self, carte: CarteId) -> bool:
        if carte in self.main:
            self.main.remove(carte)
            return carte
        return None

@dataclass
class AttenteJoueurs:
    """
    Modélise une attente de réponses des joueurs.

    statut:
      - "ATTENTE_REPONSE_JOUEUR" : les joueurs peuvent encore répondre
      - "REPONSES_RECUES"        : tous les joueurs attendus ont répondu
      - "TERMINE" ou None        : aucune attente active
    """
    statut: Optional[str] = None          # voir ci-dessus
    type: Optional[str] = None            # "VOTE", "ENGAGER_CARTE", ...
    joueurs: List[JoueurId] = field(default_factory=list)
    recus: Set[JoueurId] = field(default_factory=set)
    meta: Dict[str, Any] = field(default_factory=dict)

    # Helpers pour garder une API lisible
    @property
    def est_active(self) -> bool:
        return self.statut == "ATTENTE_REPONSE_JOUEUR"

    @property
    def est_complete(self) -> bool:
        return self.statut == "REPONSES_RECUES"

    def init(
        self,
        type: str,
        joueurs: List[JoueurId],
        meta: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Ouvre une nouvelle attente. Écrase l'ancienne si elle était TERMINE/None.
        """
        self.statut = "ATTENTE_REPONSE_JOUEUR"
        self.type = type
        self.joueurs = list(joueurs)
        self.recus.clear()
        self.meta = dict(meta or {})

    def marquer_recu(self, joueur_id: JoueurId) -> None:
        """
        Marque une réponse reçue pour un joueur.
        Ne fonctionne que si l'attente est en cours.
        """
        if self.statut != "ATTENTE_REPONSE_JOUEUR":
            return
        if joueur_id in self.recus :
            return

        if joueur_id in self.joueurs:
            self.recus.add(joueur_id)
            if set(self.joueurs) <= self.recus:
                # tous les joueurs ciblés ont répondu
                self.statut = "REPONSES_RECUES"

    def terminer(self) -> None:
        """
        Clôt définitivement l'attente.
        On garde type/meta pour consultation éventuelle jusqu'à la prochaine init().
        """
        self.statut = "TERMINE"
        self.type = None
        self.joueurs.clear()
        self.recus.clear()
        self.meta.clear()

    def reset_hard(self) -> None:
        """
        Reset complet : utilisé si tu veux tout effacer, y compris type/meta.
        """
        self.statut = None
        self.type = None
        self.joueurs.clear()
        self.recus.clear()
        self.meta.clear()

@dataclass
class EtatOpposition:
    """
    État simplifié de l'opposition.

    - capital_politique : score global utilisé pour comparer au capital_collectif
    - donnees_skin      : espace libre pour la skin (adhésion, missions, etc.)
    """
    capital_politique: int = 0
    donnees_skin: Dict[str, Any] = field(default_factory=dict)

# --- Decks -------------------------------------------------------------------
CardType = Literal["mesure", "amendement", "procedure", "evenement"]
ProgrammeCardType = Literal["mesure", "amendement"]


@dataclass
class DeckState:
    """Deck sans remise, avec défausse, pour cartes 'mesure/amendement/procedure'."""
    pioche: Deque[CarteId] = field(default_factory=deque)
    defausse: Deque[CarteId] = field(default_factory=deque)

    def tirer(self, n: int = 1) -> List[CarteId]:
        cartes: List[CarteId] = []
        for _ in range(n):
            if not self.pioche and self.defausse:
                # On remélange la défausse (simple rotation ici; le mélange se fera au setup)
                self.pioche = deque(self.defausse)
                self.defausse = deque()
            if not self.pioche:
                break
            cartes.append(self.pioche.popleft())
        return cartes

    def jeter(self, carte: CarteId) -> None:
        if carte :
            self.defausse.append(carte)

    def melanger(self) -> None:
        """Mélange la pioche (déterminisme laissé au jeu/skin, ici random simple)."""
        cartes = list(self.pioche)
        random.shuffle(cartes)
        self.pioche = deque(cartes)


@dataclass
class EventDeckState:
    pioche: Deque[str] = field(default_factory=deque)
    defausse: Deque[str] = field(default_factory=deque)
    actif: Optional[str] = None

    def prochain(self) -> Optional[str]:
        """Tire la prochaine carte événement sans la défausser immédiatement."""
        if not self.pioche:
            return None
        self.actif = self.pioche.popleft()
        return self.actif

    def clore_evt(self) -> None:
        """Déplace l’événement actif vers la défausse."""
        if self.actif:
            self.defausse.appendleft(self.actif)
            self.actif = None


# --- Programme ---------------------------------------------------------------

@dataclass
class EntreeProgramme:
    uid: str
    carte_id: CarteId
    auteur_id: JoueurId
    type: ProgrammeCardType = "mesure"   # par défaut
    params: Dict[str, Any] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)
    attention_engagee: int = 0

@dataclass
class ProgrammeTour:
    version: int = 2
    entrees: List[EntreeProgramme] = field(default_factory=list)
    votes: Dict[JoueurId, int] = field(default_factory=dict)  # vote global binaire
    verdict : bool = None

    def resultat_vote(self) -> Optional[bool]:
        if not self.votes:
            return None
        oui = sum(1 for v in self.votes.values() if v == 1)
        non = sum(1 for v in self.votes.values() if v == -1)
        abs = sum(1 for v in self.votes.values() if v == 0)
        return True if oui > non else False if non > oui else None  # None = égalité

# --- Gestion de la dynamique des tours ---------------------------------------

Phase = Literal["mise_en_place", "tour", "fin_jeu"]
SousPhase = Literal[
    "monde",
    "conseil",
    "vote_programme",
    "amendements",
    "execution_programme",
    "cloture_tour",
]

class Command(TypedDict, total=False):
    op: str
    axe: str
    delta: int
    reason: str
    joueur_id: str
    cout: int
    carte_id: str
    sous_phase: str
    type: str
    payload: Dict[str, Any]

# --- État principal ----------------------------------------------------------

@dataclass
class Etat:
    id: str
    tour: int
    axes: Dict[AxeId, Axe]
    eco: Economie

    joueurs: Dict[JoueurId, Joueur]
    attente: AttenteJoueurs = field(default_factory=AttenteJoueurs)
    capital_collectif: int = 0
    opposition: EtatOpposition = field(default_factory=EtatOpposition)

    analyse_skin: Dict[str, Any] = field(default_factory=dict)
    programme: Optional[ProgrammeTour] = None

    historiques: List[Dict[str, Any]] = field(default_factory=list)
    termine: bool = False
    raison_fin: Optional[str] = None

    # moteur de règles
    skin: str | None = None
    regles: Optional[ReglesInterface] = None

    # définitions et decks
    cartes_def: Dict[CarteId, Dict[str, Any]] = field(default_factory=dict)
    deck_global: DeckState = field(default_factory=DeckState)
    deck_events: EventDeckState = field(default_factory=EventDeckState)
    main_init : int = 3
    
    # --- état de la machine d'étapes/phases ---
    phase: Phase = "mise_en_place"
    sous_phase: Optional[SousPhase] = None

    # ordre des sous-phases défini par la skin (peut changer les noms !)
    sous_phase_order: tuple[str, ...] = field(default_factory=tuple)

    # mapping sous-phase -> signal BRE/mocked (défaut si non fourni par la skin)
    sous_phase_signals: Dict[str, str] = field(default_factory=dict)

    # registre interne: quelles sous-phases ont déjà été exécutées à ce tour ?
    _hooks_done: Set[Tuple[int, SousPhase]] = field(default_factory=set, repr=False)

    # --- buffer d’événements de domaine ---
    evenements: List[EvenementDomaine] = field(default_factory=list, repr=False)

    def clone(self) -> "Etat":
        return copy.deepcopy(self)

    def asdict(self) -> Dict[str, Any]:
        return asdict(self)

    # ----------------------------------------------------
    # Hooks (vides par défaut) que tu peux surcharger plus tard
    # ----------------------------------------------------
    def _on_mise_en_place(self) -> None:
        """Distribuer les mains initiales, initialiser ressources, etc."""
        pass

    def _run_subphase(self, sp: str) -> None:
        if self.termine:
            self.journaliser("phase_skip_partie_terminee", sous_phase=sp)
            return
        """Exécute la sous-phase `sp` au plus une fois, via le moteur de règles."""
        if self._has_run(sp):
            self.journaliser("hook_skip", key=f"{self.tour}:{sp}")
            return

        signal = self.sous_phase_signals.get(sp, f"on_{sp}")
        if not signal or self.regles is None:
            return

        cmds = self.regles.regle_sous_phase(self, signal)
        self.appliquer_commandes(cmds)
        self._mark_run(sp)

    def _has_run(self, sp: SousPhase) -> bool:
        return (self.tour, sp) in self._hooks_done

    def _mark_run(self, sp: SousPhase) -> None:
        self._hooks_done.add((self.tour, sp))
        self.journaliser("hook_done", key=f"{self.tour}:{sp}")

    # --- Primitives de tour --------------------------------------------------

    def avancer_tour(self) -> None:
        self.tour += 1

    def _extraire_joueur_id(self, meta: dict) -> str | None:
        jid = meta.get("joueur_id")
        if jid:
            return jid
        payload = meta.get("payload") or {}
        if isinstance(payload, dict):
            return payload.get("joueur_id")
        return None

    def _route_notif_joueur(self, type_evt: str, meta: dict) -> dict | None:
        """
        Catalogue central : pour certains types d'événements métier journalisés,
        on déclenche aussi une notification joueur (UX immédiate).
        Retourne un dict {joueur_id, code, message, severity, payload} ou None.
        """
        jid = self._extraire_joueur_id(meta)

        # --- programme : refus d'engagement ---
        if type_evt == "programme_engagement_attention_insuffisante":
            carte_id = meta.get("carte_id") or "carte"
            cout = meta.get("cout_attention")
            dispo = meta.get("attention_dispo")
            if not jid:
                return None
            return {
                "joueur_id": jid,
                "code": "erreur.programme.engager.attention_insuffisante",
                "message": f"échec : attention insuffisante pour engager {carte_id} (coût {cout}, dispo {dispo}).",
                "severity": "error",
                "payload": {"type": type_evt, **meta},
            }

        if type_evt == "programme_engagement_invalide":
            carte_id = meta.get("carte_id") or "carte"
            if not jid:
                return None
            return {
                "joueur_id": jid,
                "code": "erreur.programme.engager.invalide",
                "message": f"échec : engagement invalide ({carte_id}).",
                "severity": "error",
                "payload": {"type": type_evt, **meta},
            }


        # --- attente : réponses incohérentes / UI en retard ---
        if type_evt == "attente_joueur_recu_sans_attente":
            if not jid:
                return None
            return {
                "joueur_id": jid,
                "code": "warn.attente.sans_attente",
                "message": "réponse ignorée : aucune attente active (écran probablement en retard).",
                "severity": "warn",
                "payload": {"type": type_evt, **meta},
            }

        if type_evt == "attente_type_incoherent":
            if not jid:
                return None
            tr = meta.get("type_recu")
            ta = meta.get("attente_type")
            return {
                "joueur_id": jid,
                "code": "warn.attente.type_incoherent",
                "message": f"réponse ignorée : type d’attente incohérent (reçu {tr}, attendu {ta}).",
                "severity": "warn",
                "payload": {"type": type_evt, **meta},
            }

        # --- vote : refus / incohérences ---
        if type_evt == "vote_refuse_joueur_inconnu":
            if not jid:
                return None
            return {
                "joueur_id": jid,
                "code": "erreur.vote.joueur_inconnu",
                "message": "vote refusé : joueur inconnu.",
                "severity": "error",
                "payload": {"type": type_evt, **meta},
            }

        if type_evt == "vote_refuse_pas_habile":
            if not jid:
                return None
            return {
                "joueur_id": jid,
                "code": "erreur.vote.pas_habile",
                "message": "vote refusé : vous n’êtes pas habilité à voter.",
                "severity": "error",
                "payload": {"type": type_evt, **meta},
            }

        if type_evt == "vote_refuse_deja_confirme":
            if not jid:
                return None
            return {
                "joueur_id": jid,
                "code": "warn.vote.deja_confirme",
                "message": "vote ignoré : vous avez déjà confirmé votre bulletin.",
                "severity": "warn",
                "payload": {"type": type_evt, **meta},
            }

        if type_evt == "vote_refuse_sans_programme":
            if not jid:
                return None
            return {
                "joueur_id": jid,
                "code": "warn.vote.sans_programme",
                "message": "vote ignoré : aucun programme actif.",
                "severity": "warn",
                "payload": {"type": type_evt, **meta},
            }

        # --- vote : retirer ---
        if type_evt == "vote_retirer_joueur_inconnu":
            if not jid:
                return None
            return {
                "joueur_id": jid,
                "code": "erreur.vote_retirer.joueur_inconnu",
                "message": "retrait du vote refusé : joueur inconnu.",
                "severity": "error",
                "payload": {"type": type_evt, **meta},
            }

        if type_evt == "vote_retirer_pas_habile":
            if not jid:
                return None
            return {
                "joueur_id": jid,
                "code": "erreur.vote_retirer.pas_habile",
                "message": "retrait du vote refusé : vous n’êtes pas habilité à voter.",
                "severity": "error",
                "payload": {"type": type_evt, **meta},
            }

        if type_evt == "vote_retirer_sans_programme":
            if not jid:
                return None
            return {
                "joueur_id": jid,
                "code": "warn.vote_retirer.sans_programme",
                "message": "retrait ignoré : aucun programme actif.",
                "severity": "warn",
                "payload": {"type": type_evt, **meta},
            }
        return None

    def journaliser(self, type_evt: str, **payload: Any) -> None:
        meta = {"tour": self.tour, "type": type_evt, **payload}
        self.historiques.append(meta)

        notif = self._route_notif_joueur(type_evt, meta)
        if notif:
            self.notifier_joueur(
                joueur_id=notif["joueur_id"],
                code=notif["code"],
                message=notif["message"],
                severity=notif["severity"],
                payload=notif.get("payload"),
            )

    # --- Notifications ciblées (UX) ----------------------------------------
    def notifier_joueur(
        self,
        joueur_id: str,
        code: str,
        message: str,
        *,
        severity: str = "warn",
        refs: Mapping[str, Any] | None = None,
        payload: Mapping[str, Any] | None = None,
    ) -> None:
        """Émet une notification ciblée joueur via un événement de domaine `notif.joueur`.

        Objectif : permettre à l'UI d'afficher immédiatement (toast/bandeau) un refus
        ou une erreur qui ne concerne que le joueur.

        Notes :
        - On n'applique PAS une commande `notif.joueur` ici (évite récursion).
        - On émet un EvenementDomaine avec recipients=[joueur_id].
        - Le moteur conserve en parallèle la trace métier dans l'historique
          via `journaliser(...)` (refus/action/etc.).
        """
        data = {
            "op": "notif.joueur",
            "joueur_id": joueur_id,
            "code": code,
            "payload": {
                "message": message,
                "refs": dict(refs or {}),
                **(dict(payload or {})),
            },
        }

        evt = make_evt_from_op(
            self.id,
            "notif.joueur",
            data,
            recipients=[joueur_id],
            severity=severity,
            metadata={"code": code, "scope": "joueur", "joueur_id": joueur_id},
        )
        self.ajouter_evenement(evt)

    # --- Raccourcis cartes ---------------------------------------------------

    def preparer_commandes_carte(
        self,
        joueur_id: JoueurId,
        carte_id: CarteId,
        **kwargs: Any,
    ) -> List[Command]:
        """
        Construit les commandes à partir de la définition de carte.

        Ne touche PAS à l'état de la partie :
        - ne vérifie pas les ressources
        - ne modifie pas la main / le deck
        - n'applique pas les commandes

        Retourne :
        - commandes : liste de commandes prêtes à être appliquées
        """
        defn = self.cartes_def.get(carte_id, {})
        carte_type: CardType = defn.get("type", "mesure")

        commandes_cfg = defn.get("commandes") or []
        commandes: List[Command] = copy.deepcopy(list(commandes_cfg))
        effet: Dict[str, Any] = defn.get("effet", {})

        # Coûts par défaut définis dans la carte
        cout_cp_def = int(defn.get("cout_cp", 0))
        cout_attention_def = int(defn.get("cout_attention", 0))

        # Efforts éventuellement surchargés par l'UI
        effort_cp = int(kwargs.get("effort_cp", cout_cp_def))
        effort_attention = int(kwargs.get("effort_attention", cout_attention_def))

        # Cible pour les cartes relationnelles
        cible_id: JoueurId = kwargs.get("cible_id") or joueur_id

        # Résolution des placeholders
        for cmd in commandes:
            if cmd.get("joueur_id") == "_auto":
                cmd["joueur_id"] = joueur_id
            elif cmd.get("joueur_id") == "_cible":
                cmd["joueur_id"] = cible_id

            # convention : delta == "_effort" → effort_cp
            if cmd.get("delta") == "_effort":
                cmd["delta"] = effort_cp

            # (optionnel) autres remplacements basés sur kwargs
            # ex: if cmd.get("axe") == "_axe": cmd["axe"] = kwargs["axe"]

        # Fallback legacy via effet.delta_axes
        if not commandes:
            delta_axes = effet.get("delta_axes", {})
            commandes = [
                {"op": "axes.delta", "axe": axe, "delta": int(delta)}
                for axe, delta in delta_axes.items()
            ]

        return commandes

    def jouer_carte(self, joueur_id: JoueurId, carte_id: CarteId, **kwargs: Any) -> bool:
        j = self.joueurs[joueur_id]
        if carte_id not in j.main:
            return False

        defn = self.cartes_def.get(carte_id, {})
        carte_type: CardType = defn.get("type", "mesure")
        effet: Dict[str, Any] = defn.get("effet", {})

        # Coûts par défaut
        cout_cp_def = int(defn.get("cout_cp", 0))
        cout_attention_def = int(defn.get("cout_attention", 0))

        # Efforts réels (possiblement choisis par l'acteur via l'UI)
        effort_cp = int(kwargs.get("effort_cp", cout_cp_def))
        effort_attention = int(kwargs.get("effort_attention", cout_attention_def))

        # Cible logique pour la journalisation
        cible_id: JoueurId = kwargs.get("cible_id") or joueur_id

        # Vérifications de marge de manœuvre
        if j.capital_politique < effort_cp:
            return False
        if j.attention_dispo < effort_attention:
            return False

        # Construction des commandes
        commandes = self.preparer_commandes_carte(
            joueur_id,
            carte_id,
            **kwargs,
        )

        # Application de l'effet
        if commandes:
            self.appliquer_commandes(commandes)

        # Paiement des coûts
        j.capital_politique -= effort_cp
        j.attention_dispo -= effort_attention

        # Défausse de la carte
        self.deck_global.jeter(j.defausser(carte_id))

        # Journalisation détaillée
        self.journaliser(
            "jouer_carte",
            joueur=joueur_id,
            carte=carte_id,
            type=carte_type,
            effet=effet,
            commandes=commandes,
            cout_cp=effort_cp,
            cout_attention=effort_attention,
            cible=cible_id,
        )
        return True




    def jeter_carte(self, joueur_id: JoueurId, carte_id: CarteId) -> bool:
        """Défausse une carte depuis la main d'un joueur vers le deck global."""
        j = self.joueurs[joueur_id]
        if carte_id not in j.main:
            return False

        self.deck_global.jeter(j.defausser(carte_id))
        self.journaliser("defausser_carte", joueur=joueur_id, carte=carte_id)
        return True

    def piocher(self, joueur_id: JoueurId, n: int = 1) -> List[CarteId]:
        cartes = self.deck_global.tirer(n)
        self.joueurs[joueur_id].pioche_en_main(cartes)
        if cartes:
            self.journaliser("piocher", joueur=joueur_id, cartes=cartes)
        return cartes

    # ----------------------------------------------------
    # machine d'états légère pour étapes/phases
    # ----------------------------------------------------

    def demarrer_partie(self) -> None:
        """Passe de 'mise_en_place' au mode 'tour' et laisse le skin choisir la première sous-phase."""
        if self.phase != "mise_en_place":
            return
        self._on_mise_en_place()
        self.phase = "tour"
        self.sous_phase = None  # sera déterminée par le skin via avancer_sous_phase()

        self.journaliser("phase", phase=self.phase, sous_phase=self.sous_phase)
        self.ajouter_evenement(
            make_evt_from_op(
                self.id,
                "phase.set",
                {
                    "op": "phase.set",
                    "partie_id": self.id,
                    "phase": self.phase,
                    "sous_phase": self.sous_phase,
                },
            )
        )

        # Premier "tick" de sous-phase : le skin décidera quoi faire
        self.avancer_sous_phase()


    def appliquer_commandes(self, commandes: list[dict]) -> None:
        """
        Applique les commandes CAB.D001.
        Chaque commande est un dict {"op": "...", ...}.
        D001 NE tient PAS compte du moment du processus :
          – le BRE, les skins ou les joueurs décident du QUAND,
          – D001 applique seulement le QUOI.

        Les familles d'opérations sont documentées dans le README “Langage des commandes”.
        """
        print(f"Commande = {commandes}")
        for cmd in commandes:
            op = cmd.get("op")
            if not op:
                continue

            # --- Événement de domaine pour chaque op appliquée ---
            try:
                evt = make_evt_from_op(self.id, op, cmd)
                self.ajouter_evenement(evt)
            except ValueError:
                # op non mappée dans OP_MATRIX → on n'émet pas d'événement domaine
                self.journaliser("evt_op_non_classe", op=op, cmd=cmd)

            # ------------------------------------------------------------------
            # D600 – Déroulement / phases / attente joueurs / notifications
            # ------------------------------------------------------------------
            if op == "phase.set":
                self.sous_phase = cmd["sous_phase"]

            elif op == "tour.increment":
                self.avancer_tour()  # déjà présent dans Etat

            elif op == "partie.terminer":
                self.termine = True
                self.raison_fin = cmd.get("raison", "FIN_INCONNUE")
                self.phase = "fin_jeu"
                self.appliquer_commandes([
                            {"op": "phase.set", "sous_phase" : None}
                        ])
                self.journaliser("partie_terminee", raison=self.raison_fin)

            elif op == "partie.joueur_quitte_definitivement":
                # Rien à modifier dans l'état de la partie : c'est un signal logistique.
                # Mais on journalise pour garder une trace dans l'historique interne.
                self.journaliser(
                    "joueur_quitte_definitivement",
                    joueur_id=cmd.get("joueur_id"),
                    partie_id=cmd.get("partie_id", self.id),
                )

            # notifications UX
            elif op == "notif.broadcast":
                self.journaliser("notif_broadcast", code=cmd["code"], payload=cmd.get("payload", {}))

            elif op == "notif.joueur":
                self.journaliser("notif_joueur",
                                 joueur_id=cmd["joueur_id"],
                                 code=cmd["code"],
                                 payload=cmd.get("payload", {}))

            # ------------------------------------------------------------------
            # D100 – Axes / économie / capital collectif
            # ------------------------------------------------------------------
            elif op == "axes.delta":
                axe = self.axes[cmd["axe"]]
                axe.delta(int(cmd["delta"]))

            elif op == "axes.set":
                axe = self.axes[cmd["axe"]]
                axe.valeur = int(cmd["valeur"])
                axe.clamp()

            elif op == "axes.poids.set":
                axe = self.axes[cmd["axe"]]
                axe.poids = float(cmd["poids"])

            # === ÉCONOMIE (pilotée par le skin) =========================

            elif op == "eco.delta_recettes":
                """
                Ajuste les recettes d’un ou plusieurs postes.

                Convention :
                - self.eco.recettes est un dict[str, PosteBudgetaire]
                  construit à partir du config du skin.
                - La commande fournit un dict "postes": {nom_poste: delta_valeur}.

                Exemple :
                    { "op": "eco.delta_recettes",
                      "postes": { "impot_part": +200, "taxe_carbone": -50 } }
                """
                postes = cmd.get("postes", {})
                for nom_poste, delta in postes.items():
                    poste = self.eco.recettes.get(nom_poste)
                    if poste is None:
                        # poste non défini par le skin : on le crée à 0
                        poste = PosteBudgetaire(nom=nom_poste, valeur=0.0)
                        self.eco.recettes[nom_poste] = poste
                    poste.valeur = float(poste.valeur) + float(delta)

            # ------------------------------------------------------------------

            elif op == "eco.delta_depenses":
                """
                Ajuste les dépenses d’un ou plusieurs postes.

                Convention :
                - self.eco.depenses est un dict[str, PosteBudgetaire].

                Exemple :
                    { "op": "eco.delta_depenses",
                      "postes": { "sante": +300, "defense": -100 } }
                """
                postes = cmd.get("postes", {})
                for nom_poste, delta in postes.items():
                    poste = self.eco.depenses.get(nom_poste)
                    if poste is None:
                        poste = PosteBudgetaire(nom=nom_poste, valeur=0.0)
                        self.eco.depenses[nom_poste] = poste
                    poste.valeur = float(poste.valeur) + float(delta)

            # ------------------------------------------------------------------

            elif op == "eco.delta_dette":
                """
                Ajuste la dette globale de l'État.

                Exemple :
                    { "op": "eco.delta_dette", "montant": +3 }
                """
                self.eco.dette = float(self.eco.dette) + float(cmd["montant"])

            # ------------------------------------------------------------------

            elif op == "eco.set_taux":
                """
                Ajuste un ou plusieurs taux économiques.

                On ne limite PAS la liste des taux :
                - le skin décide quels champs existent dans Economie.
                - on se contente de poser des floats.

                Exemple :
                    { "op": "eco.set_taux",
                      "taux": { "taux_interet": 0.05 } }
                """
                for k, v in cmd["taux"].items():
                    setattr(self.eco, k, float(v))

            # ------------------------------------------------------------------
            # D200 – Joueurs
            # ------------------------------------------------------------------
            elif op == "joueur.capital.delta":
                self.joueurs[cmd["joueur_id"]].capital_politique += cmd["delta"]

            elif op == "joueur.capital.set":
                self.joueurs[cmd["joueur_id"]].capital_politique = cmd["valeur"]

            elif op == "joueur.piocher":
                self.piocher(cmd["joueur_id"], cmd["nb"])
            elif op == "joueur.defausser_choix":
                jid = cmd["joueur_id"]
                cartes = cmd.get("cartes", [])
                joueur = self.joueurs[jid]
                for carte_id in cartes:
                    # on utilise la méthode du Joueur pour garder la logique locale cohérente
                    self.deck_global.jeter(joueur.defausser(carte_id))
            elif op == "joueur.defausser_hasard":
                jid = cmd["joueur_id"]
                joueur = self.joueurs[jid]
                nb = cmd["nb"]
                for _ in range(min(nb, len(joueur.main))):
                    self.deck_global.jeter(joueur.main.pop())

            elif op == "joueur.attention.delta":
                j = self.joueurs[cmd["joueur_id"]]
                j.attention_dispo += cmd["delta"]

            elif op == "joueur.attention.set":
                self.joueurs[cmd["joueur_id"]].attention_dispo = cmd["valeur"]
            elif op == "joueur.reset_attention":
                j = self.joueurs[cmd["joueur_id"]]
                if hasattr(j, "attention_max"):
                    j.attention_dispo = int(j.attention_max)
            elif op == "joueur.jouer_carte":
                joueur_id = cmd["joueur_id"]
                carte_id = cmd["carte_id"]

                # tout le reste de la commande est passé tel quel à jouer_carte
                extra_kwargs = {
                    k: v
                    for k, v in cmd.items()
                    if k not in ("op", "joueur_id", "carte_id")
                }

                ok = self.jouer_carte(joueur_id, carte_id, **extra_kwargs)
                if not ok:
                    self.journaliser(
                        "joueur_jouer_carte_echec",
                        severity="warn",
                        payload=cmd,
                    )
                    self.notifier_joueur(
                        joueur_id,
                        code="CARTE_JOUER_ECHEC",
                        message="Action refusée : la carte ne peut pas être jouée (carte absente de la main ou action invalide).",
                        severity="warn",
                        refs={"op": op, "carte_id": carte_id},
                        payload={"cmd": cmd},
                    )

            elif op == "joueur.vote.set":
                jid = cmd["joueur_id"]
                valeur = int(cmd["valeur"])
                j = self.joueurs.get(jid)

                # 1) joueur inconnu
                if j is None:
                    self.journaliser("vote_refuse_joueur_inconnu", op=op, payload=cmd)
                    return

                # 2) pas habilité à voter
                if not getattr(j, "peut_voter", False):
                    self.journaliser("vote_refuse_pas_habile", op=op, payload=cmd)
                    return

                # 3) déjà confirmé dans l'attente de type VOTE → on ne change plus le bulletin
                if (
                    self.attente.type == "VOTE"
                    and self.attente.statut in ("ATTENTE_REPONSE_JOUEUR", "REPONSES_RECUES")
                    and jid in self.attente.recus
                ):
                    self.journaliser("vote_refuse_deja_confirme", op=op, payload=cmd)
                    return

                # 4) programme absent ou mal initialisé
                if self.programme is None or not hasattr(self.programme, "votes"):
                    self.journaliser("vote_refuse_sans_programme", op=op, payload=cmd)
                    return

                # 5) ok, on enregistre / écrase le vote
                self.programme.votes[jid] = valeur
                self.journaliser("vote_enregistre", op=op, payload=cmd)


            elif op == "joueur.vote.retirer":
                jid = cmd["joueur_id"]
                j = self.joueurs.get(jid)

                if j is None:
                    self.journaliser("vote_retirer_joueur_inconnu", op=op, payload=cmd)
                    return

                if not getattr(j, "peut_voter", False):
                    self.journaliser("vote_retirer_pas_habile", op=op, payload=cmd)
                    return

                if self.programme is not None and hasattr(self.programme, "votes"):
                    self.programme.votes.pop(jid, None)
                    self.journaliser("vote_retire", op=op, payload=cmd)
                else:
                    self.journaliser("vote_retirer_sans_programme", op=op, payload=cmd)


            elif op == "joueur.vote_poids.delta":
                jid = cmd["joueur_id"]
                delta = int(cmd["delta"])
                j = self.joueurs.get(jid)

                if j:
                    # on s'assure de ne pas descendre sous 0
                    j.poids_vote = max(0, getattr(j, "poids_vote", 0) + delta)


            elif op == "joueur.vote_droit.set":
                jid = cmd["joueur_id"]
                peut = bool(cmd["peut_voter"])
                j = self.joueurs.get(jid)

                if j:
                    j.peut_voter = peut


            elif op == "attente.joueurs":
                # Interdiction d’ouvrir une nouvelle attente si l’ancienne n’est pas encore terminée
                if self.attente.statut in ("ATTENTE_REPONSE_JOUEUR", "REPONSES_RECUES"):
                    self.journaliser(
                        "attente_deja_active",
                        type=self.attente.type,
                        joueurs=self.attente.joueurs,
                    )
                    return

                self.attente.init(
                    type=cmd["type"],
                    joueurs=list(cmd.get("joueurs", [])),
                    meta=cmd.get("procedure", {}),
                )


            elif op == "attente.joueur_recu":
                jid = cmd["joueur_id"]
                type_recu = cmd.get("type")  # type d'attente auquel l'interface pense répondre

                # 1) aucune attente en cours
                if self.attente.statut not in ("ATTENTE_REPONSE_JOUEUR", "REPONSES_RECUES"):
                    self.journaliser(
                        "attente_joueur_recu_sans_attente",
                        joueur_id=jid,
                        type_recu=type_recu,
                        attente_type=self.attente.type,
                    )
                    return

                # 2) incohérence sur le type : probablement une réponse en retard
                if self.attente.type is None or type_recu != self.attente.type:
                    self.journaliser(
                        "attente_type_incoherent",
                        joueur_id=jid,
                        type_recu=type_recu,
                        attente_type=self.attente.type,
                    )
                    return

                # 3) ok, on marque la réponse
                self.attente.marquer_recu(jid)

                self.journaliser(
                    f"{jid} a répondu",
                    type=self.attente.type,
                    joueurs=self.attente.joueurs,
                )
                # 4) si tout le monde a répondu, on appelle le skin
                if self.attente.est_complete:
                    if self.regles is not None and self.attente.type is not None:
                        cmds_suiv = self.regles.regle_attente_terminee(self, self.attente.type)
                        if cmds_suiv:
                            self.appliquer_commandes(cmds_suiv)

            elif op == "attente.terminer":
                self.attente.terminer()

            elif op == "joueur.demission_fracassante":
                """
                Le joueur quitte le cabinet de manière spectaculaire.
                On calcule les caractéristiques du remplaçant et on publie un
                évènement de domaine pour que les adapters/skins ajustent
                l'état côté interfaces.
                """
                jid = cmd["joueur_id"]
                mode = cmd.get("mode", "remplacant_moyenne_capital")

                joueur_sortant = self.joueurs[jid]

                # Exemple de calcul : capital du remplaçant = moyenne des autres
                autres_capitaux = [
                    j.capital_politique
                    for j_id, j in self.joueurs.items()
                    if j_id != jid
                ]
                if autres_capitaux:
                    capital_remplacant = int(sum(autres_capitaux) / len(autres_capitaux))
                else:
                    capital_remplacant = int(joueur_sortant.capital_politique)

                # On peut marquer le sortant comme "à l'écart", à ta discrétion
                joueur_sortant.capital_politique = 0
                # éventuellement : joueur_sortant.peut_voter = False, etc.

                # Événement domaine pour le remplaçant : libre à l'UI de l'utiliser
                self.ajouter_evenement(
                    make_evt_from_op(
                        self.id,
                        "joueur.remplacant",
                        {
                            "joueur_sortant": jid,
                            "mode": mode,
                            "capital_remplacant": capital_remplacant,
                        },
                    )
                )

            # règles de fin de tour
            elif op == "joueur.cartes_max_fin_tour.set":
                self.joueurs[cmd["joueur_id"]].cartes_max_fin_tour = cmd["valeur"]

            # ------------------------------------------------------------------
            # D300 – Decks et échanges
            # ------------------------------------------------------------------
            elif op == "deck.defausser_main":
                jid = cmd["joueur_id"]
                main = self.joueurs[jid].main.copy()
                for cid in main:
                    self.jeter_carte(jid, cid)

            elif op == "deck.melanger":
                self.deck_global.melanger()

            elif op == "deck.echanger_joueurs":
                j1 = self.joueurs[cmd["joueur_a"]]
                j2 = self.joueurs[cmd["joueur_b"]]
                j1.main, j2.main = j2.main, j1.main

            elif op == "deck.echange_carte_hasard":
                j1 = self.joueurs[cmd["joueur_a"]]
                j2 = self.joueurs[cmd["joueur_b"]]
                nb = int(cmd.get("nb", 1))
                for _ in range(nb):
                    # On prend la dernière carte de la main (même logique que "hasard" ailleurs)
                    if not j1.main or not j2.main:
                        break
                    c1 = j1.main.pop()
                    c2 = j2.main.pop()
                    j1.main.append(c2)
                    j2.main.append(c1)

            elif op == "deck.echange_carte_choix":
                j1 = self.joueurs[cmd["joueur_a"]]
                j2 = self.joueurs[cmd["joueur_b"]]
                carte_a = cmd["carte_a"]
                carte_b = cmd["carte_b"]

                if carte_a in j1.main and carte_b in j2.main:
                    j1.main.remove(carte_a)
                    j2.main.remove(carte_b)
                    j1.main.append(carte_b)
                    j2.main.append(carte_a)

            # ------------------------------------------------------------------
            # D400 – Événements mondiaux
            # ------------------------------------------------------------------
            elif op == "evt.piocher":
                """
                Pioche un ou plusieurs événements mondiaux et les exécute
                immédiatement.

                Commande attendue :
                  {
                    "op": "evt.piocher",
                    "nombre": 3,  # ou "nb": 3, optionnel, défaut 1
                  }

                Pour chaque carte événement :
                  - on la tire via deck_events.prochain()
                  - on la place dans event_courant
                  - on appelle 'evt.executer' (qui applique les commandes et
                    clôture l'événement).
                Si la pile est vide → on termine la partie.
                """
                nb = int(cmd.get("nombre", cmd.get("nb", 1)))
                if nb <= 0:
                    nb = 1

                for _ in range(nb):
                    evt_id = self.deck_events.prochain()
                    if evt_id:
                        # on indique quel événement est en cours
                        self.event_courant = evt_id
                        # on réutilise la logique existante de evt.executer
                        self.appliquer_commandes([{"op": "evt.executer"}])
                    else:
                        # pile d'événements épuisée → fin de partie
                        self.appliquer_commandes([
                            {
                                "op": "partie.terminer",
                                "raison": "Pile d'événements mondiaux épuisée",
                            }
                        ])
                        break

            elif op == "evt.executer":
                """
                Applique les commandes de l’événement courant, puis le clôture :

                  - exécution des commandes de la carte événement
                  - déplacement de l’événement actif vers la défausse
                  - remise à None de event_courant
                """
                evt_id = getattr(self, "event_courant", None)
                if evt_id:
                    defn = self.cartes_def.get(evt_id, {})
                    commandes = defn.get("commandes")

                    if commandes is None:
                        # fallback legacy: effet.delta_axes -> axes.delta
                        effet = defn.get("effet", {})
                        delta_axes = effet.get("delta_axes", {})
                        commandes = [
                            {"op": "axes.delta", "axe": axe, "delta": int(delta)}
                            for axe, delta in delta_axes.items()
                        ]

                    # on exécute ces commandes via D001
                    self.appliquer_commandes(list(commandes))

                    # clôture de l'événement dans le deck
                    self.deck_events.clore_evt()
                    # et on efface l'événement courant
                    if hasattr(self, "event_courant"):
                        self.event_courant = None


            # ------------------------------------------------------------------
            # D500 – Programme
            # ------------------------------------------------------------------
            elif op == "programme.engager_carte":
                if self.programme is None:
                    self.programme = ProgrammeTour(entrees=[], votes={})

                joueur_id = cmd["joueur_id"]
                carte_id = cmd["carte_id"]
                joueur = self.joueurs.get(joueur_id)

                if not joueur or carte_id not in joueur.main:
                    self.journaliser(
                        "programme_engagement_invalide",
                        joueur_id=joueur_id,
                        carte_id=carte_id,
                    )
                else:
                    defn = self.cartes_def.get(carte_id, {})
                    cout_attention_def = int(defn.get("cout_attention", 0))

                    params = cmd.get("params", {}) or {}
                    effort_attention = int(params.get("effort_attention", 0))

                    if joueur.attention_dispo < (effort_attention + cout_attention_def):
                        self.journaliser(
                            "programme_engagement_attention_insuffisante",
                            joueur_id=joueur_id,
                            carte_id=carte_id,
                            cout_attention=(effort_attention + cout_attention_def),
                            attention_dispo=joueur.attention_dispo,
                        )
                    else:
                        # débit d'attention à l'engagement
                        joueur.attention_dispo -= (effort_attention + cout_attention_def)

                        # retrait de la carte de la main
                        joueur.main.remove(carte_id)

                        entree_type = cmd.get("type", "mesure")
                        uid = cmd.get("uid") or f"EP-{len(self.programme.entrees) + 1}"
                        tags = cmd.get("tags", [])

                        self.programme.entrees.append(EntreeProgramme(
                            uid=uid,
                            auteur_id=joueur_id,
                            carte_id=carte_id,
                            type=entree_type,
                            params=params,
                            tags=tags,
                            attention_engagee=(effort_attention + cout_attention_def),
                        ))

                        self.journaliser(
                            "programme_carte_engagee",
                            joueur_id=joueur_id,
                            carte_id=carte_id,
                            entree_uid=uid,
                            cout_attention=effort_attention,
                        )

            elif op == "programme.retirer_carte":
                """
                Retirer une ou plusieurs cartes engagées avant le vote.

                Commande possible :
                  - par uid :
                      { "op": "programme.retirer_carte", "uid": "EP-001" }
                  - par carte + joueur :
                      {
                        "op": "programme.retirer_carte",
                        "carte_id": "MES-001",
                        "joueur_id": "J000001"
                      }

                Les cartes retirées sont rendues à la main de leurs auteurs.
                """
                if self.programme:
                    uid = cmd.get("uid")
                    joueur_filtre = cmd.get("joueur_id")
                    carte_filtre = cmd.get("carte_id")

                    nouvelles_entrees: list[EntreeProgramme] = []

                    for entree in self.programme.entrees:
                        match = False

                        if uid is not None and entree.uid == uid:
                            match = True
                        elif carte_filtre is not None and entree.carte_id == carte_filtre:
                            if joueur_filtre is None or entree.auteur_id == joueur_filtre:
                                match = True

                        if match:
                            # on rend la carte à son auteur
                            joueur = self.joueurs.get(entree.auteur_id)
                            if joueur is not None:
                                # rendre la carte
                                if entree.carte_id not in joueur.main:
                                    joueur.main.append(entree.carte_id)

                                # rembourser l'attention engagée
                                if getattr(entree, "attention_engagee", 0) > 0:
                                    joueur.attention_dispo += entree.attention_engagee

                            self.journaliser(
                                "programme_carte_retiree",
                                joueur_id=entree.auteur_id,
                                carte_id=entree.carte_id,
                                entree_uid=entree.uid,
                                attention_remboursee=getattr(entree, "attention_engagee", 0),
                            )
                        else:
                            nouvelles_entrees.append(entree)

                    self.programme.entrees = nouvelles_entrees

            elif op == "programme.rejeter":
                """
                Rejet global du programme :

                  - toutes les cartes engagées sont rendues à leurs auteurs ;
                  - l'attention engagée sur ces cartes est remboursée ;
                  - le programme est remis à blanc (entrees + votes) ;
                  - le verdict éventuel est effacé.
                """
                if self.programme is not None:
                    nb_entrees = len(self.programme.entrees)
                    total_attention_remboursee = 0

                    # rendre toutes les cartes aux auteurs + rembourser l'attention
                    for entree in self.programme.entrees:
                        joueur = self.joueurs.get(entree.auteur_id)
                        if joueur is not None:
                            if entree.carte_id not in joueur.main:
                                joueur.main.append(entree.carte_id)

                            att = getattr(entree, "attention_engagee", 0)
                            if att > 0:
                                joueur.attention_dispo += att
                                total_attention_remboursee += att

                    self.journaliser(
                        "programme_rejete",
                        nb_entrees=nb_entrees,
                        attention_remboursee=total_attention_remboursee,
                    )

                    # reset du programme
                    self.programme.entrees.clear()
                    self.programme.votes.clear()

                    if hasattr(self, "programme_verdict"):
                        self.programme_verdict = None

            elif op == "programme.reset":
                """
                Reset après adoption / exécution du programme :

                  - toutes les cartes engagées sont envoyées dans la défausse
                    du deck global (cartes consommées pour ce cycle) ;
                  - on s'assure qu'elles ne traînent plus dans aucune main ;
                  - le programme est remis à blanc (entrees + votes) ;
                  - le verdict est effacé.

                La logique d'exécution des cartes (effets, mérites, etc.)
                est gérée dans le skin avant d'appeler cette opération.
                """
                if self.programme is not None:
                    # 1) défausser toutes les cartes engagées dans le deck global
                    for entree in self.programme.entrees:
                        cid = entree.carte_id

                        # au cas où la carte serait encore dans une main
                        for joueur in self.joueurs.values():
                            if cid in joueur.main:
                                joueur.main.remove(cid)

                        # carte consommée -> défausse globale
                        self.deck_global.jeter(cid)

                    self.journaliser(
                        "programme_reset",
                        nb_entrees=len(self.programme.entrees),
                    )

                    # 2) reset complet du programme
                    self.programme.entrees.clear()
                    self.programme.votes.clear()

                    self.programme.verdict = None

                    # on laisse self.programme exister comme ProgrammeTour vide
                    # ou on peut recréer un objet propre :
                    self.programme = ProgrammeTour(entrees=[], votes={})

            elif op == "programme.intention.set":
                intention = cmd.get("intention")
                if intention is not None:
                    setattr(self, "programme_intention", intention)

            elif op == "programme.verdict.set":
                self.programme.verdict = cmd["adopte"]

            # ------------------------------------------------------------------
            # D700 – Analyse du jeu / cabinet vs opposition
            # ------------------------------------------------------------------
            elif op == "capital_collectif.delta":
                self.capital_collectif += int(cmd["delta"])

            elif op == "capital_collectif.set":
                self.capital_collectif = int(cmd["valeur"])

            elif op == "opposition.capital.delta":
                self.opposition.capital_politique += int(cmd["delta"])

            elif op == "opposition.capital.set":
                self.opposition.capital_politique = int(cmd["valeur"])

            elif op == "analyse.data.set":
                cle = cmd["cle"]
                self.analyse_skin[cle] = cmd.get("valeur")

            elif op == "analyse.data.delta":
                cle = cmd["cle"]
                delta = int(cmd.get("delta", 0))
                current = self.analyse_skin.get(cle, 0)
                if not isinstance(current, (int, float)):
                    current = 0
                self.analyse_skin[cle] = current + delta

            elif op == "opposition.data.set":
                cle = cmd["cle"]
                self.opposition.donnees_skin[cle] = cmd.get("valeur")

            elif op == "opposition.data.delta":
                cle = cmd["cle"]
                delta = int(cmd.get("delta", 0))
                current = self.opposition.donnees_skin.get(cle, 0)
                if not isinstance(current, (int, float)):
                    current = 0
                self.opposition.donnees_skin[cle] = current + delta

            # ------------------------------------------------------------------
            # D800 – Journalisation
            # ------------------------------------------------------------------
            elif op == "journal":
                self.journaliser(cmd.get("type", "journal"), **cmd.get("payload", {}))

            # ------------------------------------------------------------------
            # Cas inconnu
            # ------------------------------------------------------------------
            else:
                self.journaliser("cmd_inconnue", op=op, payload=cmd)


    def avancer_sous_phase(self) -> None:
        """
        Exécute la sous-phase courante via le moteur de règles.

        La décision de la prochaine sous-phase est laissée au skin, qui peut
        renvoyer des commandes "phase.set" dans regle_sous_phase.

        Le manager reste maître de self.phase ("mise_en_place" / "tour" / "fin_jeu").
        """
        if self.phase != "tour":
            return

        # initialisation si nécessaire : si aucune sous-phase n'est définie,
        # on laisse le skin choisir via un signal dédié (ex. "signal.init_tour").
        if self.sous_phase is None:
            if self.regles is None:
                return
            self.sous_phase = "init_tour"
            signal = self.sous_phase_signals.get("init_tour", "signal.init_tour")
            cmds = self.regles.regle_sous_phase(self, signal)
            self.appliquer_commandes(cmds)
        else:
            # on exécute simplement la sous-phase courante
            self._run_subphase(self.sous_phase)

        # à ce stade, le skin a éventuellement changé self.sous_phase
        self.journaliser("phase", phase=self.phase, sous_phase=self.sous_phase)


    # --- Événements de domaine (D100–D600) ---------------------------------

    def ajouter_evenement(self, evt: EvenementDomaine) -> None:
        """Ajoute un événement de domaine dans le buffer."""
        self.evenements.append(evt)

    def vider_evenements(self) -> List[EvenementDomaine]:
        """Récupère et vide le buffer d’événements de domaine."""
        evts = list(self.evenements)
        self.evenements.clear()
        return evts

