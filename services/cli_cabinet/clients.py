# services/cli_cabinet/clients.py

from typing import Any, Dict, Optional

import requests
import httpx
from .settings import settings


class LobbyClient:
    def __init__(self, base_url: Optional[str] = None) -> None:
        self.base_url = base_url or settings.lobby_base_url.rstrip("/")
        self._client = httpx.Client(base_url=settings.lobby_base_url, timeout=5.0)

    def _url(self, path: str) -> str:
        return f"{self.base_url}{path}"

    def _handle_error(self, r: requests.Response) -> None:
        """Lève une erreur plus explicite avec le body de FastAPI."""
        try:
            payload = r.json()
        except Exception:  # noqa: BLE001
            payload = r.text
        raise RuntimeError(f"HTTP {r.status_code} {r.reason}: {payload}")

    # ------------------------------------------------------------------
    # ACC.011 - inscription d’un utilisateur inconnu
    # ------------------------------------------------------------------
    def inscrire_joueur(
        self,
        pseudo: str,
        email: str,
        nom: str,
        mot_de_passe: str,
        alias: str | None = None,
    ) -> Dict[str, Any]:
        payload = {
            "nom": nom,
            "alias": alias or pseudo,   # alias visible = pseudo par défaut
            "courriel": email,
            "mot_de_passe": mot_de_passe,
        }
        r = requests.post(self._url("/api/joueurs"), json=payload, timeout=5)
        if r.status_code >= 400:
            self._handle_error(r)
        return r.json()

    # ------------------------------------------------------------------
    # ACC.021 - authentification d’un utilisateur existant
    # ------------------------------------------------------------------
    def authentifier_joueur(
        self,
        courriel: str,
        mot_de_passe: str,
    ) -> Dict[str, Any]:
        payload = {
            "courriel": courriel,
            "mot_de_passe": mot_de_passe,
        }
        r = requests.post(self._url("/api/sessions"), json=payload, timeout=5)
        if r.status_code >= 400:
            self._handle_error(r)
        return r.json()

    # ------------------------------------------------------------------
    # ACC.111 - gestion des tables
    # ------------------------------------------------------------------
    def lister_tables(self, statut: str | None = None) -> Dict[str, Any]:
        """
        GET /api/tables?statut=...
        Renvoie la ReponseListeTables telle que renvoyée par le lobby.
        """
        params: Dict[str, Any] = {}
        if statut:
            params["statut"] = statut
        r = requests.get(self._url("/api/tables"), params=params, timeout=5)
        if r.status_code >= 400:
            self._handle_error(r)
        return r.json()

    def creer_table(
        self,
        id_hote: str,
        nom_table: str,
        nb_sieges: int = 4,
        mot_de_passe_table: str | None = None,
        skin_jeu: str | None = None,
    ) -> Dict[str, Any]:
        """
        POST /api/tables
        Body = DemandeCreationTable
        """
        payload: Dict[str, Any] = {
            "id_hote": id_hote,
            "nom_table": nom_table,
            "nb_sieges": nb_sieges,
            "mot_de_passe_table": mot_de_passe_table,
            "skin_jeu": skin_jeu,
        }
        # on enlève les champs None pour garder un JSON propre
        payload = {k: v for k, v in payload.items() if v is not None}

        r = requests.post(self._url("/api/tables"), json=payload, timeout=5)
        if r.status_code >= 400:
            self._handle_error(r)
        return r.json()

    def joindre_table(
        self,
        id_table: str,
        id_joueur: str,
        mot_de_passe_table: str | None = None,
    ) -> Dict[str, Any]:
        """
        POST /api/tables/{id_table}/joueurs
        Body = DemandeJoindreTable
        """
        payload: Dict[str, Any] = {
            "id_joueur": id_joueur,
            "mot_de_passe_table": mot_de_passe_table,
        }
        payload = {k: v for k, v in payload.items() if v is not None}

        r = requests.post(
            self._url(f"/api/tables/{id_table}/joueurs"),
            json=payload,
            timeout=5,
        )
        if r.status_code >= 400:
            self._handle_error(r)
        return r.json()

    def joueur_pret(
        self,
        id_table: str,
        id_joueur: str,
    ) -> Dict[str, Any]:
        """
        POST /api/tables/{id_table}/joueurs/pret
        Body = DemandeJoueurPret
        """
        payload = {"id_joueur": id_joueur}
        r = requests.post(
            self._url(f"/api/tables/{id_table}/joueurs/pret"),
            json=payload,
            timeout=5,
        )
        if r.status_code >= 400:
            self._handle_error(r)
        return r.json()

    # ------------------------------------------------------------------
    # ACC.115 - lancer la partie
    # ------------------------------------------------------------------
    def lancer_partie(
        self,
        id_table: str,
        id_hote: str,
    ) -> Dict[str, Any]:
        """
        POST /api/tables/{id_table}/lancer
        Body = DemandeLancerPartie (id_hote)
        """
        payload = {"id_hote": id_hote}
        r = requests.post(
            self._url(f"/api/tables/{id_table}/lancer"),
            json=payload,
            timeout=5,
        )
        if r.status_code >= 400:
            self._handle_error(r)
        return r.json()

    # ------------------------------------------------------------------
    # Health
    # ------------------------------------------------------------------
    def health(self) -> Dict[str, Any]:
        r = requests.get(self._url("/health"), timeout=3)
        if r.status_code >= 400:
            self._handle_error(r)
        return r.json()

