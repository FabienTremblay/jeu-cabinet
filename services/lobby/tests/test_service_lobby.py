# services/lobby/tests/test_service_lobby.py
# rôle        : vérifie le service applicatif lobby
# usage       : tests pytest des cas d'usage ServiceLobby
# contexte    : joueurs, tables, événements et politique de timeout
# statut      : actif
from __future__ import annotations

import asyncio
from fastapi import HTTPException

from services.lobby.schemas import (
    DemandeInscription,
    DemandeConnexion,
    DemandeCreationTable,
    DemandeConfigurationTable,
    DemandePriseSiege,
)
from services.lobby.domaine import StatutSession, StatutTable
from services.lobby.events import (
    EvenementJoueurCree,
    EvenementJoueurIntroduit,
    EvenementJoueurConnecte,
    EvenementTableCree,
    EvenementJoueurARejointTable,
    EvenementJoueurPret,
    EvenementPartieLancee,
)
from services.lobby.services_lobby import ServiceLobby
from services.lobby.kafka_producteur import ProducteurEvenements
from services.lobby.settings import Settings


def test_inscription_et_connexion_produisent_evenements(
    service_lobby: ServiceLobby,
    producteur: ProducteurEvenements,
):
    async def scenario():
        # inscription
        rep_insc = await service_lobby.inscrire_joueur(
            DemandeInscription(
                nom="Joueur Un",
                alias="Alias1",
                courriel="joueur1@example.com",
                mot_de_passe="secret1",
            )
        )

        assert rep_insc.id_joueur.startswith("J")
        assert rep_insc.courriel == "joueur1@example.com"

        # connexion
        rep_conn = await service_lobby.connecter_joueur(
            DemandeConnexion(
                courriel="joueur1@example.com",
                mot_de_passe="secret1",
            )
        )

        assert rep_conn.id_joueur == rep_insc.id_joueur
        assert rep_conn.jeton_session  # non vide

        # événements en mémoire (fixture producteur vient de conftest)
        types = [type(evt) for _, evt in producteur.evenements]

        assert EvenementJoueurCree in types
        assert EvenementJoueurIntroduit in types
        assert EvenementJoueurConnecte in types

    asyncio.run(scenario())


def test_connexion_remplace_session_active_et_expiration_ne_retire_pas_le_siege(
    joueur_repo,
    table_repo,
    session_repo,
    producteur: ProducteurEvenements,
):
    service = ServiceLobby(
        settings=Settings(
            session_absence_secondes=5,
            session_expiration_secondes=10,
        ),
        joueurs=joueur_repo,
        tables=table_repo,
        sessions=session_repo,
        producteur=producteur,
    )

    async def scenario():
        joueur = await service.inscrire_joueur(
            DemandeInscription(
                nom="Joueur Session",
                alias="JS",
                courriel="session@example.com",
                mot_de_passe="secret",
            )
        )
        connexion1 = await service.connecter_joueur(
            DemandeConnexion(courriel="session@example.com", mot_de_passe="secret")
        )
        await service.creer_table(
            DemandeCreationTable(
                id_hote=joueur.id_joueur,
                nom_table="Table session",
                nb_sieges=2,
            )
        )

        ancienne = session_repo.trouver_par_id(connexion1.jeton_session)
        assert ancienne is not None
        assert ancienne.statut == StatutSession.ACTIVE

        connexion2 = await service.connecter_joueur(
            DemandeConnexion(courriel="session@example.com", mot_de_passe="secret")
        )
        ancienne = session_repo.trouver_par_id(connexion1.jeton_session)
        nouvelle = session_repo.trouver_par_id(connexion2.jeton_session)
        assert ancienne is not None
        assert ancienne.statut == StatutSession.EXPIREE
        assert nouvelle is not None
        assert nouvelle.statut == StatutSession.ACTIVE
        assert connexion2.contexte_reprise is not None
        assert connexion2.contexte_reprise.id_table is not None

        service.expirer_sessions_inactives(maintenant=nouvelle.expire_le + 1)
        nouvelle = session_repo.trouver_par_id(connexion2.jeton_session)
        assert nouvelle is not None
        assert nouvelle.statut == StatutSession.EXPIREE

        table = table_repo.trouver_table_active_du_joueur(joueur.id_joueur)
        assert table is not None
        assert table.id_hote == joueur.id_joueur

    asyncio.run(scenario())


