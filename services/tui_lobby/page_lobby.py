def page_lobby(session):
    while True:
        # si on découvre qu'on est assis, on ne devrait plus être au lobby
        if session.id_table:
            return "table"

        session.rafraichir_position_table()
        if session.id_table:
            return "table"

        # triptyque lobby : gauche infos, droite événements
        session.afficher_vue_lobby()

        print("\n=== Lobby ===")
        print("joueur:", session.alias, f"[{session.id_joueur}]")
        print("table actuelle: (aucune)")

        print("\nActions :")
        print("1) Créer une table")
        print("2) Rejoindre une table")
        print("3) Rafraîchir l'écran")
        print("0) Retour accueil")

        choix = input("> ").strip()

        if choix == "1":
            session.creer_table()
            session.rafraichir_position_table()
            if session.id_table:
                return "table"

        elif choix == "2":
            session.rejoindre_table()
            session.rafraichir_position_table()
            if session.id_table:
                return "table"

        elif choix == "3":
            # juste rafraîchir
            continue

        elif choix == "0":
            return "accueil"

