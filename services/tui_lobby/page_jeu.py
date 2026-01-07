def page_jeu(session):
    """
    Page de jeu :
      - statut de la partie
      - événements de jeu (historiques)
      - journal (état moteur)
      - programme du cabinet
      - cartes du joueur
      - attente en cours
      - rappel des conditions / palmarès
      - menu d'actions (adapté à la sous-phase)
    """

    while True:
        # 1) rafraîchir les infos de base
        session.rafraichir_position_table()
        session.est_dans_partie_active()
        session.rafraichir_etat_partie()

        etat = session._etat_partie or {}
        sous_phase = etat.get("sous_phase") or session.sous_phase

        # 2) partie terminée ?
        if etat.get("termine"):
            session._afficher_header()
            session.afficher_fenetre_statut_partie()
            session.afficher_fenetre_palmares()
            print("\nLa partie est terminée.")
            input("\n(Entrée pour revenir au lobby) ")
            return "quit"

        # 3) affichage principal (vue triptyque)
        session._afficher_header()

        # 3.1) statut de la partie
        session.afficher_fenetre_statut_partie()
        print()

        # 3.2) événements de jeu et journal
        session.afficher_fenetre_evenements_jeu()
        session.afficher_fenetre_journal()

        print("\n------------------------------")
        print("\n=== vue jeu ===\n")

        # 3.3) programme du cabinet
        session.afficher_fenetre_programme()
        print()

        # 3.4) cartes du joueur (avec coûts d'attention)
        session.afficher_fenetre_cartes()
        print()

        # 3.5) attente éventuelle
        session.afficher_fenetre_attente()
        print()

        # 3.6) petit message de transition : rappel palmarès / conditions
        # (pour l'instant : on affiche simplement le palmarès, qui sert de proxy
        # aux conditions de victoire du skin.)
        session.afficher_fenetre_palmares()

        # 4) menu d'actions
        print("\n=== menu d'actions ===")
        print("1) rafraîchir l'état de la partie")
        print("2) voir le détail d'une carte")

        # libellé de l'option 4 selon la sous-phase
        label4 = "actions proposées par le skin"
        if sous_phase == "PHASE_PROGRAMME":
            label4 = "actions de programme (skin)"
        elif sous_phase == "PHASE_VOTE":
            label4 = "actions de vote (skin)"
        elif sous_phase == "PHASE_PERTURBATION_VOTE":
            label4 = "actions de perturbation (skin)"

        print(f"4) {label4}")

        # Option 5 : jeu hors programme (toujours dispo pour l'instant,
        # le skin / moteur pourra décider de refuser l'action)
        print("5) jouer une carte (hors programme)")

        # Options de debug / infra
        print("8) envoyer une action brute au moteur")
        print("9) événements système (Kafka)")
        print("0) retour à la table")

        choix = input("> ").strip()

        # 5) gestion des choix

        if choix == "1":
            # on reboucle, tout sera rafraîchi
            continue

        elif choix == "2":
            session.afficher_detail_carte()

        elif choix == "4":
            att = session.attente_active
            if not att:
                print("\nAucune attente active (ou toutes les réponses ont été reçues).")
                input("\n(Entrée pour revenir à la vue jeu) ")
                continue

            meta = att.get("meta") or {}
            ui = meta.get("ui") or {}
            actions = ui.get("actions") or []
            if not actions:
                print("\nCette attente ne propose pas d'actions spécifiques.")
                input("\n(Entrée pour revenir à la vue jeu) ")
                continue

            print("\n=== actions proposées ===")
            session.afficher_ressources_joueur_courant()
            print()
            for i, a in enumerate(actions, start=1):
                print(f"{i}) {a.get('label') or a.get('op')}")

            s = input("Votre choix d'action : ").strip()
            if not s:
                continue
            try:
                idx = int(s)
            except ValueError:
                print("choix invalide.")
                continue
            if not (1 <= idx <= len(actions)):
                print("numéro hors limites.")
                continue

            action_def = actions[idx - 1]
            session.executer_action_ui(action_def)

        elif choix == "5":
            session.jouer_carte_hors_programme()

        elif choix == "8":
            type_action = input("type_action ? ").strip()
            if not type_action:
                print("type_action vide, abandon.")
                continue

            print(
                "donnees (json) ? laisse vide pour {}.\n"
                "exemple : {\"cible\": \"X\", \"valeur\": 1}"
            )
            ligne = input("donnees> ").strip()
            if not ligne:
                donnees = {}
            else:
                try:
                    donnees = json.loads(ligne)
                    if not isinstance(donnees, dict):
                        print("le json doit être un objet (clé/valeur).")
                        continue
                except Exception as e:
                    print(f"json invalide : {e}")
                    continue

            session.envoyer_action(type_action=type_action, donnees=donnees)

        elif choix == "9":
            print("\n=== événements système (Kafka) ===")
            session.afficher_evenements()
            input("\n(Entrée pour revenir à la vue jeu) ")

        elif choix == "0":
            return "quit"

        else:
            print("choix inconnu.")

