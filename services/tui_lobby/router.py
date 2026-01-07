from .page_accueil import page_accueil
from .page_lobby import page_lobby
from .page_table import page_table
from .page_jeu import page_jeu

def start(session):
    current = "accueil"

    while True:
        if current == "accueil":
            current = page_accueil(session)

        elif current == "lobby":
            if session.id_table:
                current = "table"
            else:
                current = page_lobby(session)

        elif current == "table":
            if not session.id_table:
                current = "lobby"
            else:
                current = page_table(session)

        elif current == "jeu":
            current = page_jeu(session)

        elif current == "quit":
            break

        else:
            print(f"page inconnue: {current}")
            break

