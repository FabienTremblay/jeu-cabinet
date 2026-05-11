# services/lobby/tests/test_api_lobby.py
# rôle        : vérifie l'API HTTP du lobby
# usage       : tests pytest avec TestClient FastAPI
# contexte    : inscriptions, tables, sièges et politique de timeout
# statut      : actif
from __future__ import annotations

from typing import Any

from services.lobby.domaine import StatutTable


def _inscrire(client: Any, email: str, nom: str, mot_de_passe: str, alias: str):
    rep = client.post(
        "/api/joueurs",
        json={
            "nom": nom,
            "alias": alias,
            "courriel": email,
            "mot_de_passe": mot_de_passe,
        },
    )
    assert rep.status_code == 200
    return rep.json()


def _auth(client: Any, email: str, mot_de_passe: str):
    rep = client.post(
        "/api/sessions",
        json={"courriel": email, "mot_de_passe": mot_de_passe},
    )
    assert rep.status_code == 200
    return rep.json()


def _headers_session(auth: dict[str, Any]) -> dict[str, str]:
    return {"Authorization": f"Bearer {auth['jeton_session']}"}


def test_parcours_acc_happy_path(client: Any):
    # 1) Inscription joueur 1
    j1 = _inscrire(
        client,
        email="joueur1@example.com",
        nom="Joueur Un",
        mot_de_passe="secret1",
        alias="Alias1",
    )

    # 2) Auth joueur 1
    auth_j1 = _auth(client, "joueur1@example.com", "secret1")
    assert auth_j1["id_joueur"] == j1["id_joueur"]

    # 3) Création table
    rep = client.post(
        "/api/tables",
        headers=_headers_session(auth_j1),
        json={
            "id_hote": j1["id_joueur"],
            "nom_table": "Table test multi",
            "nb_sieges": 2,
        },
    )
    assert rep.status_code == 200
    table = rep.json()
    assert table["id_table"].startswith("T")
    assert table["statut"] == StatutTable.OUVERTE.value
    assert table["politique_timeout_partie"] == {
        "version": 1,
        "active": True,
        "delai_inactivite_secondes": 3600,
    }

    # 4) Inscription + auth joueur 2
    j2 = _inscrire(
        client,
        email="joueur2@example.com",
        nom="Joueur Deux",
        mot_de_passe="secret2",
        alias="Alias2",
    )
    auth_j2 = _auth(client, "joueur2@example.com", "secret2")
    assert auth_j2["id_joueur"] == j2["id_joueur"]

    # 5) Joueur 2 rejoint la table
    rep = client.post(
        f"/api/tables/{table['id_table']}/joueurs",
        headers=_headers_session(auth_j2),
        json={
            "id_joueur": j2["id_joueur"],
            "role": "invite",
        },
    )
    assert rep.status_code == 200
    siege = rep.json()
    assert siege["id_joueur"] == j2["id_joueur"]
    assert siege["statut_table"] == StatutTable.EN_PREPARATION.value

    # 6) Joueurs prêts
    rep = client.post(
        f"/api/tables/{table['id_table']}/joueurs/pret",
        headers=_headers_session(auth_j1),
        json={"id_joueur": j1["id_joueur"]},
    )
    assert rep.status_code == 200

    rep = client.post(
        f"/api/tables/{table['id_table']}/joueurs/pret",
        headers=_headers_session(auth_j2),
        json={"id_joueur": j2["id_joueur"]},
    )
    assert rep.status_code == 200

    # 7) Lancer la partie
    rep = client.post(
        f"/api/tables/{table['id_table']}/lancer",
        headers=_headers_session(auth_j1),
        json={"id_hote": j1["id_joueur"]},
    )
    assert rep.status_code == 200
    partie = rep.json()
    assert partie["id_partie"].startswith("P")


