# services/ui_etat_joueur/repository.py
from __future__ import annotations

from datetime import datetime
import copy

from typing import Any, Dict, Iterable, List, Optional

from .domaine import ActionDisponible, EtatJoueurUI


class DepotEtatsUI:
    """
    Dépôt en mémoire des états projetés côté UI, indexés par joueur.
    """

    def __init__(self) -> None:
        self._par_joueur: Dict[str, EtatJoueurUI] = {}

    # --- normalisation (contrat journal v1) ---
    _CATEGORIES_AUTORISEES = {"DEROULEMENT", "ACTION", "SYSTEME", "TECH", "MESSAGE"}
    _SEVERITES_AUTORISEES = {"info", "warn", "error"}
    _AUDIENCE_SCOPES_AUTORISES = {"joueur", "all", "liste"}

    def _normaliser_category(self, value: Optional[str], op_code: Optional[str] = None) -> Optional[str]:
        if value in self._CATEGORIES_AUTORISEES:
            return value
        if op_code:
            if op_code.startswith("partie."):
                return "SYSTEME"
            if op_code.startswith("attente."):
                return "ACTION"
            if op_code.startswith("notif.") or op_code.startswith("journal"):
                return "MESSAGE"
        return "TECH"

    def _normaliser_severity(self, value: Optional[str]) -> Optional[str]:
        if value in self._SEVERITES_AUTORISEES:
            return value
        if not value:
            return "info"
        v = value.lower().strip()
        if v in {"warning"}:
            return "warn"
        if v in {"err", "fatal"}:
            return "error"
        if v in {"ok", "passed"}:
            return "info"
        if v in self._SEVERITES_AUTORISEES:
            return v
        return "info"

    def _valider_audience_pour_joueur(
        self, joueur_id: str, audience: Optional[Dict[str, Any]]
    ) -> None:
        """
        Patch strict :
        - Le journal est stocké PAR JOUEUR (EtatJoueurUI.journal_recent).
        - Donc l'audience doit être soit None, soit {"scope":"joueur","joueur_id":<meme joueur>}.

        Les diffusions "all" / "liste" sont acceptées seulement avant duplication,
        puis doivent être converties en audience joueur lors du stockage.
        """
        if audience is None:
            return
        scope = (audience.get("scope") or "").strip()
        if scope not in self._AUDIENCE_SCOPES_AUTORISES:
            raise ValueError(f"Audience invalide: scope={scope!r}")

        if scope != "joueur":
            raise ValueError(
                "Audience incohérente : une entrée stockée dans le journal d'un joueur "
                "doit avoir scope='joueur' (ou audience=None)."
            )

        aud_jid = audience.get("joueur_id")
        if aud_jid != joueur_id:
            raise ValueError(
                f"Audience incohérente : joueur_id={joueur_id!r} mais audience.joueur_id={aud_jid!r}"
            )

    # --- accès de base ---

    def obtenir_ou_creer(self, joueur_id: str) -> EtatJoueurUI:
        if joueur_id not in self._par_joueur:
            self._par_joueur[joueur_id] = EtatJoueurUI(joueur_id=joueur_id)
        return self._par_joueur[joueur_id]

    def tous(self) -> Dict[str, EtatJoueurUI]:
        return self._par_joueur

    # --- ancrage / navigation ---

    def ancrer_joueur_partie(self, joueur_id: str, partie_id: str) -> None:
        etat = self.obtenir_ou_creer(joueur_id)
        etat.ancrage.type = "partie"
        etat.ancrage.partie_id = partie_id
        etat.ancrage.table_id = None

    def ancrer_joueur_table(self, joueur_id: str, table_id: str) -> None:
        etat = self.obtenir_ou_creer(joueur_id)
        etat.ancrage.type = "table"
        etat.ancrage.table_id = table_id
        etat.ancrage.partie_id = None

    def ancrer_joueur_lobby(self, joueur_id: str) -> None:
        """
        Ancre le joueur sur le lobby (ni table, ni partie).
        """
        etat = self.obtenir_ou_creer(joueur_id)
        etat.ancrage.type = "lobby"
        etat.ancrage.table_id = None
        etat.ancrage.partie_id = None

    # --- vue par partie ---

    def joueurs_par_partie(self, partie_id: str) -> Iterable[tuple[str, EtatJoueurUI]]:
        for jid, etat in self._par_joueur.items():
            if etat.ancrage.partie_id == partie_id:
                yield jid, etat

    # --- état de partie (phase / sous-phase / tour) ---

    def maj_etat_partie_par_partie(
        self,
        partie_id: str,
        phase: Optional[str] = None,
        sous_phase: Optional[str] = None,
        tour: Optional[int] = None,
    ) -> None:
        for _, etat_joueur in self.joueurs_par_partie(partie_id):
            if phase is not None:
                etat_joueur.etat_partie.phase = phase
            if sous_phase is not None:
                etat_joueur.etat_partie.sous_phase = sous_phase
            if tour is not None:
                etat_joueur.etat_partie.tour = tour

    # --- marqueurs (par partie ou par joueur) ---

    def maj_marqueur_partie_par_partie(
        self, partie_id: str, when: datetime
    ) -> None:
        for _, etat_joueur in self.joueurs_par_partie(partie_id):
            etat_joueur.marqueurs.partie = when

    def maj_marqueur_actions_par_partie(
        self, partie_id: str, when: datetime
    ) -> None:
        for _, etat_joueur in self.joueurs_par_partie(partie_id):
            etat_joueur.marqueurs.actions = when

    def maj_marqueur_actions_pour_joueurs(
        self, joueurs_ids: Iterable[str], when: datetime
    ) -> None:
        for jid in joueurs_ids:
            etat = self.obtenir_ou_creer(jid)
            etat.marqueurs.actions = when

    def maj_marqueur_info_axes_par_partie(
        self, partie_id: str, when: datetime
    ) -> None:
        for _, etat_joueur in self.joueurs_par_partie(partie_id):
            etat_joueur.marqueurs.info_axes = when

    def maj_marqueur_info_cartes_par_partie(
        self, partie_id: str, when: datetime
    ) -> None:
        for _, etat_joueur in self.joueurs_par_partie(partie_id):
            etat_joueur.marqueurs.info_cartes = when

    # --- actions disponibles ---

    def definir_actions_pour_joueur(
        self, joueur_id: str, actions: List[ActionDisponible]
    ) -> None:
        etat = self.obtenir_ou_creer(joueur_id)
        etat.set_actions(actions)

    def vider_actions_pour_joueur(self, joueur_id: str) -> None:
        etat = self.obtenir_ou_creer(joueur_id)
        etat.reset_actions()

    def vider_actions_pour_joueurs(self, joueurs_ids: Iterable[str]) -> None:
        for jid in joueurs_ids:
            self.vider_actions_pour_joueur(jid)

    def vider_actions_par_partie(self, partie_id: str) -> None:
        for jid, _ in self.joueurs_par_partie(partie_id):
            self.vider_actions_pour_joueur(jid)

    # --- journal ---

    def ajouter_entree_journal(
        self,
        joueur_id: str,
        message: str,
        event_id: Optional[str] = None,
        occurred_at: Optional[datetime] = None,
        category: Optional[str] = None,
        severity: Optional[str] = None,
        code: Optional[str] = None,
        meta: Optional[Dict[str, Any]] = None,
        audience: Optional[Dict[str, Any]] = None,
        op_code: Optional[str] = None,
        raw: Optional[dict] = None,
    ) -> None:
        # Normalisations
        cat = self._normaliser_category(category, op_code=op_code)
        sev = self._normaliser_severity(severity)

        # Patch strict : audience cohérente avec le stockage par joueur
        self._valider_audience_pour_joueur(joueur_id, audience)

        etat = self.obtenir_ou_creer(joueur_id)
        etat.ajouter_journal(
            message=message,
            event_id=event_id,
            occurred_at=occurred_at,
            category=cat,
            severity=sev,
            code=code,
            meta=meta,
            audience=audience,
            raw=raw,
        )

    def ajouter_entree_journal_partie(
        self,
        partie_id: str,
        message: str,
        event_id: Optional[str] = None,
        occurred_at: Optional[datetime] = None,
        category: Optional[str] = None,
        severity: Optional[str] = None,
        code: Optional[str] = None,
        meta: Optional[Dict[str, Any]] = None,
        audience: Optional[Dict[str, Any]] = None,
        op_code: Optional[str] = None,
        raw: Optional[dict] = None,
    ) -> None:
        base_audience = copy.deepcopy(audience) if audience else None
        for jid, _ in self.joueurs_par_partie(partie_id):
            # Patch strict : lors d'une diffusion, on stocke par joueur => audience joueur
            aud = {"scope": "joueur", "joueur_id": jid} if base_audience else None
            self.ajouter_entree_journal(
                joueur_id=jid,
                message=message,
                event_id=event_id,
                occurred_at=occurred_at,
                category=category,
                severity=severity,
                code=code,
                meta=meta,
                audience=aud,
                op_code=op_code,
                raw=raw,
            )

    def journal_par_recipients(
        self,
        aggregate_id: Optional[str],
        recipients: list[str],
        message: str,
        event_id: Optional[str] = None,
        occurred_at: Optional[datetime] = None,
        category: Optional[str] = None,
        severity: Optional[str] = None,
        code: Optional[str] = None,
        meta: Optional[Dict[str, Any]] = None,
        audience: Optional[Dict[str, Any]] = None,
        op_code: Optional[str] = None,
        raw: Optional[dict] = None,
    ) -> None:
        if not recipients:
            return

        if recipients == ["ALL"] and aggregate_id is not None:
            self.ajouter_entree_journal_partie(
                partie_id=aggregate_id,
                message=message,
                event_id=event_id,
                occurred_at=occurred_at,
                category=category,
                severity=severity,
                code=code,
                meta=meta,
                # Patch strict : on accepte audience "all" ici comme sémantique de diffusion,
                # mais ajouter_entree_journal_partie convertira en audience joueur au stockage.
                audience=audience,
                raw=raw,
            )
        else:
            for jid in recipients:
                self.ajouter_entree_journal(
                    joueur_id=jid,
                    message=message,
                    event_id=event_id,
                    occurred_at=occurred_at,
                    category=category,
                    severity=severity,
                    code=code,
                    meta=meta,
                    audience={"scope": "joueur", "joueur_id": jid} if audience else None,
                    op_code=op_code,
                    raw=raw,
                )

