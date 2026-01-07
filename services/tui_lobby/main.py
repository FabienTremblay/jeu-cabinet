import argparse
from .config import charger_config
from .client_lobby import ClientLobby
from .client_moteur import ClientMoteur
from .kafka_listener import EcouteurEvenements
from .session import SessionJoueur
from .router import start


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--alias", help="alias du joueur (écrase TUI_JOUEUR_ALIAS)")
    args = parser.parse_args()

    cfg = charger_config()
    if args.alias:
        cfg.joueur_alias = args.alias

    client_lobby = ClientLobby(cfg)
    client_moteur = ClientMoteur(cfg)

    session = SessionJoueur(cfg, client_lobby, client_moteur=client_moteur)

    def on_evt(evt: dict):
        session.ajouter_evenement(evt)

    ecouteur = EcouteurEvenements(
        cfg,
        filtre_joueur_id=None,
        filtre_table_id=None,
    )
    ecouteur.demarrer(on_evt)

    try:
        start(session)
    finally:
        ecouteur.arreter()


if __name__ == "__main__":
    main()

