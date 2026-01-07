import requests
from .config import ConfigTuiLobby


class ClientLobby:
    def __init__(self, config: ConfigTuiLobby):
        self.cfg = config

    def _url(self, path: str) -> str:
        return f"{self.cfg.base_url_lobby}{self.cfg.lobby_prefix}{path}"

    # --- joueurs ---

    def inscrire_joueur(self, alias: str, email: str, mot_de_passe: str) -> dict:
        payload = {
            "nom": alias,
            "alias": alias,
            "courriel": email,
            "mot_de_passe": mot_de_passe,
        }
        r = requests.post(self._url("/joueurs"), json=payload, timeout=5)
        r.raise_for_status()
        return r.json()

    def connecter_joueur(self, email: str, mot_de_passe: str) -> dict:
        payload = {
            "courriel": email,
            "mot_de_passe": mot_de_passe,
        }
        r = requests.post(self._url("/sessions"), json=payload, timeout=5)
        r.raise_for_status()
        return r.json()

    def lister_joueurs_lobby(self) -> list[dict]:
        """
        GET /api/joueurs/lobby
        -> { "joueurs": [ ... ] }
        """
        r = requests.get(self._url("/joueurs/lobby"), timeout=5)
        r.raise_for_status()
        data = r.json()
        return data.get("joueurs", [])

    def lister_joueurs_table(self, id_table: str) -> dict:
        """
        GET /api/tables/{id_table}/joueurs
        -> { "id_table": "...", "joueurs": [ ... ] }
        """
        r = requests.get(self._url(f"/tables/{id_table}/joueurs"), timeout=5)
        r.raise_for_status()
        return r.json()

    # --- tables ---

    def lister_tables(self, statut: str | None = None) -> list[dict]:
        """
        GET /api/tables?statut=en_preparation|en_jeu|...
        -> ReponseListeTables { "tables": [...] }
        """
        params = {}
        if statut:
            params["statut"] = statut
        r = requests.get(self._url("/tables"), params=params or None, timeout=5)
        r.raise_for_status()
        data = r.json()
        if isinstance(data, dict) and "tables" in data:
            return data["tables"]
        return data

    def creer_table(
        self,
        hote_id: str,
        nb_max: int = 4,
        skin_jeu: str | None = None,
    ) -> dict:
        payload = {
            "id_hote": hote_id,
            "nom_table": f"table-{hote_id}",
            "nb_sieges": nb_max,
            "mot_de_passe_table": None,
        }
        if skin_jeu is not None:
            payload["skin_jeu"] = skin_jeu

        r = requests.post(self._url("/tables"), json=payload, timeout=5)
        r.raise_for_status()
        return r.json()

    def rejoindre_table(self, table_id: str, joueur_id: str) -> dict:
        payload = {
            "id_joueur": joueur_id,
            "role": "invite",
        }
        r = requests.post(
            self._url(f"/tables/{table_id}/joueurs"),
            json=payload,
            timeout=5,
        )
        r.raise_for_status()
        return r.json()

    def signaler_pret(self, table_id: str, joueur_id: str) -> dict:
        payload = {
            "id_joueur": joueur_id,
        }
        r = requests.post(
            self._url(f"/tables/{table_id}/joueurs/pret"),
            json=payload,
            timeout=5,
        )
        r.raise_for_status()
        return r.json()

    def lancer_partie(self, table_id: str, hote_id: str) -> dict:
        payload = {"id_hote": hote_id}
        r = requests.post(
            self._url(f"/tables/{table_id}/lancer"),
            json=payload,
            timeout=5,
        )
        r.raise_for_status()
        return r.json()

    # --- skins ---

    def lister_skins(self) -> list[dict]:
        """
        GET /api/skins
        -> { "skins": [ ... ] }
        """
        r = requests.get(self._url("/skins"), timeout=5)
        r.raise_for_status()
        data = r.json()
        return data.get("skins", [])