def test_patch_configuration_table_timeout(client: Any):
    hote = _inscrire(
        client,
        email="hote-config@example.com",
        nom="Hôte Config",
        mot_de_passe="secret",
        alias="Config",
    )
    auth_hote = _auth(client, "hote-config@example.com", "secret")
    rep = client.post(
        "/api/tables",
        headers=_headers_session(auth_hote),
        json={
            "id_hote": hote["id_joueur"],
            "nom_table": "Table config",
            "nb_sieges": 2,
        },
    )
    assert rep.status_code == 200
    table = rep.json()

    rep = client.patch(
        f"/api/tables/{table['id_table']}/configuration",
        headers=_headers_session(auth_hote),
        json={
            "id_hote": hote["id_joueur"],
            "politique_timeout_partie": {
                "active": False,
                "delai_inactivite_secondes": 1800,
            },
        },
    )

    assert rep.status_code == 200
    table_modifiee = rep.json()
    assert table_modifiee["politique_timeout_partie"] == {
        "version": 1,
        "active": False,
        "delai_inactivite_secondes": 1800,
    }


def test_patch_configuration_table_timeout_valide_bornes(client: Any):
    hote = _inscrire(
        client,
        email="hote-bornes@example.com",
        nom="Hôte Bornes",
        mot_de_passe="secret",
        alias="Bornes",
    )
    auth_hote = _auth(client, "hote-bornes@example.com", "secret")
    rep = client.post(
        "/api/tables",
        headers=_headers_session(auth_hote),
        json={
            "id_hote": hote["id_joueur"],
            "nom_table": "Table bornes",
            "nb_sieges": 2,
        },
    )
    assert rep.status_code == 200
    table = rep.json()

    rep = client.patch(
        f"/api/tables/{table['id_table']}/configuration",
        headers=_headers_session(auth_hote),
        json={
            "id_hote": hote["id_joueur"],
            "politique_timeout_partie": {
                "active": True,
                "delai_inactivite_secondes": 59,
            },
        },
    )

    assert rep.status_code == 422


def test_heartbeat_et_session_expiree_bloquent_appel_protege(client: Any, service_lobby):
    joueur = _inscrire(
        client,
        email="expire@example.com",
        nom="Expire",
        mot_de_passe="secret",
        alias="EXP",
    )
    auth = _auth(client, "expire@example.com", "secret")

    rep = client.post(f"/api/sessions/{auth['jeton_session']}/heartbeat", json={})
    assert rep.status_code == 200
    assert rep.json()["statut"] == "active"

    session = service_lobby.sessions.trouver_par_id(auth["jeton_session"])
    assert session is not None
    service_lobby.expirer_sessions_inactives(maintenant=session.expire_le + 1)

    rep = client.post(f"/api/sessions/{auth['jeton_session']}/heartbeat", json={})
    assert rep.status_code == 401
    assert rep.json()["detail"] == "session_expiree"

    rep = client.post(
        "/api/tables",
        headers=_headers_session(auth),
        json={
            "id_hote": joueur["id_joueur"],
            "nom_table": "Table bloquee",
            "nb_sieges": 2,
        },
    )
    assert rep.status_code == 401
    assert rep.json()["detail"] == "session_expiree"


def test_expiration_reconnexion_recupere_contexte_reprise_table(client: Any, service_lobby):
    joueur = _inscrire(
        client,
        email="reprise-expiration@example.com",
        nom="Reprise Expiration",
        mot_de_passe="secret",
        alias="REX",
    )
    auth1 = _auth(client, "reprise-expiration@example.com", "secret")

    rep = client.post(
        "/api/tables",
        headers=_headers_session(auth1),
        json={
            "id_hote": joueur["id_joueur"],
            "nom_table": "Table reprise expiration",
            "nb_sieges": 2,
        },
    )
    assert rep.status_code == 200
    table = rep.json()

    session = service_lobby.sessions.trouver_par_id(auth1["jeton_session"])
    assert session is not None
    service_lobby.expirer_sessions_inactives(maintenant=session.expire_le + 1)

    rep = client.post(
        f"/api/tables/{table['id_table']}/joueurs/pret",
        headers=_headers_session(auth1),
        json={"id_joueur": joueur["id_joueur"]},
    )
    assert rep.status_code == 401
    assert rep.json()["detail"] == "session_expiree"

    auth2 = _auth(client, "reprise-expiration@example.com", "secret")
    assert auth2["jeton_session"] != auth1["jeton_session"]
    assert auth2["contexte_reprise"]["id_table"] == table["id_table"]
    assert auth2["contexte_reprise"]["id_partie"] is None
    assert auth2["contexte_reprise"]["statut_table"] == StatutTable.OUVERTE.value