def test_heartbeat_reactive_session_absente(service_lobby: ServiceLobby, session_repo):
    async def scenario():
        await service_lobby.inscrire_joueur(
            DemandeInscription(
                nom="Joueur Heartbeat",
                alias="HB",
                courriel="heartbeat@example.com",
                mot_de_passe="secret",
            )
        )
        connexion = await service_lobby.connecter_joueur(
            DemandeConnexion(courriel="heartbeat@example.com", mot_de_passe="secret")
        )
        session = session_repo.trouver_par_id(connexion.jeton_session)
        assert session is not None
        session.statut = StatutSession.ABSENTE
        session_repo.sauvegarder(session)

        reponse = await service_lobby.heartbeat_session(connexion.jeton_session)

        assert reponse.statut == StatutSession.ACTIVE
        assert session_repo.trouver_par_id(connexion.jeton_session).statut == StatutSession.ACTIVE

    asyncio.run(scenario())

def test_table_reste_ouverte_jusqua_plein_service(
    service_lobby: ServiceLobby,
    producteur: ProducteurEvenements,
):
    async def scenario():
        # Hôte
        rep_h = await service_lobby.inscrire_joueur(
            DemandeInscription(
                nom="Hôte",
                alias="H",
                courriel="hote@example.com",
                mot_de_passe="secret",
            )
        )
        await service_lobby.connecter_joueur(
            DemandeConnexion(courriel="hote@example.com", mot_de_passe="secret")
        )

        # Table 4 sièges (hôte inclus)
        rep_table = await service_lobby.creer_table(
            DemandeCreationTable(
                id_hote=rep_h.id_joueur,
                nom_table="Table 4",
                nb_sieges=4,
            )
        )
        assert rep_table.statut == StatutTable.OUVERTE.value
        assert rep_table.politique_timeout_partie.active is True
        assert rep_table.politique_timeout_partie.delai_inactivite_secondes == 3600

        async def creer_et_join(courriel: str, alias: str) -> str:
            rep_j = await service_lobby.inscrire_joueur(
                DemandeInscription(
                    nom=alias,
                    alias=alias,
                    courriel=courriel,
                    mot_de_passe="pw",
                )
            )
            await service_lobby.connecter_joueur(
                DemandeConnexion(courriel=courriel, mot_de_passe="pw")
            )
            rep_siege = await service_lobby.prendre_siege(
                rep_table.id_table,
                DemandePriseSiege(id_joueur=rep_j.id_joueur, role="invite"),
            )
            return rep_siege.statut_table

        # 2/4
        statut = await creer_et_join("j2@example.com", "J2")
        assert statut == StatutTable.OUVERTE.value

        # 3/4
        statut = await creer_et_join("j3@example.com", "J3")
        assert statut == StatutTable.OUVERTE.value

        # 4/4 -> en_preparation
        statut = await creer_et_join("j4@example.com", "J4")
        assert statut == StatutTable.EN_PREPARATION.value

    asyncio.run(scenario())


