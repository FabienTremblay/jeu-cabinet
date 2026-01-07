def page_accueil(session):
    while True:
        session.afficher_evenements()

        print("\n=== Accueil ===")
        print("1) Inscription")
        print("2) Connexion")
        print("0) Quitter")

        choix = input("> ").strip()

        if choix == "1":
            session.inscrire()
            session.rafraichir_position_table()

            if session.est_dans_partie_active():
                return "jeu"
            elif session.id_table:
                return "table"
            else:
                return "lobby"

        elif choix == "2":
            session.connecter()
            session.rafraichir_position_table()

            if session.est_dans_partie_active():
                return "jeu"
            elif session.id_table:
                return "table"
            else:
                return "lobby"

        elif choix == "0":
            return "quit"