def test_table_reste_ouverte_jusqua_plein_et_filtre_ouverte(client: Any):
    # 1) Inscription + auth hôte
    j1 = _inscrire(
        client,
        email="hote@example.com",
        nom="Hôte",
        mot_de_passe="secret",
        alias="H1",
    )
    auth_j1 = _auth(client, "hote@example.com", "secret")

    # 2) Création table à 4 sièges (hôte inclus)
    rep = client.post(
        "/api/tables",
        headers=_headers_session(auth_j1),
        json={
            "id_hote": j1["id_joueur"],
            "nom_table": "Table 4 joueurs",
            "nb_sieges": 4,
        },
    )
    assert rep.status_code == 200
    table = rep.json()
    id_table = table["id_table"]
    assert table["statut"] == StatutTable.OUVERTE.value

    def _ids_tables_ouvertes():
        rep_list = client.get("/api/tables", params={"statut": StatutTable.OUVERTE.value})
        assert rep_list.status_code == 200
        payload = rep_list.json()
        return {t["id_table"] for t in payload["tables"]}

    # Visible dans "ouverte" dès le départ
    assert id_table in _ids_tables_ouvertes()

    # 3) Joueur 2 rejoint -> table 2/4 -> reste OUVERTE + toujours listée
    j2 = _inscrire(client, "j2@example.com", "J2", "s2", "A2")
    auth_j2 = _auth(client, "j2@example.com", "s2")
    rep = client.post(
        f"/api/tables/{id_table}/joueurs",
        headers=_headers_session(auth_j2),
        json={"id_joueur": j2["id_joueur"], "role": "invite"},
    )
    assert rep.status_code == 200
    siege = rep.json()
    assert siege["statut_table"] == StatutTable.OUVERTE.value
    assert id_table in _ids_tables_ouvertes()

    # 4) Joueur 3 rejoint -> table 3/4 -> reste OUVERTE + toujours listée
    j3 = _inscrire(client, "j3@example.com", "J3", "s3", "A3")
    auth_j3 = _auth(client, "j3@example.com", "s3")
    rep = client.post(
        f"/api/tables/{id_table}/joueurs",
        headers=_headers_session(auth_j3),
        json={"id_joueur": j3["id_joueur"], "role": "invite"},
    )
    assert rep.status_code == 200
    siege = rep.json()
    assert siege["statut_table"] == StatutTable.OUVERTE.value
    assert id_table in _ids_tables_ouvertes()

    # 5) Joueur 4 rejoint -> table 4/4 -> devient EN_PREPARATION + n'est plus listée "ouverte"
    j4 = _inscrire(client, "j4@example.com", "J4", "s4", "A4")
    auth_j4 = _auth(client, "j4@example.com", "s4")
    rep = client.post(
        f"/api/tables/{id_table}/joueurs",
        headers=_headers_session(auth_j4),
        json={"id_joueur": j4["id_joueur"], "role": "invite"},
    )
    assert rep.status_code == 200
    siege = rep.json()
    assert siege["statut_table"] == StatutTable.EN_PREPARATION.value
    assert id_table not in _ids_tables_ouvertes()

    # Bonus : la table doit maintenant apparaître dans le filtre "en_preparation"
    rep_list_prep = client.get("/api/tables", params={"statut": StatutTable.EN_PREPARATION.value})
    assert rep_list_prep.status_code == 200
    ids_prep = {t["id_table"] for t in rep_list_prep.json()["tables"]}
    assert id_table in ids_prep
