from __future__ import annotations

from typing import Any, Dict, Optional

import requests

from .config import ConfigTuiLobby


class ClientMoteur:
    """
    Client très simple pour l'API moteur, basé sur le swagger fourni.
    - POST /parties
    - GET  /parties/{partie_id}/etat
    - POST /parties/{partie_id}/actions
    - POST /parties/{partie_id}/cloture-tour
    """

    def __init__(self, config: ConfigTuiLobby):
        self.cfg = config

    def _url(self, path: str) -> str:
        # l'api-moteur n'a pas de /api par défaut dans le swagger
        return f"{self.cfg.base_url_moteur}{path}"

    # --- parties ---

    def creer_partie(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        r = requests.post(self._url("/parties"), json=payload, timeout=5)
        r.raise_for_status()
        return r.json()

    def lire_etat(self, partie_id: str) -> Dict[str, Any]:
        """
        GET /parties/{partie_id}/etat
        -> ReponseEtat { "partie_id": "...", "etat": {...} }
        """
        r = requests.get(
            self._url(f"/parties/{partie_id}/etat"),
            timeout=5
        )
        r.raise_for_status()
        return r.json()

    def soumettre_action(
        self,
        partie_id: str,
        acteur: str,
        type_action: str,
        donnees: Optional[Dict[str, Any]] = None,
        idempotency_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        POST /parties/{partie_id}/actions
        body: RequeteAction { "acteur", "type_action", "donnees" }
        """
        headers: Dict[str, str] = {}
        if idempotency_key:
            headers["Idempotency-Key"] = idempotency_key

        payload = {
            "acteur": acteur,
            "type_action": type_action,
            "donnees": donnees or {},
        }

        r = requests.post(
            self._url(f"/parties/{partie_id}/actions"),
            json=payload,
            headers=headers or None,
            timeout=5,
        )
        r.raise_for_status()
        return r.json()