def test_creer_table_applique_politique_timeout_depuis_settings(
    joueur_repo,
    table_repo,
    session_repo,
    producteur: ProducteurEvenements,
):
    service = ServiceLobby(
        settings=Settings(
            timeout_partie_actif=False,
            timeout_partie_delai_inactivite_secondes=900,
        ),
        joueurs=joueur_repo,
        tables=table_repo,
        sessions=session_repo,
        producteur=producteur,
    )

    async def scenario():
        rep_j1 = await service.inscrire_joueur(
            DemandeInscription(
                nom="Joueur Un",
                alias="Alias1",
                courriel="joueur1@example.com",
                mot_de_passe="secret1",
            )
        )

        rep_table = await service.creer_table(
            DemandeCreationTable(
                id_hote=rep_j1.id_joueur,
                nom_table="Table timeout",
                nb_sieges=2,
            )
        )

        assert rep_table.politique_timeout_partie.active is False
        assert rep_table.politique_timeout_partie.delai_inactivite_secondes == 900

        table = table_repo.trouver_par_id(rep_table.id_table)
        assert table is not None
        assert table.politique_timeout_partie.active is False
        assert table.politique_timeout_partie.delai_inactivite_secondes == 900

    asyncio.run(scenario())


def test_hote_modifie_configuration_timeout_avant_lancement(
    service_lobby: ServiceLobby,
    table_repo,
):
    async def scenario():
        rep_hote = await service_lobby.inscrire_joueur(
            DemandeInscription(
                nom="Hote Timeout",
                alias="HoteTimeout",
                courriel="hote-timeout@example.com",
                mot_de_passe="secret",
            )
        )
        rep_table = await service_lobby.creer_table(
            DemandeCreationTable(
                id_hote=rep_hote.id_joueur,
                nom_table="Table configurable",
                nb_sieges=2,
            )
        )

        rep_modifiee = await service_lobby.modifier_configuration_table(
            rep_table.id_table,
            DemandeConfigurationTable(
                id_hote=rep_hote.id_joueur,
                politique_timeout_partie={
                    "active": False,
                    "delai_inactivite_secondes": 900,
                },
            ),
        )

        assert rep_modifiee.politique_timeout_partie.version == 1
        assert rep_modifiee.politique_timeout_partie.active is False
        assert rep_modifiee.politique_timeout_partie.delai_inactivite_secondes == 900

        table_relue = table_repo.trouver_par_id(rep_table.id_table)
        assert table_relue is not None
        assert table_relue.politique_timeout_partie.active is False
        assert table_relue.politique_timeout_partie.delai_inactivite_secondes == 900

    asyncio.run(scenario())


def test_non_hote_ne_peut_pas_modifier_configuration_timeout(
    service_lobby: ServiceLobby,
):
    async def scenario():
        rep_hote = await service_lobby.inscrire_joueur(
            DemandeInscription(
                nom="Hote",
                alias="Hote",
                courriel="hote-refus@example.com",
                mot_de_passe="secret",
            )
        )
        rep_table = await service_lobby.creer_table(
            DemandeCreationTable(
                id_hote=rep_hote.id_joueur,
                nom_table="Table refus",
                nb_sieges=2,
            )
        )

        try:
            await service_lobby.modifier_configuration_table(
                rep_table.id_table,
                DemandeConfigurationTable(
                    id_hote="J-AUTRE",
                    politique_timeout_partie={
                        "active": True,
                        "delai_inactivite_secondes": 600,
                    },
                ),
            )
        except HTTPException as exc:
            assert exc.status_code == 403
            assert exc.detail == "seul_l_hote_peut_modifier_configuration"
        else:
            raise AssertionError("modification acceptee pour un non-hote")

    asyncio.run(scenario())


def test_modifier_configuration_table_introuvable_retourne_404(
    service_lobby: ServiceLobby,
):
    async def scenario():
        try:
            await service_lobby.modifier_configuration_table(
                "T-INCONNUE",
                DemandeConfigurationTable(
                    id_hote="J000001",
                    politique_timeout_partie={
                        "active": True,
                        "delai_inactivite_secondes": 600,
                    },
                ),
            )
        except HTTPException as exc:
            assert exc.status_code == 404
            assert exc.detail == "table_introuvable"
        else:
            raise AssertionError("modification acceptee pour une table inconnue")

    asyncio.run(scenario())


