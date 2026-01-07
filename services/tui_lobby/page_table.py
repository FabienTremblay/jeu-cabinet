def page_table(session):
    while True:
        # si on a perdu la table (ex: expulsé), retour au lobby
        if not session.id_table:
            return "lobby"

        session.rafraichir_position_table()
        if not session.id_table:
            return "lobby"

        # si la partie est déjà en cours pour cette table, on file à la page jeu
        if session.verifier_si_partie_lancee():
            return "jeu"

        # triptyque table
        session.afficher_vue_table()

        print("\n=== Table ===")
        print("joueur:", session.alias, f"[{session.id_joueur}]")
        print("table actuelle:", session.id_table)

        print("\nActions :")
        print("1) Me déclarer prêt")
        print("2) Lancer la partie (hôte)")
        print("3) Rafraîchir l'écran")
        print("0) Retour accueil (quitter le TUI)")

        choix = input("> ").strip()

        if choix == "1":
            session.se_declarer_pret()

        elif choix == "2":
            session.lancer_partie()
            # juste après, on vérifie si un événement PartieLancee est arrivé
            if session.verifier_si_partie_lancee():
                return "jeu"

        elif choix == "3":
            # on reboucle → réaffiche vue + re-check PartieLancee au début
            continue

        elif choix == "0":
            return "quit"

