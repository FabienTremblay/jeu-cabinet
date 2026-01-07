from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from .config import ConfigTuiLobby
from .client_lobby import ClientLobby
from .client_moteur import ClientMoteur

import requests


@dataclass
class SessionJoueur:
    """État local d'une session TUI pour un joueur du lobby."""

    cfg: ConfigTuiLobby
    client: ClientLobby
    client_moteur: ClientMoteur | None = None

    id_joueur: Optional[str] = None
    alias: Optional[str] = None
    email: Optional[str] = None
    id_table: Optional[str] = None

    phase: Optional[str] = None
    sous_phase: Optional[str] = None

    partie_en_cours: bool = False
    partie_id: Optional[str] = None

    _evenements: List[Dict[str, Any]] = field(default_factory=list)

    # état de jeu coté moteur
    _etat_partie: Dict[str, Any] = field(default_factory=dict)
    _cartes_joueur: List[Any] = field(default_factory=list)


    # ---------- helpers internes ----------

    def _afficher_header(self) -> None:
        print("\n==============================")
        print(
            f" joueur: {self.alias or '(non inscrit)'}  "
            f" | id: {self.id_joueur or '-'}"
            f" | table: {self.id_table or '-'}"
        )
        print("==============================")

    # ---------- gestion joueur ----------

    def inscrire_ou_recuperer(self) -> None:
        """Ancienne méthode utilisée par ui_minimal (conservée pour compat)."""
        self._afficher_header()

        if self.id_joueur is not None:
            print("joueur déjà connu dans cette session.")
            return

        alias = self.cfg.joueur_alias
        email = self.cfg.joueur_email or f"{alias}@example.com"
        mot_de_passe = "secret"  # pour les tests seulement

        print(f"inscription / récupération du joueur alias={alias}, email={email}…")
        try:
            data = self.client.inscrire_joueur(
                alias=alias,
                email=email,
                mot_de_passe=mot_de_passe,
            )
        except requests.HTTPError as e:
            resp = e.response
            if resp is not None:
                try:
                    err = resp.json()
                    detail = err.get("detail", err)
                except Exception:
                    detail = resp.text
            else:
                detail = str(e)
            print(f"[erreur inscription] {detail}")
            return

        self.id_joueur = data["id_joueur"]
        self.alias = data.get("alias", alias)
        self.email = data.get("courriel", email)

        print(f"joueur connecté : {self.alias} [{self.id_joueur}]")


    def inscrire(self) -> None:
        """Utilisée par la page d'accueil."""
        self.inscrire_ou_recuperer()

    def connecter(self) -> None:
        """
        Connexion d'un joueur existant via /api/sessions.
        Pour l'instant on utilise l'email du config; plus tard tu pourras
        demander l'email/mot de passe à l'utilisateur.
        """
        if self.id_joueur is not None:
            print("joueur déjà connu dans cette session.")
            return

        alias = self.cfg.joueur_alias
        email = self.cfg.joueur_email or f"{alias}@example.com"
        mot_de_passe = "secret"  # même mot de passe que lors de l'inscription de test

        print(f"connexion du joueur courriel={email}…")
        try:
            data = self.client.connecter_joueur(email=email, mot_de_passe=mot_de_passe)
        except requests.HTTPError as e:
            resp = e.response
            if resp is not None:
                try:
                    err = resp.json()
                    detail = err.get("detail", err)
                except Exception:
                    detail = resp.text
            else:
                detail = str(e)
            print(f"[erreur connexion] {detail}")
            return

        self.id_joueur = data["id_joueur"]
        self.alias = data.get("alias", alias)
        self.email = data.get("courriel", email)

        print(f"joueur connecté : {self.alias} [{self.id_joueur}]")



    # ---------- gestion tables ----------

    def lister_tables(self) -> None:
        self._afficher_header()
        tables = self.client.lister_tables()

        if not tables:
            print("aucune table disponible.")
            return

        print("tables :")
        for t in tables:
            tid = t.get("id_table")
            hote = t.get("id_hote")
            nb_max = t.get("nb_sieges")
            statut = t.get("statut")
            skin = t.get("skin_jeu")
            print(f" - {tid} | hôte={hote} | sièges={nb_max} | statut={statut} | skin={skin}")

    def creer_table(self):
        if not self.id_joueur:
            print("Impossible de créer une table : joueur non connecté.")
            return

        # 1) récupérer les skins disponibles
        try:
            skins = self.client.lister_skins()
        except Exception as e:
            print(f"Erreur lors de la récupération des skins : {e}")
            # fallback : aucune contrainte côté TUI
            skin_choisi = None
        else:
            skin_choisi = None
            if not skins:
                print("Aucun skin disponible, la table sera créée sans skin explicite.")
            elif len(skins) == 1:
                unique = skins[0]
                skin_choisi = unique["id_skin"]
                print(
                    f"Un seul skin disponible : {unique['nom']} "
                    f"[{unique['id_skin']}]. Utilisation automatique."
                )
            else:
                print("\nChoisissez un skin pour la table :")
                for idx, skin in enumerate(skins, start=1):
                    desc = f" - {skin.get('description')}" if skin.get("description") else ""
                    print(f"{idx}) {skin['nom']} [{skin['id_skin']}] {desc}")

                while True:
                    choix = input("> ").strip()
                    if not choix.isdigit():
                        print("Veuillez entrer le numéro d'un skin.")
                        continue
                    idx = int(choix)
                    if not (1 <= idx <= len(skins)):
                        print("Numéro hors plage.")
                        continue
                    skin_choisi = skins[idx - 1]["id_skin"]
                    break

        # 2) éventuellement demander le nb de sièges (ou réutiliser une valeur par défaut)
        try:
            nb_str = input("Nombre de sièges (défaut 4) ? ").strip()
            nb_sieges = int(nb_str) if nb_str else 4
        except ValueError:
            print("Valeur invalide, on utilise 4 sièges.")
            nb_sieges = 4

        # 3) appel au lobby
        try:
            rep = self.client.creer_table(
                hote_id=self.id_joueur,
                nb_max=nb_sieges,
                skin_jeu=skin_choisi,
            )
        except Exception as e:
            print(f"Erreur lors de la création de la table : {e}")
            return

        self.id_table = rep.get("id_table")
        print(f"Table créée : {self.id_table} (skin={rep.get('skin_jeu')!r})")

    def rejoindre_table(self) -> None:
        self._afficher_header()

        if self.id_joueur is None:
            print("aucun joueur dans la session, on procède à l'inscription…")
            self.inscrire()

        table_id = input("id de la table à rejoindre : ").strip()
        if not table_id:
            print("id de table vide, abandon.")
            return

        try:
            _ = self.client.rejoindre_table(table_id=table_id, joueur_id=self.id_joueur)
        except requests.HTTPError as e:
            resp = e.response
            if resp is not None:
                try:
                    err = resp.json()
                    detail = err.get("detail", err)
                except Exception:
                    detail = resp.text
            else:
                detail = str(e)
            print(f"[erreur rejoindre table] {detail}")
            return

        self.id_table = table_id
        print(f"joueur {self.alias} a rejoint la table {self.id_table}")


    def se_declarer_pret(self) -> None:
        self._afficher_header()

        if self.id_joueur is None or self.id_table is None:
            print("il faut un joueur et une table pour se déclarer prêt.")
            return

        try:
            _ = self.client.signaler_pret(table_id=self.id_table, joueur_id=self.id_joueur)
        except requests.HTTPError as e:
            resp = e.response
            if resp is not None:
                try:
                    err = resp.json()
                    detail = err.get("detail", err)
                except Exception:
                    detail = resp.text
            else:
                detail = str(e)
            print(f"[erreur joueur prêt] {detail}")
            return

        print(f"joueur {self.alias} s'est déclaré prêt sur la table {self.id_table}")

    def lancer_partie(self) -> None:
        if not (self.id_table and self.id_joueur):
            print("il faut être attaché à une table et avoir un joueur pour lancer la partie.")
            return

        try:
            _ = self.client.lancer_partie(self.id_table, self.id_joueur)
        except requests.HTTPError as e:
            resp = e.response
            if resp is not None:
                try:
                    err = resp.json()
                    detail = err.get("detail", err)
                except Exception:
                    detail = resp.text
            else:
                detail = str(e)
            print(f"[erreur lancement partie] {detail}")
            return

        print("Partie lancée !")
        self.partie_en_cours = True

    # ---------- gestion des événements Kafka ----------

    def ajouter_evenement(self, evt: Dict[str, Any]) -> None:
        """Ajoute un événement reçu de Kafka au buffer local et met à jour un mini état moteur."""
        self._evenements.append(evt)
        if len(self._evenements) > 50:
            self._evenements = self._evenements[-50:]

        # détecter table_id / partie_id
        t_id, p_id = self._extraire_ids_evenement(evt)
        if p_id and not self.partie_id:
            self.partie_id = p_id
        if t_id and not self.id_table:
            self.id_table = t_id

        # --- enrichissement spécifique pour les événements moteur ---
        type_evt = evt.get("event_type") or evt.get("type") or ""
        data = evt.get("data") or evt.get("payload") or {}

        # cas particulier : event.partie.creee → on sait qu'une partie démarre pour ce joueur
        if type_evt == "event.partie.creee" and p_id:
            self.partie_en_cours = True

        # cas D060 : phase.set
        if type_evt in ("cab.D060.phase.set", "cab.D600.phase.set"):
            # data attendu : { "op": "phase.set", "partie_id", "phase", "sous_phase", "tour" (optionnel) }
            phase = data.get("phase")
            sous_phase = data.get("sous_phase")
            tour = data.get("tour")

            if phase:
                self.phase = phase
                self._etat_partie["phase"] = phase
            if sous_phase:
                self.sous_phase = sous_phase
                self._etat_partie["sous_phase"] = sous_phase
            if tour is not None:
                self._etat_partie["tour"] = tour

            if p_id and not self.partie_id:
                self.partie_id = p_id

            self.partie_en_cours = True

            # si on a maintenant un couple (client_moteur, partie_id) et aucun état complet,
            # on peut tenter un premier rafraîchissement silencieux
            if self.client_moteur and self.partie_id and not self._etat_partie.get("joueurs"):
                try:
                    self.rafraichir_etat_partie()
                except Exception:
                    # on garde l'état minimal (phase/sous_phase/tour) même si le GET échoue
                    pass

        if type_evt == "cab.D600.journal":
            msg = data.get("message") or data.get("msg")
            if msg:
                self._dernier_journal = msg

        if type_evt.startswith("cab.D200.joueur"):
            if self.client_moteur and self.partie_id:
                try:
                    self.rafraichir_etat_partie()
                except:
                    pass



    def afficher_evenements(self) -> None:
        self._afficher_header()

        if not self._evenements:
            print("aucun événement reçu pour le moment.")
            return

        print("derniers événements (du plus ancien au plus récent) :")
        for i, evt in enumerate(self._evenements, start=1):
            type_evt = evt.get("type") or evt.get("event_type") or "?"
            j_id = evt.get("id_joueur")
            t_id = evt.get("id_table")
            payload = evt.get("payload") or evt.get("data") or {}

            # petit enrichissement pour certains types d'événements
            details = ""
            if type_evt in ("cab.D060.phase.set", "cab.D600.phase.set") and isinstance(payload, dict):
                ph = payload.get("phase")
                sp = payload.get("sous_phase")
                if ph or sp:
                    details = f" (phase={ph}, sous_phase={sp})"
            elif type_evt == "event.partie.creee" and isinstance(payload, dict):
                nom = payload.get("nom")
                pid = payload.get("partie_id")
                if nom or pid:
                    details = f" (partie={pid}, nom={nom})"
            if type_evt.startswith("cab."):
                prefix = "[MOTEUR]"
            else:
                prefix = "[LOBBY]"

            print(f"[{i}] {prefix} {type_evt} joueur={j_id} table={t_id}{details}")

    def afficher_vue_lobby(self, max_events: int = 10) -> None:
        """Vue 'triptyque' pour le lobby (joueur non assis)."""

        self._afficher_header()

        print("=== Lobby (gauche) ===")

        # Joueurs présents dans le lobby
        try:
            joueurs_lobby = self.client.lister_joueurs_lobby()
        except Exception as e:
            print(f"[erreur lister joueurs lobby] {e}")
            joueurs_lobby = []

        if joueurs_lobby:
            print("joueurs dans le lobby :")
            for j in joueurs_lobby:
                alias = j.get("alias") or j.get("nom") or "?"
                jid = j.get("id_joueur")
                print(f" - {alias} [{jid}]")
        else:
            print("aucun joueur dans le lobby (visible).")

        print("\nTables ouvertes (en_preparation) :")
        try:
            tables_ouvertes = self.client.lister_tables()
        except Exception as e:
            print(f"[erreur lister tables] {e}")
            tables_ouvertes = []

        if tables_ouvertes:
            for t in tables_ouvertes:
                print(
                    f" - {t.get('id_table')} | nom={t.get('nom_table')} "
                    f"| hôte={t.get('id_hote')} | sièges={t.get('nb_sieges')} "
                    f"| statut={t.get('statut')}"
                )
        else:
            print(" (aucune table)")

        print("\n=== Événements récents (droite) ===")
        if not self._evenements:
            print("aucun événement reçu pour le moment.")
            return

        derniers = self._evenements[-max_events:]
        offset = len(self._evenements) - len(derniers)
        for idx, evt in enumerate(derniers, start=offset + 1):
            type_evt = evt.get("type") or evt.get("event_type") or "?"
            j_id = evt.get("id_joueur")
            t_id = evt.get("id_table")
            payload = evt.get("payload") or evt.get("data") or {}
            if j_id is None and isinstance(payload, dict):
                j_id = payload.get("id_joueur")
            if t_id is None and isinstance(payload, dict):
                t_id = payload.get("id_table") 
            print(f"[{idx}] type={type_evt} joueur={j_id} table={t_id}")

    def afficher_vue_table(self, max_events: int = 10) -> None:
        """Vue 'triptyque' pour une table où le joueur est assis."""

        self._afficher_header()

        print("=== Table (gauche) ===")

        if not self.id_table:
            print("aucune table courante dans la session.")
            return

        # Détails de la table courante
        try:
            rep = self.client.lister_joueurs_table(self.id_table)
            joueurs_table = rep.get("joueurs", [])
        except Exception as e:
            print(f"[erreur lister joueurs table] {e}")
            joueurs_table = []

        print(f"Table actuelle : {self.id_table}")
        if joueurs_table:
            print(" joueurs à la table :")
            for jt in joueurs_table:
                alias = jt.get("alias") or jt.get("nom") or "?"
                jid = jt.get("id_joueur")
                role = jt.get("role")
                pret = jt.get("pret")
                marque_pret = "✅" if pret else "…"
                print(f" - {alias} [{jid}] | role={role} | prêt={marque_pret}")
        else:
            print(" aucun joueur listé pour cette table (encore).")

        print("\nTables en cours de jeu (en_jeu) :")
        try:
            tables = self.client.lister_tables()
        except Exception as e:
            print(f"[erreur lister tables] {e}")
            tables = []

        tables_en_jeu = [t for t in tables if t.get("statut") == "en_jeu"]
        if tables_en_jeu:
            for t in tables_en_jeu:
                print(
                    f" - {t.get('id_table')} | nom={t.get('nom_table')} "
                    f"| hôte={t.get('id_hote')} | sièges={t.get('nb_sieges')}"
                )
        else:
            print(" (aucune autre table en_jeu)")

        print("\n=== Événements récents (droite) ===")
        if not self._evenements:
            print("aucun événement reçu pour le moment.")
            return

        derniers = self._evenements[-max_events:]
        offset = len(self._evenements) - len(derniers)
        for idx, evt in enumerate(derniers, start=offset + 1):
            type_evt = evt.get("type") or evt.get("event_type") or "?"
            j_id = evt.get("id_joueur")
            t_id = evt.get("id_table")
            payload = evt.get("payload") or evt.get("data") or {}
            if j_id is None and isinstance(payload, dict):
                j_id = payload.get("id_joueur")
            if t_id is None and isinstance(payload, dict):
                t_id = payload.get("id_table")
            print(f"[{idx}] type={type_evt} joueur={j_id} table={t_id}")

    def detecter_evenement(self, type_evt_recherche: str) -> bool:
        """Retourne True s'il existe un événement de ce type (optionnellement filtré sur la table courante)."""
        for evt in self._evenements:
            type_evt = evt.get("type") or evt.get("event_type")
            if type_evt != type_evt_recherche:
                continue
            # si l'événement inclut un table_id, on vérifie qu'il correspond
            t_id = evt.get("id_table")
            if t_id is not None and self.id_table is not None and t_id != self.id_table:
                continue
            return True
        return False

    def rafraichir_position_table(self) -> None:
        """
        Tente de déterminer sur quelle table est assis le joueur courant.
        Si self.id_table est déjà renseigné, on vérifie qu'il y est encore.
        Sinon, on cherche dans toutes les tables.
        """
        if self.id_joueur is None:
            return

        # 1) si on croit déjà connaître la table, on vérifie
        if self.id_table:
            try:
                rep = self.client.lister_joueurs_table(self.id_table)
                for j in rep.get("joueurs", []):
                    if j.get("id_joueur") == self.id_joueur:
                        return  # toujours assis ici
            except Exception:
                pass
            # plus trouvé sur cette table
            self.id_table = None

        # 2) sinon, on cherche dans toutes les tables
        try:
            tables = self.client.lister_tables()
        except Exception:
            return

        for t in tables:
            t_id = t.get("id_table") or t.get("id")
            if not t_id:
                continue
            try:
                rep = self.client.lister_joueurs_table(t_id)
            except Exception:
                continue
            for j in rep.get("joueurs", []):
                if j.get("id_joueur") == self.id_joueur:
                    self.id_table = t_id
                    self.est_dans_partie_active()
                    return

    def verifier_si_partie_lancee(self) -> bool:
        """
        Utilisé pour basculer vers la page de jeu.
        Ne considère PartieLancee que si :
        - le joueur est assis à une table
        - l'événement concerne cette table
        - et on en profite pour capturer partie_id si présent.
        """
        if self.partie_en_cours:
            return True

        if self.id_table is None:
            return False

        for evt in self._evenements:
            type_evt = evt.get("type") or evt.get("event_type")
            if type_evt != "PartieLancee":
                continue

            t_id, p_id = self._extraire_ids_evenement(evt)

            # si l'événement ne concerne pas la table courante, on ignore
            if t_id is not None and t_id != self.id_table:
                continue

            # là, oui : la partie de MA table est lancée
            if p_id and not getattr(self, "partie_id", None):
                self.partie_id = p_id
                print(f"(info) partie_id détecté pour la table {self.id_table} : {self.partie_id}")

            self.partie_en_cours = True
            return True

        return False

    def _extraire_ids_evenement(self, evt: dict) -> tuple[str | None, str | None]:
        """Retourne (table_id, partie_id) en analysant toutes les variantes possibles."""

        # --- 1) extraction directe à la racine ---
        table_id = evt.get("id_table")
        partie_id = evt.get("id_partie")
        joueur_id = evt.get("id_joueur")

        # --- 2) extraction dans le payload ---
        payload = evt.get("payload") or evt.get("data") or {}
        if isinstance(payload, dict):
            table_id = table_id or payload.get("id_table")
            partie_id = partie_id or payload.get("id_partie")
            joueur_id = joueur_id or payload.get("id_joueur")

        # --- 3) fallback générique pour formats inconnus ---
        if table_id is None and isinstance(payload, dict):
            for k, v in payload.items():
                if "table" in k.lower():
                    table_id = v
                    break

        if partie_id is None and isinstance(payload, dict):
            for k, v in payload.items():
                if "partie" in k.lower():
                    partie_id = v
                    break

        return table_id, partie_id


    def est_dans_partie_active(self) -> bool:
        """
        Détermine si le joueur est déjà dans une partie active.
        Utilise d'abord l'état local (partie_en_cours), puis le statut de la table
        côté lobby, puis éventuellement les événements (PartieLancee).
        """
        # 1) déjà marqué en cours → rien à faire
        if getattr(self, "partie_en_cours", False):
            return True

        # 2) sans table, aucune partie pour ce joueur
        if not self.id_table:
            return False

        # 3) interroger le lobby pour connaître le statut de cette table
        try:
            toutes = self.client.lister_tables()
        except Exception:
            toutes = []

        for t in toutes:
            t_id = t.get("id_table") or t.get("id")
            if t_id != self.id_table:
                continue
            statut = t.get("statut")
            if statut == "en_jeu":
                self.partie_en_cours = True
                return True
            break  # on a trouvé la table, inutile de continuer

        # 4) à défaut, on laisse une chance à Kafka:
        if self.verifier_si_partie_lancee():
            return True

        return False

    # ---------- intégration avec l'api-moteur ----------

    def rafraichir_etat_partie(self) -> None:
        """
        Appelle /parties/{partie_id}/etat et garde une copie locale.
        Tente aussi d'extraire les cartes du joueur dans l'état.
        """
        if not self.client_moteur:
            return
        if not self.partie_id:
            # on essaie de voir si une PartieLancee n'a pas déjà donné un id
            if not self.verifier_si_partie_lancee():
                return

        try:
            rep = self.client_moteur.lire_etat(self.partie_id)  # type: ignore[arg-type]
        except Exception as e:
            print(f"[erreur lecture état partie] {e}")
            return

        # ReponseEtat { "partie_id", "etat": {...} }
        etat = rep.get("etat", rep)
        self._etat_partie = etat if isinstance(etat, dict) else {}
        self._extraire_cartes_joueur_depuis_etat()

    # ---------- helpers dérivés de l'état moteur ----------

    @property
    def _etat(self) -> Dict[str, Any]:
        """Alias pratique vers l'état courant renvoyé par le moteur."""
        return self._etat_partie or {}

    @property
    def _historiques(self) -> List[Dict[str, Any]]:
        """Liste des entrées d'historique dans l'état courant."""
        hist = self._etat.get("historiques")
        return hist if isinstance(hist, list) else []

    @property
    def _cartes_def(self) -> Dict[str, Any]:
        """Dictionnaire des définitions de cartes (mesures + événements)."""
        cartes = self._etat.get("cartes_def")
        return cartes if isinstance(cartes, dict) else {}

    @property
    def _programme(self) -> Dict[str, Any]:
        """Programme courant (programme du tour)."""
        prog = self._etat.get("programme")
        return prog if isinstance(prog, dict) else {}

    @property
    def _joueurs_map(self) -> Dict[str, Any]:
        """Dictionnaire id_joueur -> données joueur issues de l'état."""
        joueurs = self._etat.get("joueurs")
        return joueurs if isinstance(joueurs, dict) else {}

    @property
    def _attente(self) -> dict:
        """Attente courante renvoyée par le moteur (ou dict vide)."""
        att = self._etat_partie.get("attente") if isinstance(self._etat_partie, dict) else None
        return att if isinstance(att, dict) else {}

    @property
    def attente_brute(self) -> Dict[str, Any]:
        """Attente telle que renvoyée par l'état, ou dict vide."""
        att = self._etat_partie.get("attente") if isinstance(self._etat_partie, dict) else None
        return att if isinstance(att, dict) else {}

    @property
    def attente_active(self) -> Optional[Dict[str, Any]]:
        """
        Attente active : statut == "ATTENTE_REPONSE_JOUEUR".
        Retourne None si aucune attente active.
        """
        att = self.attente_brute
        if not att:
            return None
        if att.get("statut") != "ATTENTE_REPONSE_JOUEUR":
            return None
        return att

    def _extraire_cartes_joueur_depuis_etat(self) -> None:
        self._cartes_joueur = []

        if not self._etat_partie or not self.id_joueur:
            return

        joueurs = self._etat_partie.get("joueurs")
        if isinstance(joueurs, dict):
            j = joueurs.get(self.id_joueur)
            if isinstance(j, dict):
                for cle in ("main", "cartes", "cartes_main"):
                    val = j.get(cle)
                    if isinstance(val, list):
                        self._cartes_joueur = val
                        return

    def _calculer_palmares_local(self) -> List[Dict[str, Any]]:
        """
        Calcule un classement provisoire des joueurs à partir de l'état.

        Pour l'instant :
          - critère principal : capital_politique décroissant
          - bris d'égalité : nom de joueur croissant

        Plus tard, on pourra aligner ça avec les véritables conditions de
        victoire (prestige, contentieux résolus, etc.) définies par le skin.
        """
        palmares: List[Dict[str, Any]] = []

        joueurs = self._joueurs_map
        if not joueurs:
            return palmares

        for jid, jdata in joueurs.items():
            if not isinstance(jdata, dict):
                continue
            nom = jdata.get("nom") or jid
            capital = jdata.get("capital_politique", 0)
            poids_vote = jdata.get("poids_vote", 1)
            peut_voter = bool(jdata.get("peut_voter", True))

            entree = {
                "id": jid,
                "nom": nom,
                "capital": capital,
                "poids_vote": poids_vote,
                "peut_voter": peut_voter,
            }
            palmares.append(entree)

        # tri : capital_politique décroissant, puis nom
        palmares.sort(key=lambda e: (-int(e["capital"]), str(e["nom"])))
        return palmares

    def envoyer_action(
        self,
        type_action: str,
        donnees: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Wrapper pour POST /parties/{partie_id}/actions.
        """
        if not self.client_moteur:
            print("aucun client moteur configuré.")
            return
        if not self.partie_id or not self.id_joueur:
            print("il faut une partie et un joueur pour envoyer une action.")
            return

        try:
            rep = self.client_moteur.soumettre_action(
                partie_id=self.partie_id,
                acteur=self.id_joueur,
                type_action=type_action,
                donnees=donnees or {},
            )
        except requests.HTTPError as e:
            resp = e.response
            if resp is not None:
                try:
                    err = resp.json()
                    detail = err.get("detail", err)
                except Exception:
                    detail = resp.text
            else:
                detail = str(e)
            print(f"[erreur envoi action] {detail}")
            return
        except Exception as e:
            print(f"[erreur envoi action] {e}")
            return

        # si l'api renvoie un état, on l'exploite
        etat = rep.get("etat")
        if isinstance(etat, dict):
            self._etat_partie = etat
            self._extraire_cartes_joueur_depuis_etat()

    def jouer_carte_hors_programme(self) -> None:
        """
        Permet au joueur de jouer une carte directement (op = 'joueur.jouer_carte'),
        distinct de l'engagement dans le programme.

        On ne passe pas par executer_action_ui pour éviter la double sélection :
        on construit directement le payload et on le complète avec
        _completer_payload_jouer_carte.
        """
        # s'assurer que la main est à jour
        if hasattr(self, "_extraire_cartes_joueur_depuis_etat"):
            self._extraire_cartes_joueur_depuis_etat()

        main = getattr(self, "_cartes_joueur", None)
        if not main:
            print("aucune carte en main.")
            return

        print("=== jouer une carte (hors programme) ===")
        self.afficher_ressources_joueur_courant()
        print()
        for i, carte in enumerate(main, start=1):
            if isinstance(carte, dict):
                code = carte.get("code") or carte.get("id") or ""
            else:
                code = str(carte)

            nom = ""
            def_carte = self._cartes_def.get(code) if self._cartes_def else None
            if isinstance(def_carte, dict):
                nom = def_carte.get("nom") or ""

            resume = self._resumer_carte(code) if code else ""

            ligne = f"{i:2d}) {code}"
            if nom:
                ligne += f" – {nom}"

            # <<< COÛT D’ATTENTION >>>
            cout_att = self._estimer_cout_attention_carte(code)
            if cout_att:
                ligne += f" [att={cout_att}]"

            if resume:
                ligne += f" | {resume}"

            print(ligne)

        s = input("numéro de la carte à jouer (Entrée pour annuler) : ").strip()
        if not s:
            return
        try:
            idx = int(s)
        except ValueError:
            print("entrée invalide.")
            return
        if not (1 <= idx <= len(main)):
            print("numéro hors limites.")
            return

        carte_sel = main[idx - 1]
        if isinstance(carte_sel, dict):
            carte_id = carte_sel.get("code") or carte_sel.get("id") or str(carte_sel)
        else:
            carte_id = str(carte_sel)

        # payload de base
        payload: Dict[str, Any] = {
            "joueur_id": self.id_joueur,
            "carte_id": carte_id,
        }

        # compléter avec cible_id / effort_cp / effort_attention si nécessaire
        complet = self._completer_payload_jouer_carte(payload)
        if complet is None:
            print("[ui] action 'jouer une carte' annulée.")
            return

        # envoi direct au moteur
        self.envoyer_action(type_action="joueur.jouer_carte", donnees=complet)


    def executer_action_ui(self, action_def: Dict[str, Any]) -> None:
        """
        Construit le payload à partir de action_def["fields"]
        en fonction de domain, et envoie l'action.
        """
        op = action_def.get("op")
        if not op:
            print("[ui] action sans 'op'")
            return

        payload: Dict[str, Any] = {}
        fields = action_def.get("fields") or []

        for field in fields:
            nom = field.get("name")
            if not nom:
                continue
            domain = field.get("domain")
            required = bool(field.get("required", False))
            label = field.get("label") or nom

            value = None

            # domain sous forme simple
            if isinstance(domain, str):
                if domain == "joueur_id":
                    value = self.id_joueur

                elif domain == "attente_type":
                    # type imposé par l'attente active
                    att = self.attente_active or self.attente_brute
                    if not att:
                        print("[ui] aucune attente pour remplir 'type'.")
                        if required:
                            return
                        value = None
                    else:
                        value = att.get("type")
                        if value is None and required:
                            print("[ui] attente sans 'type' pour remplir 'type'.")
                            return

                elif domain == "carte_main":
                    value = self._choisir_carte_dans_main(label)
                elif domain == "int":
                    value = self._saisir_valeur(label + " (entier) : ", type_="int")
                elif domain == "string":
                    value = self._saisir_valeur(label + " : ", type_="str")
                else:
                    # inconnu → fallback sur un input texte
                    value = self._saisir_valeur(label + " : ", type_="str")

            # domain sous forme de dict (ex. choix)
            elif isinstance(domain, dict):
                kind = domain.get("kind")
                if kind == "choice":
                    values = domain.get("values") or []
                    value = self._saisir_choix(label, values)
                else:
                    value = self._saisir_valeur(label + " : ", type_="str")

            else:
                # pas de domain → input libre
                value = self._saisir_valeur(label + " : ", type_="str")

            if required and value is None:
                print(f"[ui] champ obligatoire ignoré : {nom}")
                return

            if value is not None:
                payload[nom] = value

        # Post-traitement pour certaines ops
        if op == "joueur.jouer_carte":
            complet = self._completer_payload_jouer_carte(payload)
            if complet is None:
                print("[ui] action 'joueur.jouer_carte' annulée.")
                return
            payload = complet

        self.envoyer_action(type_action=op, donnees=payload)

    def _completer_payload_jouer_carte(self, payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Complète le payload d'une action 'joueur.jouer_carte' en fonction de
        la définition de la carte (cartes_def).

        - cible_id : si au moins une commande contient joueur_id == "_cible"
        - effort_cp : si une commande joueur.capital.delta a delta == "_effort"
        - effort_attention : si une commande joueur.attention.delta a delta == "_effort"
        """
        carte_id = payload.get("carte_id")
        if not carte_id:
            print("[ui] carte_id manquant pour joueur.jouer_carte.")
            return None

        def_carte = self._cartes_def.get(carte_id)
        if not def_carte:
            print(f"[ui] définition inconnue pour la carte {carte_id}.")
            # on laisse passer tel quel, le moteur décidera
            return payload

        commandes = def_carte.get("commandes") or []
        commandes = [c for c in commandes if isinstance(c, dict)]

        # --- 1) besoin d'une cible ? ---
        besoin_cible = any(c.get("joueur_id") == "_cible" for c in commandes)

        if besoin_cible:
            joueurs = (self._etat_partie or {}).get("joueurs") or {}
            # tous les autres joueurs de la partie
            autres = [
                (jid, j.get("nom") or jid)
                for jid, j in joueurs.items()
                if jid != self.id_joueur
            ]

            if not autres:
                print("[ui] aucune cible possible : aucun autre joueur dans la partie.")
                return None

            print("\nChoisissez la cible pour cette carte :")
            for idx, (jid, nom) in enumerate(autres, start=1):
                print(f"{idx}) {nom} [{jid}]")

            while True:
                s = input("Votre choix (numéro) : ").strip()
                try:
                    i = int(s)
                except ValueError:
                    print("Veuillez entrer un numéro.")
                    continue
                if 1 <= i <= len(autres):
                    cible_id = autres[i - 1][0]
                    payload["cible_id"] = cible_id
                    break
                else:
                    print("Numéro hors limites.")

        # --- 2) besoins d'effort_cp / effort_attention ? ---
        besoin_effort_cp = any(
            c.get("op") == "joueur.capital.delta" and c.get("delta") == "_effort"
            for c in commandes
        )
        besoin_effort_attention = any(
            c.get("op") == "joueur.attention.delta" and c.get("delta") == "_effort"
            for c in commandes
        )

        if besoin_effort_cp:
            while True:
                s = input("Effort de capital politique (entier >= 0) : ").strip()
                try:
                    n = int(s)
                except ValueError:
                    print("Veuillez entrer un entier.")
                    continue
                if n < 0:
                    print("La valeur doit être >= 0.")
                    continue
                payload["effort_cp"] = n
                break

        if besoin_effort_attention:
            # on peut tenter de guider avec l'attention disponible
            attention_dispo = None
            try:
                jdata = (self._etat_partie or {}).get("joueurs", {}).get(self.id_joueur, {})
                attention_dispo = jdata.get("attention_dispo")
            except Exception:
                pass

            if isinstance(attention_dispo, (int, float)):
                prompt = f"Effort d'attention (entier, max {int(attention_dispo)}) : "
            else:
                prompt = "Effort d'attention (entier >= 0) : "

            while True:
                s = input(prompt).strip()
                try:
                    n = int(s)
                except ValueError:
                    print("Veuillez entrer un entier.")
                    continue
                if n < 0:
                    print("La valeur doit être >= 0.")
                    continue
                if isinstance(attention_dispo, (int, float)) and n > attention_dispo:
                    print("Valeur supérieure à l'attention disponible.")
                    continue
                payload["effort_attention"] = n
                break

        return payload

    def _saisir_valeur(self, prompt: str, type_: str = "str"):
        while True:
            s = input(prompt).strip()
            if type_ == "int":
                try:
                    return int(s)
                except ValueError:
                    print("Veuillez entrer un entier.")
                    continue
            else:
                return s

    def _saisir_choix(self, label: str, values) -> Any:
        """
        values peut être [1, 0] ou une liste de dicts {"value", "label"}.
        """
        if not values:
            return None

        # normaliser
        norm = []
        for v in values:
            if isinstance(v, dict):
                norm.append((v.get("value"), v.get("label", str(v.get("value")))))
            else:
                norm.append((v, str(v)))

        print(label)
        for i, (val, lab) in enumerate(norm, start=1):
            print(f" {i}) {lab}")

        while True:
            s = input("Votre choix : ").strip()
            try:
                idx = int(s)
            except ValueError:
                print("Entrez un numéro.")
                continue
            if not (1 <= idx <= len(norm)):
                print("Numéro hors limites.")
                continue
            return norm[idx - 1][0]

    def _choisir_carte_dans_main(self, label: str) -> Optional[str]:
        """
        Propose la main du joueur avec les caractéristiques de chaque carte,
        et retourne l'id de la carte choisie (string).
        Retourne None si l'utilisateur annule.
        """
        # si nécessaire, on ré-extrait depuis l'état
        if not self._cartes_joueur and self._etat_partie:
            self._extraire_cartes_joueur_depuis_etat()

        if not self._cartes_joueur:
            print("Vous n'avez aucune carte en main.")
            return None

        print("\n=== cartes disponibles ===")
        for i, carte in enumerate(self._cartes_joueur, start=1):
            if isinstance(carte, dict):
                cid = carte.get("id") or carte.get("code") or str(carte)
                nom = carte.get("nom") or carte.get("label") or cid
                resume = carte.get("resume") or carte.get("description", "")
            else:
                cid = str(carte)
                def_carte = self._cartes_def.get(cid, {}) if self._cartes_def else {}
                nom = def_carte.get("nom") or def_carte.get("label") or cid
                resume = def_carte.get("resume") or def_carte.get("description", "")

            cout_att = self._estimer_cout_attention_carte(cid)

            ligne = f"{i:2d}) {cid} – {nom}"
            if cout_att:
                ligne += f" [att={cout_att}]"
            print(ligne)

            if resume:
                print(f"     {resume}")

        while True:
            s = input(
                f"{label} (numéro 1-{len(self._cartes_joueur)} ou Entrée pour annuler) : "
            ).strip()

            # permettre d'annuler
            if s == "":
                return None

            try:
                idx = int(s)
            except ValueError:
                print("Veuillez entrer un numéro valide.")
                continue

            if not (1 <= idx <= len(self._cartes_joueur)):
                print("Numéro invalide.")
                continue

            carte = self._cartes_joueur[idx - 1]
            if isinstance(carte, dict):
                cid = carte.get("id") or carte.get("code") or str(carte)
            else:
                cid = str(carte)

            print(f"Vous avez choisi la carte {cid}.")
            return cid

    # ---------- vues de jeu ----------


    def afficher_fenetre_statut_partie(self) -> None:
        etat = self._etat_partie or {}
        partie_id = etat.get("id")
        tour = etat.get("tour")
        phase = etat.get("phase")
        sous_phase = etat.get("sous_phase")
        termine = bool(etat.get("termine"))
        raison_fin = etat.get("raison_fin")

        print("=== statut de la partie ===")
        print(f"table : {self.id_table}")
        print(f"partie : {partie_id}")
        print(f"en cours : {'non' if termine else 'oui'}")
        if tour is not None:
            print(f"tour : {tour}")
        if phase:
            print(f"phase : {phase}")
        if sous_phase:
            print(f"sous-phase : {sous_phase}")
        if termine and raison_fin:
            print(f"fin : {raison_fin}")

    def afficher_fenetre_journal(self, max_lignes: int = 10) -> None:
        """
        Affiche les dernières entrées de journal (type == 'journal').

        On enrichit avec carte_id / evenement_id quand possible,
        en se basant sur cartes_def de l'état.
        """
        print("=== journal du tour ===")

        journaux = [h for h in self._historiques if h.get("type") == "journal"]
        if not journaux:
            print("(journal vide)")
            return

        journaux = journaux[-max_lignes:]

        for h in journaux:
            tour = h.get("tour", "?")
            msg = h.get("message", "")
            prefix = f"[T{tour}] "

            # carte ?
            carte_id = h.get("carte_id")
            if carte_id:
                carte_def = self._cartes_def.get(carte_id, {})
                nom_carte = carte_def.get("nom", carte_id)
                prefix += f"[{carte_id} – {nom_carte}] "

            # événement mondial ?
            evt_id = h.get("evenement_id")
            if evt_id:
                evt_def = self._cartes_def.get(evt_id, {})
                nom_evt = evt_def.get("nom", evt_id)
                prefix += f"[{evt_id} – {nom_evt}] "

            print(prefix + msg)


    def afficher_fenetre_evenements_jeu(self, max_lignes: int = 15) -> None:
        """
        Affiche les événements de jeu issus des historiques
        (tout ce qui n'est pas 'journal').

        Ajoute un marquage [ANALYSE] pour les événements D700 / ANALYSE :
          - family == "D700"
          - category == "ANALYSE"
          - ou op commence par capital_collectif./opposition./analyse.
        """
        print("=== événements de jeu (historiques) ===")

        evts = [h for h in self._historiques if h.get("type") != "journal"]
        if not evts:
            print("(aucun événement de jeu)")
            return

        evts = evts[-max_lignes:]

        for i, h in enumerate(evts, start=1):
            tour = h.get("tour")
            t = h.get("type")

            op = h.get("op")
            famille = h.get("family") or h.get("famille")
            categorie = h.get("category") or h.get("categorie")

            base = f"[{i}] "
            if tour is not None:
                base += f"[T{tour}] "

            # Détection des événements d’analyse (D700)
            is_analyse = (
                categorie == "ANALYSE"
                or famille == "D700"
                or (isinstance(op, str) and op.startswith(("capital_collectif.", "opposition.", "analyse.")))
            )
            prefix = "[ANALYSE] " if is_analyse else ""

            if t == "piocher":
                joueur = h.get("joueur") or h.get("joueur_id") or "?"
                cartes_brutes = h.get("cartes") or []
                if not isinstance(cartes_brutes, (list, tuple)):
                    cartes_brutes = [cartes_brutes]
                cartes = ", ".join(str(c) for c in cartes_brutes)
                print(f"{base}{prefix}type=piocher joueur={joueur} cartes=[{cartes}]")

            elif t == "phase":
                phase = h.get("phase")
                sous_phase = h.get("sous_phase")
                if sous_phase:
                    print(f"{base}{prefix}type=phase phase={phase} / {sous_phase}")
                else:
                    print(f"{base}{prefix}type=phase phase={phase} / None")

            elif t == "programme_carte_engagee":
                joueur_id = h.get("joueur_id") or h.get("joueur") or "?"
                carte_id = h.get("carte_id") or h.get("carte") or "?"
                entree_uid = h.get("entree_uid")
                cout_attention = h.get("cout_attention")

                extra_bits: list[str] = []
                if entree_uid:
                    extra_bits.append(f"entree={entree_uid}")
                if cout_attention is not None:
                    extra_bits.append(f"cout_attention={cout_attention}")
                extra = " ".join(extra_bits)

                print(
                    f"{base}{prefix}type=programme_carte_engagee "
                    f"joueur={joueur_id} carte={carte_id}"
                    + (f" {extra}" if extra else "")
                )

            elif t == "programme_reset":
                nb_entrees = h.get("nb_entrees")
                if nb_entrees is not None:
                    print(f"{base}{prefix}type=programme_reset nb_entrees={nb_entrees}")
                else:
                    print(f"{base}{prefix}type=programme_reset")

            elif t == "ENGAGER_CARTE":
                joueurs = h.get("joueurs") or []
                if not joueurs:
                    print(f"{base}{prefix}type=ENGAGER_CARTE (aucun joueur en attente)")
                else:
                    joueurs_str = ", ".join(joueurs)
                    print(f"{base}{prefix}type=ENGAGER_CARTE joueurs=[{joueurs_str}]")

            elif t == "VOTE":
                joueurs = h.get("joueurs") or []
                if not joueurs:
                    print(f"{base}{prefix}type=VOTE (aucun joueur en attente)")
                else:
                    joueurs_str = ", ".join(joueurs)
                    print(f"{base}{prefix}type=VOTE joueurs=[{joueurs_str}]")

            elif t == "vote_enregistre":
                joueur_id = h.get("joueur") or h.get("joueur_id") or "?"
                vote_val = h.get("vote") or h.get("valeur")
                payload = h.get("payload") or {}
                print(
                    f"{base}{prefix}type=vote_enregistre "
                    f"joueur={joueur_id} vote={vote_val} payload={payload}"
                )

            else:
                # Cas générique : on affiche tout ce qu'on trouve,
                # en gardant le préfixe [ANALYSE] si applicable.
                extra = {
                    k: v
                    for k, v in h.items()
                    if k not in ("tour", "type", "family", "famille", "category", "categorie")
                }
                if op is not None and "op" not in extra:
                    extra["op"] = op
                print(f"{base}{prefix}type={t} {extra}")


    def afficher_fenetre_programme(self) -> None:
        """
        Affiche le programme du cabinet (cartes engagées et votes),
        surtout pertinent en PHASE_PROGRAMME / PHASE_VOTE / PHASE_RESOLUTION.
        """
        sous_phase = self._etat_partie.get("sous_phase")
        prog = self._programme

        print("=== programme du cabinet ===")

        if not prog:
            print("(aucun programme en cours)")
            return

        # Optionnel : n'afficher quelque chose de détaillé que dans ces sous-phases
        phases_pertinentes = {"PHASE_PROGRAMME", "PHASE_VOTE", "PHASE_RESOLUTION"}
        if sous_phase not in phases_pertinentes:
            print(f"(programme présent mais sous-phase={sous_phase})")

        version = prog.get("version")
        if version is not None:
            print(f"version : {version}")

        entrees = prog.get("entrees") or []
        if not entrees:
            print("(aucune carte engagée dans le programme)")
        else:
            print("cartes engagées :")
            for i, e in enumerate(entrees, start=1):
                uid = e.get("uid") or "?"
                carte_id = e.get("carte_id") or "?"
                auteur_id = e.get("auteur_id") or "?"
                type_entree = e.get("type") or "?"

                carte_def = self._cartes_def.get(carte_id, {})
                nom_carte = carte_def.get("nom", carte_id)

                joueur = self._joueurs_map.get(auteur_id, {})
                nom_joueur = joueur.get("nom", auteur_id)

                # coût en attention : valeur fournie par l'état, sinon estimation locale
                label_cout = None
                if "cout_attention" in e and e.get("cout_attention") is not None:
                    label_cout = str(e.get("cout_attention"))
                else:
                    est = self._estimer_cout_attention_carte(carte_id)
                    if est:
                        label_cout = est

                ligne = (
                    f" {i:2d}) [{uid}] {carte_id} – {nom_carte} "
                    f"(auteur : {nom_joueur} [{auteur_id}], type={type_entree})"
                )
                if label_cout is not None:
                    ligne += f" | att={label_cout}"

                print(ligne)



        # votes
        votes = prog.get("votes") or {}
        joueurs = self._joueurs_map

        print("\nétat des votes :")
        if not votes and not joueurs:
            print("(aucune information sur les votes)")
            return

        if votes:
            print("votes enregistrés :")
            for jid, val in votes.items():
                j = joueurs.get(jid, {})
                nom = j.get("nom", jid)
                print(f" - {nom} [{jid}] : {val}")
        else:
            print("(aucun vote enregistré pour l'instant)")

        # joueurs en attente de vote (si on est en PHASE_VOTE)
        if sous_phase == "PHASE_VOTE" and joueurs:
            en_attente = []
            for jid, j in joueurs.items():
                if j.get("peut_voter") and jid not in votes:
                    en_attente.append((jid, j.get("nom", jid)))
            if en_attente:
                print("\njoueurs en attente de vote :")
                for jid, nom in en_attente:
                    print(f" - {nom} [{jid}]")

    def _estimer_cout_attention_carte(self, carte_id: str) -> str | None:
        """
        Estime le coût en attention d'une carte à partir de sa définition.

        - Si la carte contient des commandes joueur.attention.delta avec un delta numérique,
          on prend la somme des deltas (valeur absolue, pour afficher un coût positif).
        - Si la carte contient un delta == "_effort", on retourne "effort".
        - Si on ne trouve rien d'exploitable, on retourne None.
        """
        def_carte = self._cartes_def.get(carte_id) if self._cartes_def else None
        if not isinstance(def_carte, dict):
            return None

        commandes = def_carte.get("commandes") or []
        if not isinstance(commandes, list):
            return None

        total_num = 0
        a_un_effort = False

        for cmd in commandes:
            if not isinstance(cmd, dict):
                continue
            if cmd.get("op") != "joueur.attention.delta":
                continue

            delta = cmd.get("delta")
            if isinstance(delta, (int, float)):
                total_num += delta
            elif delta == "_effort":
                a_un_effort = True

        # Cas "effort" seulement
        if a_un_effort and total_num == 0:
            return "effort"

        # Cas mixte numérique + effort
        if a_un_effort and total_num != 0:
            return f"{abs(int(total_num))}+effort"

        # Cas purement numérique
        if total_num != 0:
            return str(abs(int(total_num)))

        return None

    def _resumer_carte(self, carte_id: str) -> str:
        """
        Produit un petit résumé textuel des effets de la carte.

        On couvre :
          - axes.delta          -> "axe +X" / "axe -X"
          - eco.delta_depenses  -> "depenses poste +X" / "-X"
          - eco.delta_dette     -> "dette +X" / "-X"
          - eco.delta_recettes  -> "recettes base +X" / "-X"
          - joueur.capital.delta      -> "capital +X" / "-X"
          - joueur.attention.delta    -> "attention +X" / "-X"
          - capital_collectif.delta   -> "capital collectif +X" / "-X"
          - joueur.piocher            -> "pioche +nb"
        """
        def_carte = self._cartes_def.get(carte_id) if self._cartes_def else None
        if not isinstance(def_carte, dict):
            return ""

        commandes = def_carte.get("commandes") or []
        if not isinstance(commandes, list):
            return ""

        effets: list[str] = []

        for cmd in commandes:
            if not isinstance(cmd, dict):
                continue
            op = cmd.get("op")

            # 1) axes.delta
            if op == "axes.delta":
                axe = cmd.get("axe")
                delta = cmd.get("delta")
                if isinstance(axe, str) and isinstance(delta, (int, float)):
                    signe = "+" if delta > 0 else ""
                    effets.append(f"{axe} {signe}{delta}")
                continue

            # 2) eco.delta_depenses
            if op == "eco.delta_depenses":
                postes = cmd.get("postes") or {}
                if isinstance(postes, dict):
                    for poste, delta in postes.items():
                        if isinstance(delta, (int, float)):
                            signe = "+" if delta > 0 else ""
                            effets.append(f"depenses {poste} {signe}{delta}")
                continue

            # 3) eco.delta_dette
            if op == "eco.delta_dette":
                delta = cmd.get("montant")
                if isinstance(delta, (int, float)):
                    signe = "+" if delta > 0 else ""
                    effets.append(f"dette {signe}{delta}")
                continue

            # 4) eco.delta_recettes
            if op == "eco.delta_recettes":
                bases = cmd.get("bases") or {}
                if isinstance(bases, dict):
                    for base, delta in bases.items():
                        if isinstance(delta, (int, float)):
                            signe = "+" if delta > 0 else ""
                            effets.append(f"recettes {base} {signe}{delta}")
                continue

            # 5) joueur.capital.delta
            if op == "joueur.capital.delta":
                delta = cmd.get("delta")
                if isinstance(delta, (int, float)):
                    signe = "+" if delta > 0 else ""
                    effets.append(f"capital {signe}{delta}")
                continue

            # 6) joueur.attention.delta
            if op == "joueur.attention.delta":
                delta = cmd.get("delta")
                if isinstance(delta, (int, float)):
                    signe = "+" if delta > 0 else ""
                    effets.append(f"attention {signe}{delta}")
                continue

            # 7) capital_collectif.delta
            if op == "capital_collectif.delta":
                delta = cmd.get("delta")
                if isinstance(delta, (int, float)):
                    signe = "+" if delta > 0 else ""
                    effets.append(f"capital collectif {signe}{delta}")
                continue

            # 8) joueur.piocher
            if op == "joueur.piocher":
                nb = cmd.get("nb")
                if isinstance(nb, int) and nb != 0:
                    signe = "+" if nb > 0 else ""
                    effets.append(f"pioche {signe}{nb}")
                continue

        return "; ".join(effets)

    def _get_ressources_joueur_courant(self) -> Optional[Dict[str, Any]]:
        """
        Retourne un petit dict avec les ressources du joueur courant
        (capital, attention dispo/max) si disponibles dans l'état moteur.
        """
        if not self._etat_partie:
            return None

        joueurs = self._etat_partie.get("joueurs") or {}
        jdata = joueurs.get(self.id_joueur)
        if not isinstance(jdata, dict):
            return None

        return {
            "nom": jdata.get("nom") or self.alias or self.id_joueur,
            "capital": jdata.get("capital_politique"),
            "attention_dispo": jdata.get("attention_dispo"),
            "attention_max": jdata.get("attention_max"),
        }

    def afficher_ressources_joueur_courant(self) -> None:
        """
        Affiche une ligne compacte du type :
          ressources joueur : capital=5 | attention=2/2
        """
        info = self._get_ressources_joueur_courant()
        if not info:
            return

        cap = info.get("capital")
        att_d = info.get("attention_dispo")
        att_m = info.get("attention_max")

        # on reste sobre : si une info manque, on ne casse pas l'affichage
        morceaux = []
        if cap is not None:
            morceaux.append(f"capital={cap}")
        if att_d is not None and att_m is not None:
            morceaux.append(f"attention={att_d}/{att_m}")
        elif att_d is not None:
            morceaux.append(f"attention={att_d}")

        if morceaux:
            print(f"ressources joueur : " + " | ".join(morceaux))

    def afficher_fenetre_cartes(self) -> None:
        print("=== cartes du joueur ===")
        self.afficher_ressources_joueur_courant()
        print()

        # si l'état est là mais que les cartes n'ont pas encore été extraites, on tente une extraction
        if not self._cartes_joueur and self._etat_partie:
            self._extraire_cartes_joueur_depuis_etat()

        if not self._cartes_joueur:
            print("(aucune carte détectée dans l'état courant)")
            return

        for i, carte in enumerate(self._cartes_joueur, start=1):
            # normalisation : on veut un id de carte (code) et un nom
            if isinstance(carte, dict):
                code = carte.get("code") or carte.get("id") or ""
                nom = carte.get("nom") or carte.get("label") or ""
            else:
                code = str(carte)
                nom = ""

            # résumé des effets depuis cartes_def
            resume = self._resumer_carte(code) if code else ""

            ligne = f"{i:2d}) {code} {nom}".strip()

            # <<< AJOUT IMPORTANT : coût d’attention estimé >>>
            cout_att = self._estimer_cout_attention_carte(code)
            if cout_att:
                ligne += f" [att={cout_att}]"

            if resume:
                ligne += f" | {resume}"

            print(ligne)

    def afficher_detail_carte(self) -> None:
        """
        Permet de choisir une carte dans la main et d'en afficher le détail complet.
        """
        # s'assurer que la main est à jour
        if not self._cartes_joueur and self._etat_partie:
            self._extraire_cartes_joueur_depuis_etat()

        if not self._cartes_joueur:
            print("aucune carte en main.")
            return

        # réafficher la liste simple pour choisir
        print("=== cartes du joueur ===")
        for i, carte in enumerate(self._cartes_joueur, start=1):
            if isinstance(carte, dict):
                code = carte.get("code") or carte.get("id") or ""
                nom = carte.get("nom") or carte.get("label") or ""
            else:
                code = str(carte)
                nom = ""
            print(f"{i:2d}) {code} {nom}".strip())

        s = input("numéro de la carte à détailler (Entrée pour annuler) : ").strip()
        if not s:
            return
        try:
            idx = int(s)
        except ValueError:
            print("entrée invalide.")
            return
        if not (1 <= idx <= len(self._cartes_joueur)):
            print("numéro hors limites.")
            return

        carte_sel = self._cartes_joueur[idx - 1]
        if isinstance(carte_sel, dict):
            carte_id = carte_sel.get("code") or carte_sel.get("id") or str(carte_sel)
        else:
            carte_id = str(carte_sel)

        self._afficher_detail_carte_par_id(carte_id)

    def _afficher_detail_carte_par_id(self, carte_id: str) -> None:
        """
        Affiche une vue détaillée de la carte : métadonnées + commandes.
        """
        def_carte = self._cartes_def.get(carte_id)
        if not def_carte:
            print(f"carte inconnue : {carte_id}")
            input("\n(Entrée pour revenir à la vue jeu) ")
            return

        print("\n=== détail de la carte ===")
        print(f"id : {carte_id}")
        nom = def_carte.get("nom") or def_carte.get("label") or "-"
        print(f"nom : {nom}")
        print(f"type : {def_carte.get('type') or '-'}")

        copies = def_carte.get("copies")
        if copies is not None:
            print(f"copies dans le deck : {copies}")

        resume = def_carte.get("resume") or def_carte.get("description")
        if resume:
            print(f"\nrésumé : {resume}")

        commandes = def_carte.get("commandes") or []
        if commandes:
            print("\ncommandes :")
            for cmd in commandes:
                print(f" - {cmd}")

        input("\n(Entrée pour revenir à la vue jeu) ")

    def afficher_fenetre_palmares(self) -> None:
        """
        Affiche le palmarès des joueurs, avec le capital collectif en en-tête.
        """
        print("=== palmarès des joueurs ===")

        if not self._etat_partie:
            print("(aucune information de palmarès : aucun état moteur)")
            return

        # capital collectif global
        capital_collectif = self._etat_partie.get("capital_collectif")
        if capital_collectif is not None:
            print(f"capital collectif (cabinet) : {capital_collectif}")

        opposition = self._etat_partie.get("opposition") or {}
        if isinstance(opposition, dict):
            opp_capital = opposition.get("capital_politique")
        else:
            opp_capital = None

        if opp_capital is not None:
            print(f"capital politique (opposition) : {opp_capital}")


        joueurs = self._etat_partie.get("joueurs") or {}
        if not isinstance(joueurs, dict) or not joueurs:
            print("(aucun joueur dans l'état de la partie)")
            return

        # classement par capital politique décroissant
        classement = sorted(
            joueurs.values(),
            key=lambda j: j.get("capital_politique", 0),
            reverse=True,
        )

        for rang, j in enumerate(classement, start=1):
            jid = j.get("id") or "?"
            nom = j.get("nom", jid)
            capital = j.get("capital_politique", 0)
            voix = j.get("poids_vote", 0)
            peut_voter = "✅" if j.get("peut_voter", False) else "❌"

            statut_vote = "peut voter" if peut_voter else "ne peut pas voter"
            print(f" {rang}. {nom} [{jid}] | capital={capital} | voix={voix} ({statut_vote})")

    def afficher_fenetre_attente(self) -> None:
        att = self._attente
        if not att.get("active"):
            return  # pas d'attente, rien à afficher

        meta = att.get("meta") or {}
        code = meta.get("code") or att.get("type") or "?"
        titre = meta.get("titre") or f"Attente {code}"
        desc = meta.get("description") or ""

        print("=== attente en cours ===")
        print(f"type : {code}")
        print(f"titre : {titre}")
        if desc:
            print(desc)

        # optionnel : afficher les actions annoncées par le skin
        ui = meta.get("ui") or {}
        actions = ui.get("actions") or []
        if actions:
            print("\nActions possibles :")
            for i, a in enumerate(actions, start=1):
                print(f" {i}) {a.get('label', a.get('op'))}")