def test_configuration_timeout_refusee_apres_lancement_ou_terminaison(
    service_lobby: ServiceLobby,
    table_repo,
):
    async def scenario():
        rep_hote = await service_lobby.inscrire_joueur(
            DemandeInscription(
                nom="Hote Verrou",
                alias="HoteVerrou",
                courriel="hote-verrou@example.com",
                mot_de_passe="secret",
            )
        )
        rep_table = await service_lobby.creer_table(
            DemandeCreationTable(
                id_hote=rep_hote.id_joueur,
                nom_table="Table verrou",
                nb_sieges=2,
            )
        )

        table = table_repo.trouver_par_id(rep_table.id_table)
        assert table is not None
        table.statut = StatutTable.EN_COURS
        table_repo.ajouter(table)

        demande = DemandeConfigurationTable(
            id_hote=rep_hote.id_joueur,
            politique_timeout_partie={
                "active": True,
                "delai_inactivite_secondes": 600,
            },
        )

        try:
            await service_lobby.modifier_configuration_table(rep_table.id_table, demande)
        except HTTPException as exc:
            assert exc.status_code == 400
            assert exc.detail == "configuration_table_verrouillee"
        else:
            raise AssertionError("modification acceptee pour une table en_cours")

        table.statut = StatutTable.TERMINEE
        table_repo.ajouter(table)

        try:
            await service_lobby.modifier_configuration_table(rep_table.id_table, demande)
        except HTTPException as exc:
            assert exc.status_code == 400
            assert exc.detail == "configuration_table_verrouillee"
        else:
            raise AssertionError("modification acceptee pour une table terminee")

    asyncio.run(scenario())


def test_scenario_complet_lancer_partie(
    service_lobby: ServiceLobby,
    producteur: ProducteurEvenements,
):
    async def scenario():
        # Joueur 1
        rep_j1 = await service_lobby.inscrire_joueur(
            DemandeInscription(
                nom="Joueur Un",
                alias="Alias1",
                courriel="joueur1@example.com",
                mot_de_passe="secret1",
            )
        )
        await service_lobby.connecter_joueur(
            DemandeConnexion(
                courriel="joueur1@example.com",
                mot_de_passe="secret1",
            )
        )

        # Table
        rep_table = await service_lobby.creer_table(
            DemandeCreationTable(
                id_hote=rep_j1.id_joueur,
                nom_table="Table test multi",
                nb_sieges=2,
            )
        )
        assert rep_table.statut == StatutTable.OUVERTE.value

        # Joueur 2
        rep_j2 = await service_lobby.inscrire_joueur(
            DemandeInscription(
                nom="Joueur Deux",
                alias="Alias2",
                courriel="joueur2@example.com",
                mot_de_passe="secret2",
            )
        )
        await service_lobby.connecter_joueur(
            DemandeConnexion(
                courriel="joueur2@example.com",
                mot_de_passe="secret2",
            )
        )

        # Joueur 2 prend un siège
        rep_siege = await service_lobby.prendre_siege(
            rep_table.id_table,
            DemandePriseSiege(
                id_joueur=rep_j2.id_joueur,
                role="invite",
            ),
        )
        assert rep_siege.id_joueur == rep_j2.id_joueur
        assert rep_siege.statut_table == StatutTable.EN_PREPARATION.value

        # Les deux joueurs sont prêts
        await service_lobby.marquer_joueur_pret(rep_table.id_table, rep_j1.id_joueur)
        await service_lobby.marquer_joueur_pret(rep_table.id_table, rep_j2.id_joueur)

        # Lancer la partie
        rep_partie = await service_lobby.lancer_partie(
            rep_table.id_table,
            id_hote=rep_j1.id_joueur,
        )

        assert rep_partie.id_partie.startswith("P")

        types = [type(evt) for _, evt in producteur.evenements]
        assert EvenementTableCree in types
        assert EvenementJoueurARejointTable in types
        assert EvenementJoueurPret in types
        assert EvenementPartieLancee in types
        evt_partie = next(evt for _, evt in producteur.evenements if isinstance(evt, EvenementPartieLancee))
        assert evt_partie.politique_timeout_partie is not None
        assert evt_partie.politique_timeout_partie.active is True
        assert evt_partie.politique_timeout_partie.delai_inactivite_secondes == 3600

    asyncio.run(scenario())


def test_lancer_partie_publie_politique_timeout_modifiee(
    service_lobby: ServiceLobby,
    producteur: ProducteurEvenements,
):
    async def scenario():
        rep_j1 = await service_lobby.inscrire_joueur(
            DemandeInscription(
                nom="Joueur Un",
                alias="Alias1",
                courriel="timeout-modifie-1@example.com",
                mot_de_passe="secret1",
            )
        )
        rep_table = await service_lobby.creer_table(
            DemandeCreationTable(
                id_hote=rep_j1.id_joueur,
                nom_table="Table timeout modifie",
                nb_sieges=2,
            )
        )

        rep_j2 = await service_lobby.inscrire_joueur(
            DemandeInscription(
                nom="Joueur Deux",
                alias="Alias2",
                courriel="timeout-modifie-2@example.com",
                mot_de_passe="secret2",
            )
        )
        await service_lobby.prendre_siege(
            rep_table.id_table,
            DemandePriseSiege(id_joueur=rep_j2.id_joueur, role="invite"),
        )

        await service_lobby.modifier_configuration_table(
            rep_table.id_table,
            DemandeConfigurationTable(
                id_hote=rep_j1.id_joueur,
                politique_timeout_partie={
                    "active": False,
                    "delai_inactivite_secondes": 1200,
                },
            ),
        )

        await service_lobby.marquer_joueur_pret(rep_table.id_table, rep_j1.id_joueur)
        await service_lobby.marquer_joueur_pret(rep_table.id_table, rep_j2.id_joueur)
        await service_lobby.lancer_partie(rep_table.id_table, id_hote=rep_j1.id_joueur)

        evt_partie = next(
            evt
            for _, evt in producteur.evenements
            if isinstance(evt, EvenementPartieLancee)
        )
        assert evt_partie.politique_timeout_partie is not None
        assert evt_partie.politique_timeout_partie.active is False
        assert evt_partie.politique_timeout_partie.delai_inactivite_secondes == 1200

    asyncio.run(scenario())


def test_terminer_partie_marque_table_terminee_sans_vider_joueurs(
    service_lobby: ServiceLobby,
    table_repo,
):
    async def scenario():
        rep_j1 = await service_lobby.inscrire_joueur(
            DemandeInscription(
                nom="Joueur Un",
                alias="Alias1",
                courriel="timeout1@example.com",
                mot_de_passe="secret1",
            )
        )
        rep_j2 = await service_lobby.inscrire_joueur(
            DemandeInscription(
                nom="Joueur Deux",
                alias="Alias2",
                courriel="timeout2@example.com",
                mot_de_passe="secret2",
            )
        )

        rep_table = await service_lobby.creer_table(
            DemandeCreationTable(
                id_hote=rep_j1.id_joueur,
                nom_table="Table timeout",
                nb_sieges=2,
            )
        )
        await service_lobby.prendre_siege(
            rep_table.id_table,
            DemandePriseSiege(id_joueur=rep_j2.id_joueur, role="invite"),
        )
        await service_lobby.marquer_joueur_pret(rep_table.id_table, rep_j1.id_joueur)
        await service_lobby.marquer_joueur_pret(rep_table.id_table, rep_j2.id_joueur)

        rep_partie = await service_lobby.lancer_partie(rep_table.id_table, id_hote=rep_j1.id_joueur)

        rep_terminee = await service_lobby.terminer_partie(
            id_partie=rep_partie.id_partie,
            raison="TIMEOUT_INACTIVITE",
        )

        assert rep_terminee.statut == StatutTable.TERMINEE.value
        table = table_repo.trouver_par_id(rep_table.id_table)
        assert table.statut == StatutTable.TERMINEE
        assert table.id_partie == rep_partie.id_partie
        assert rep_j2.id_joueur in table.joueurs_assis
        assert rep_j1.id_joueur in table.joueurs_prets
        assert rep_j2.id_joueur in table.joueurs_prets

    asyncio.run(scenario())


def test_inscription_refuse_courriel_duplique(service_lobby: ServiceLobby, producteur: ProducteurEvenements):
    async def scenario():
        # première inscription OK
        await service_lobby.inscrire_joueur(
            DemandeInscription(
                nom="Joueur Un",
                alias="Alias1",
                courriel="joueur@example.com",
                mot_de_passe="secret1",
            )
        )

        # deuxième inscription avec même courriel -> HTTPException 400
        from fastapi import HTTPException

        try:
            await service_lobby.inscrire_joueur(
                DemandeInscription(
                    nom="Joueur Deux",
                    alias="Alias2",
                    courriel="joueur@example.com",
                    mot_de_passe="secret2",
                )
            )
            assert False, "devrait lever HTTPException"
        except HTTPException as e:
            assert e.status_code == 400
            assert e.detail == "courriel_deja_utilise"

    asyncio.run(scenario())


def test_connexion_refuse_mot_de_passe_invalide(service_lobby: ServiceLobby, producteur: ProducteurEvenements):
    async def scenario():
        await service_lobby.inscrire_joueur(
            DemandeInscription(
                nom="Joueur Un",
                alias="Alias1",
                courriel="joueur@example.com",
                mot_de_passe="secret1",
            )
        )

        from fastapi import HTTPException

        try:
            await service_lobby.connecter_joueur(
                DemandeConnexion(
                    courriel="joueur@example.com",
                    mot_de_passe="mauvais",
                )
            )
            assert False, "devrait lever HTTPException"
        except HTTPException as e:
            assert e.status_code == 400
            assert e.detail == "mot_de_passe_invalide"

    asyncio.run(scenario())


def test_creer_table_refuse_si_table_deja_active_pour_hote(
    service_lobby: ServiceLobby,
    producteur: ProducteurEvenements,
):
    async def scenario():
        rep_j1 = await service_lobby.inscrire_joueur(
            DemandeInscription(
                nom="Joueur Un",
                alias="Alias1",
                courriel="joueur1@example.com",
                mot_de_passe="secret1",
            )
        )

        # première table OK
        await service_lobby.creer_table(
            DemandeCreationTable(
                id_hote=rep_j1.id_joueur,
                nom_table="Table 1",
                nb_sieges=2,
            )
        )

        # deuxième table pour même hôte -> refus
        from fastapi import HTTPException

        try:
            await service_lobby.creer_table(
                DemandeCreationTable(
                    id_hote=rep_j1.id_joueur,
                    nom_table="Table 2",
                    nb_sieges=3,
                )
            )
            assert False, "devrait lever HTTPException"
        except HTTPException as e:
            assert e.status_code == 400
            assert e.detail == "table_deja_active_pour_ce_joueur"

    asyncio.run(scenario())


def test_lancer_partie_refuse_si_pas_tous_prets(
    service_lobby: ServiceLobby,
    producteur: ProducteurEvenements,
):
    async def scenario():
        rep_j1 = await service_lobby.inscrire_joueur(
            DemandeInscription(
                nom="Joueur Un",
                alias="Alias1",
                courriel="joueur1@example.com",
                mot_de_passe="secret1",
            )
        )
        await service_lobby.connecter_joueur(
            DemandeConnexion(
                courriel="joueur1@example.com",
                mot_de_passe="secret1",
            )
        )

        rep_j2 = await service_lobby.inscrire_joueur(
            DemandeInscription(
                nom="Joueur Deux",
                alias="Alias2",
                courriel="joueur2@example.com",
                mot_de_passe="secret2",
            )
        )
        await service_lobby.connecter_joueur(
            DemandeConnexion(
                courriel="joueur2@example.com",
                mot_de_passe="secret2",
            )
        )

        rep_table = await service_lobby.creer_table(
            DemandeCreationTable(
                id_hote=rep_j1.id_joueur,
                nom_table="Table test",
                nb_sieges=2,
            )
        )

        # J2 s'assoit
        await service_lobby.prendre_siege(
            rep_table.id_table,
            DemandePriseSiege(
                id_joueur=rep_j2.id_joueur,
                role="invite",
            ),
        )

        # seul J1 est prêt
        await service_lobby.marquer_joueur_pret(rep_table.id_table, rep_j1.id_joueur)

        from fastapi import HTTPException

        try:
            await service_lobby.lancer_partie(rep_table.id_table, id_hote=rep_j1.id_joueur)
            assert False, "devrait lever HTTPException"
        except HTTPException as e:
            assert e.status_code == 400
            assert e.detail == "joueurs_pas_tous_prets"

    asyncio.run(scenario())

def test_lister_joueurs_lobby_et_table(
    service_lobby: ServiceLobby,
    producteur: ProducteurEvenements,
):
    async def scenario():
        # 1) inscription + connexion de 2 joueurs, aucun n'est encore à une table
        rep_j1 = await service_lobby.inscrire_joueur(
            DemandeInscription(
                nom="Joueur Un",
                alias="Alias1",
                courriel="joueur1@example.com",
                mot_de_passe="secret1",
            )
        )
        await service_lobby.connecter_joueur(
            DemandeConnexion(
                courriel="joueur1@example.com",
                mot_de_passe="secret1",
            )
        )

        rep_j2 = await service_lobby.inscrire_joueur(
            DemandeInscription(
                nom="Joueur Deux",
                alias="Alias2",
                courriel="joueur2@example.com",
                mot_de_passe="secret2",
            )
        )
        await service_lobby.connecter_joueur(
            DemandeConnexion(
                courriel="joueur2@example.com",
                mot_de_passe="secret2",
            )
        )

        # à ce stade, les deux joueurs sont dans le "lobby" (aucune table)
        joueurs_lobby = await service_lobby.lister_joueurs_lobby()
        ids_lobby = {j.id_joueur for j in joueurs_lobby}
        assert ids_lobby == {rep_j1.id_joueur, rep_j2.id_joueur}

        # 2) création d'une table par J1
        rep_table = await service_lobby.creer_table(
            DemandeCreationTable(
                id_hote=rep_j1.id_joueur,
                nom_table="Table test lobby",
                nb_sieges=2,
            )
        )
        assert rep_table.statut == StatutTable.OUVERTE.value

        # 3) J2 prend un siège comme invité
        rep_siege = await service_lobby.prendre_siege(
            rep_table.id_table,
            DemandePriseSiege(
                id_joueur=rep_j2.id_joueur,
                role="invite",
            ),
        )
        assert rep_siege.id_joueur == rep_j2.id_joueur

        # 4) liste des joueurs de la table
        joueurs_table = await service_lobby.lister_joueurs_table(rep_table.id_table)
        ids_table = {j.id_joueur for j in joueurs_table}
        # on doit retrouver l'hôte et l'invité
        assert ids_table == {rep_j1.id_joueur, rep_j2.id_joueur}

        # 5) les deux joueurs étant désormais à une table,
        # ils ne devraient plus apparaître dans la liste du lobby
        joueurs_lobby_apres = await service_lobby.lister_joueurs_lobby()
        ids_lobby_apres = {j.id_joueur for j in joueurs_lobby_apres}
        assert ids_lobby_apres == set()

    asyncio.run(scenario())
