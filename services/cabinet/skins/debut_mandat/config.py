# services/cabinet/skins/debut_mandat/config.py

SKIN_CONFIG = {
  "id": "debut_mandat",
  "nom": "Conseil des ministres – Début de mandat",
  "description": "Skin de base pour tester le moteur : 4 axes, une économie simple, un petit deck de cartes politiques et quelques événements mondiaux.",
  "axes": [
    {
      "id": "social",
      "nom": "Cohésion sociale",
      "valeur_init": 0,
      "seuil_crise": -5,
      "seuil_excellence": 5,
      "poids": 1.0
    },
    {
      "id": "economique",
      "nom": "Performance économique",
      "valeur_init": 0,
      "seuil_crise": -5,
      "seuil_excellence": 5,
      "poids": 1.0
    },
    {
      "id": "environnement",
      "nom": "Transition écologique",
      "valeur_init": 0,
      "seuil_crise": -5,
      "seuil_excellence": 5,
      "poids": 1.0
    },
    {
      "id": "institutionnel",
      "nom": "Confiance institutionnelle",
      "valeur_init": 0,
      "seuil_crise": -5,
      "seuil_excellence": 5,
      "poids": 1.0
    }
  ],

  "economie": {
      "recettes": {
          "impot_part": {
              "valeur": 1200,
              "poids_axes": { "institutionnel": -1, "economique": -1 }
          },
          "impot_ent": {
              "valeur": 800,
              "poids_axes": { "institutionnel": 1, "economique": -1 }
          },
          "taxe_carbone": {
              "valeur": 300,
              "poids_axes": { "institutionnel": 1, "economique": -1 },
              "environnement": 2
          }
      },
      "depenses": {
          "sante": {
              "valeur": 1200,
              "poids_axes": { "institutionnel": -1, "social": -1 }
          },
          "education": {
              "valeur": 500,
              "poids_axes": { "social": 1, "economique": 2 }
          },
          "defense": {
              "valeur": 300,
              "poids_axes": { "institutionnel": -1, "economique": -1 }
          }
      },
      "efficience": {
          "sante":   { "valeur": 0.65 },
          "education": { "valeur": 0.85 },
          "defense": { "valeur": 0.60 }
      },
      "dette": 20000,
      "taux_interet": 0.03
  },
  "capital_init": 5,
  "capital_collectif_init": 0,
  "capital_opposition_init": 3,
  "opposition_skin_init": { "adhesion": 0 },
  "analyse_skin_init": { "pente_axes": 0 },
  "main_init": 5,
  "nb_tours_max": 7,

  "cartes": [
    # ------------------------------------------------------------------
    # 🔥 Cartes d'influence politique (10)
    # ------------------------------------------------------------------
    {
      "id": "INF-001",
      "nom": "Appui d’une figure respectée",
      "type": "influence",
      "copies": 2,
      "cout_attention": 1,
      "cout_cp": 1,
      "commandes": [
        { "op": "capital_collectif.delta", "delta": 2 },
        {
          "op": "journal",
          "payload": {
            "carte_id": "INF-001",
            "message": "Une figure respectée accorde son appui public au cabinet."
          }
        }
      ]
    },
    {
      "id": "INF-002",
      "nom": "Campagne de terrain intensive",
      "type": "influence",
      "copies": 2,
      "cout_attention": 1,
      "cout_cp": 0,
      "commandes": [
        { "op": "capital_collectif.delta", "delta": 1 },
        {
          "op": "journal",
          "payload": {
            "carte_id": "INF-002",
            "message": "Une campagne de terrain intensive rassure une partie de l’électorat."
          }
        }
      ]
    },
    {
      "id": "INF-003",
      "nom": "Gestion exemplaire d’une crise",
      "type": "influence",
      "copies": 1,
      "cout_attention": 2,
      "cout_cp": 1,
      "commandes": [
        { "op": "capital_collectif.delta", "delta": 2 },
        {
          "op": "journal",
          "payload": {
            "carte_id": "INF-003",
            "message": "Le cabinet gère une crise de façon exemplaire et gagne en crédibilité."
          }
        }
      ]
    },
    {
      "id": "INF-004",
      "nom": "Communication maîtrisée",
      "type": "influence",
      "copies": 2,
      "cout_attention": 1,
      "cout_cp": 0,
      "commandes": [
        { "op": "capital_collectif.delta", "delta": 1 },
        {
          "op": "journal",
          "payload": {
            "carte_id": "INF-004",
            "message": "Une communication claire et cohérente renforce la confiance du public."
          }
        }
      ]
    },
    {
      "id": "INF-005",
      "nom": "Consultation citoyenne",
      "type": "influence",
      "copies": 1,
      "cout_attention": 1,
      "cout_cp": 0,
      "commandes": [
        { "op": "capital_collectif.delta", "delta": 1 },
        {
          "op": "journal",
          "payload": {
            "carte_id": "INF-005",
            "message": "Une large consultation citoyenne améliore la perception du gouvernement."
          }
        }
      ]
    },
    {
      "id": "INF-006",
      "nom": "Pacte avec les élus locaux",
      "type": "influence",
      "copies": 1,
      "cout_attention": 1,
      "cout_cp": 1,
      "commandes": [
        { "op": "capital_collectif.delta", "delta": 1 },
        # le capital perso est géré par une autre commande
        { "op": "joueur.capital.delta", "joueur_id": "_auto", "delta": 1 },
        {
          "op": "journal",
          "payload": {
            "carte_id": "INF-006",
            "message": "Un pacte avec les élus locaux renforce la base politique du ministre."
          }
        }
      ]
    },
    {
      "id": "INF-007",
      "nom": "Initiative citoyenne relayée",
      "type": "influence",
      "copies": 1,
      "cout_attention": 1,
      "cout_cp": 0,
      "commandes": [
        { "op": "capital_collectif.delta", "delta": 1 },
        {
          "op": "journal",
          "payload": {
            "carte_id": "INF-007",
            "message": "Une initiative citoyenne positive est reprise par le cabinet."
          }
        }
      ]
    },
    {
      "id": "INF-008",
      "nom": "Conférence de presse improvisée",
      "type": "influence",
      "copies": 1,
      "cout_attention": 1,
      "cout_cp": 0,
      "commandes": [
        { "op": "capital_collectif.delta", "delta": -1 },
        { "op": "joueur.capital.delta", "joueur_id": "_auto", "delta": 2 },
        {
          "op": "journal",
          "payload": {
            "carte_id": "INF-008",
            "message": "Une conférence de presse improvisée crée la controverse mais sert l’ambition personnelle du ministre."
          }
        }
      ]
    },
    {
      "id": "INF-009",
      "nom": "Promesse ciblée crédible",
      "type": "influence",
      "copies": 1,
      "cout_attention": 1,
      "cout_cp": 1,
      "commandes": [
        { "op": "capital_collectif.delta", "delta": 1 },
        { "op": "joueur.capital.delta", "joueur_id": "_auto", "delta": 1 },
        {
          "op": "journal",
          "payload": {
            "carte_id": "INF-009",
            "message": "Une promesse ciblée et crédible renforce à la fois le cabinet et le ministre."
          }
        }
      ]
    },
    {
      "id": "INF-010",
      "nom": "Plan de communication intégré",
      "type": "influence",
      "copies": 1,
      "cout_attention": 2,
      "cout_cp": 1,
      "commandes": [
        { "op": "capital_collectif.delta", "delta": 3 },
        {
          "op": "journal",
          "payload": {
            "carte_id": "INF-010",
            "message": "Un plan de communication intégré repositionne favorablement le gouvernement."
          }
        }
      ]
    },
    # ------------------------------------------------------------------
    # 🛡️ Cartes de contre-coups (10)
    # ------------------------------------------------------------------
    {
      "id": "CC-001",
      "nom": "Rectification médiatique",
      "type": "contre_coup",
      "copies": 2,
      "cout_attention": 1,
      "cout_cp": 1,
      "commandes": [
        { "op": "capital_collectif.delta", "delta": 1 },
        {
          "op": "journal",
          "payload": {
            "carte_id": "CC-001",
            "message": "Une rectification médiatique réduit l’impact d’une mauvaise nouvelle."
          }
        }
      ]
    },
    {
      "id": "CC-002",
      "nom": "Réplique en chambre",
      "type": "contre_coup",
      "copies": 1,
      "cout_attention": 1,
      "cout_cp": 0,
      "commandes": [
        { "op": "joueur.capital.delta", "joueur_id": "_auto", "delta": 1 },
        {
          "op": "journal",
          "payload": {
            "carte_id": "CC-002",
            "message": "Une réplique percutante en chambre renforce la stature du ministre."
          }
        }
      ]
    },
    {
      "id": "CC-003",
      "nom": "Excuses officielles",
      "type": "contre_coup",
      "copies": 1,
      "cout_attention": 1,
      "cout_cp": 1,
      "commandes": [
        { "op": "capital_collectif.delta", "delta": 1 },
        { "op": "joueur.capital.delta", "joueur_id": "_auto", "delta": -1 },
        {
          "op": "journal",
          "payload": {
            "carte_id": "CC-003",
            "message": "Des excuses officielles apaisent l’opinion au prix d’un peu de capital personnel."
          }
        }
      ]
    },
    {
      "id": "CC-004",
      "nom": "Rapport d’expert rassurant",
      "type": "contre_coup",
      "copies": 1,
      "cout_attention": 1,
      "cout_cp": 1,
      "commandes": [
        { "op": "capital_collectif.delta", "delta": 2 },
        {
          "op": "journal",
          "payload": {
            "carte_id": "CC-004",
            "message": "Un rapport d’expert rassurant réduit la peur dans la population."
          }
        }
      ]
    },
    {
      "id": "CC-005",
      "nom": "Commission d’enquête interne",
      "type": "contre_coup",
      "copies": 1,
      "cout_attention": 1,
      "cout_cp": 0,
      "commandes": [
        { "op": "capital_collectif.delta", "delta": 1 },
        {
          "op": "journal",
          "payload": {
            "carte_id": "CC-005",
            "message": "Une commission d’enquête interne montre que le cabinet prend la situation au sérieux."
          }
        }
      ]
    },
    {
      "id": "CC-006",
      "nom": "Démenti formel",
      "type": "contre_coup",
      "copies": 1,
      "cout_attention": 1,
      "cout_cp": 0,
      "commandes": [
        { "op": "capital_collectif.delta", "delta": 1 },
        {
          "op": "journal",
          "payload": {
            "carte_id": "CC-006",
            "message": "Un démenti formel atténue l’impact d’une rumeur."
          }
        }
      ]
    },
    {
      "id": "CC-007",
      "nom": "Appui d’un partenaire social",
      "type": "contre_coup",
      "copies": 1,
      "cout_attention": 1,
      "cout_cp": 1,
      "commandes": [
        { "op": "capital_collectif.delta", "delta": 1 },
        { "op": "joueur.capital.delta", "joueur_id": "_auto", "delta": 1 },
        {
          "op": "journal",
          "payload": {
            "carte_id": "CC-007",
            "message": "Un partenaire social prend publiquement la défense du cabinet."
          }
        }
      ]
    },
    {
      "id": "CC-008",
      "nom": "Clarification des chiffres",
      "type": "contre_coup",
      "copies": 1,
      "cout_attention": 1,
      "cout_cp": 0,
      "commandes": [
        { "op": "capital_collectif.delta", "delta": 1 },
        {
          "op": "journal",
          "payload": {
            "carte_id": "CC-008",
            "message": "Une mise au point chiffrée corrige un malentendu."
          }
        }
      ]
    },
    {
      "id": "CC-009",
      "nom": "Recentrage du débat",
      "type": "contre_coup",
      "copies": 1,
      "cout_attention": 1,
      "cout_cp": 1,
      "commandes": [
        { "op": "capital_collectif.delta", "delta": 1 },
        {
          "op": "journal",
          "payload": {
            "carte_id": "CC-009",
            "message": "Le cabinet parvient à recentrer le débat sur ses priorités."
          }
        }
      ]
    },
    {
      "id": "CC-010",
      "nom": "Mise en avant d’un succès oublié",
      "type": "contre_coup",
      "copies": 1,
      "cout_attention": 1,
      "cout_cp": 0,
      "commandes": [
        { "op": "capital_collectif.delta", "delta": 1 },
        { "op": "joueur.capital.delta", "joueur_id": "_auto", "delta": 1 },
        {
          "op": "journal",
          "payload": {
            "carte_id": "CC-010",
            "message": "Un ancien succès est remis en lumière pour compenser une mauvaise passe."
          }
        }
      ]
    },
    # ------------------------------------------------------------------
    # 🏛️ Cartes de ministère / appareil d'État (5)
    # ------------------------------------------------------------------
    {
      "id": "MIN-001",
      "nom": "Cabinet ministériel discipliné",
      "type": "ministere",
      "copies": 1,
      "cout_attention": 1,
      "cout_cp": 0,
      "commandes": [
        # un cabinet discipliné libère du temps politique
        { "op": "joueur.attention.delta", "joueur_id": "_auto", "delta": 3 },
        {
          "op": "journal",
          "payload": {
            "carte_id": "MIN-001",
            "message": "L’équipe ministérielle est soudée et libère du temps pour les grands dossiers."
          }
        }
      ]
    },
    {
      "id": "MIN-002",
      "nom": "Directeur de cabinet redoutable",
      "type": "ministere",
      "copies": 1,
      "cout_attention": 1,
      "cout_cp": 0,
      "commandes": [
        # plus d'attention ET une carte discrétionnaire en main
        { "op": "joueur.attention.delta", "joueur_id": "_auto", "delta": 1 },
        { "op": "joueur.piocher", "joueur_id": "_auto", "nb": 1 },
        {
          "op": "journal",
          "payload": {
            "carte_id": "MIN-002",
            "message": "Un directeur de cabinet redoutable maximise votre capacité d’action."
          }
        }
      ]
    },
    {
      "id": "MIN-003",
      "nom": "Haute fonction publique loyale",
      "type": "ministere",
      "copies": 1,
      "cout_attention": 0,
      "cout_cp": 0,
      "commandes": [
        # un léger bonus structurel : une carte et un peu d'attention
        { "op": "joueur.attention.delta", "joueur_id": "_auto", "delta": 1 },
        { "op": "joueur.piocher", "joueur_id": "_auto", "nb": 1 },
        {
          "op": "journal",
          "payload": {
            "carte_id": "MIN-003",
            "message": "La haute fonction publique soutient discrètement votre agenda."
          }
        }
      ]
    },
    {
      "id": "MIN-004",
      "nom": "Réseau administratif efficace",
      "type": "ministere",
      "copies": 1,
      "cout_attention": 1,
      "cout_cp": 0,
      "commandes": [
        { "op": "joueur.attention.delta", "joueur_id": "_auto", "delta": 2 },
        {
          "op": "journal",
          "payload": {
            "carte_id": "MIN-004",
            "message": "Un réseau administratif bien huilé simplifie le traitement des dossiers."
          }
        }
      ]
    },
    {
      "id": "MIN-005",
      "nom": "Sous-ministre stratégique",
      "type": "ministere",
      "copies": 1,
      "cout_attention": 1,
      "cout_cp": 0,
      "commandes": [
        { "op": "joueur.attention.delta", "joueur_id": "_auto", "delta": 1 },
        { "op": "joueur.piocher", "joueur_id": "_auto", "nb": 2 },
        {
          "op": "journal",
          "payload": {
            "carte_id": "MIN-005",
            "message": "Un sous-ministre stratégique anticipe les risques et ouvre des possibilités."
          }
        }
      ]
    },
    # ------------------------------------------------------------------
    # 🎭 Cartes de relations interpersonnelles / coups de couteau (5)
    # ------------------------------------------------------------------
    {
      "id": "REL-001",
      "nom": "Soutien public à un collègue",
      "type": "relation",
      "copies": 1,
      "cout_attention": 1,
      "cout_cp": 1,
      "commandes": [
        { "op": "capital_collectif.delta", "delta": 1 },
        # le collègue ciblé gagnera du capital ; à gérer par le moteur
        {
          "op": "journal",
          "payload": {
            "carte_id": "REL-001",
            "message": "Vous prenez publiquement la défense d’un collègue, renforçant l’image d’unité du cabinet."
          }
        }
      ]
    },
    {
      "id": "REL-002",
      "nom": "Négociation de coulisses",
      "type": "relation",
      "copies": 1,
      "cout_attention": 2,
      "cout_cp": 0,
      "commandes": [
        { "op": "joueur.capital.delta", "joueur_id": "_auto", "delta": 2 },
        {
          "op": "journal",
          "payload": {
            "carte_id": "REL-002",
            "message": "Une négociation de coulisses améliore votre position dans le cabinet."
          }
        }
      ]
    },
    {
      "id": "REL-003",
      "nom": "Fuite anonyme contrôlée",
      "type": "relation",
      "copies": 1,
      "cout_attention": 1,
      "cout_cp": 0,
      "commandes": [
        { "op": "capital_collectif.delta", "delta": -1 },
        { "op": "joueur.capital.delta", "joueur_id": "_auto", "delta": 2 },
        {
          "op": "journal",
          "payload": {
            "carte_id": "REL-003",
            "message": "Une fuite anonyme affaiblit le cabinet mais sert vos intérêts personnels."
          }
        }
      ]
    },
    {
      "id": "REL-004",
      "nom": "Solidarité discrète",
      "type": "relation",
      "copies": 1,
      "cout_attention": 1,
      "cout_cp": 0,
      "commandes": [
        { "op": "capital_collectif.delta", "delta": 1 },
        {
          "op": "journal",
          "payload": {
            "carte_id": "REL-004",
            "message": "Vous soutenez discrètement un collègue clé, consolidant l’esprit de corps."
          }
        }
      ]
    },
    {
      "id": "REL-005",
      "nom": "Démission fracassante",
      "type": "relation",
      "copies": 1,
      "cout_attention": 2,
      "cout_cp": 0,
      "commandes": [
        # 3 événements mondiaux tirés et exécutés – agitation maximale
        { "op": "evt.piocher" },
        { "op": "evt.executer" },
        { "op": "evt.piocher" },
        { "op": "evt.executer" },
        { "op": "evt.piocher" },
        { "op": "evt.executer" },
        # signal spécial pour que le moteur/skin gère le remplaçant du ministre
        {
          "op": "joueur.demission_fracassante",
          "joueur_id": "_auto",
          "mode": "remplacant_moyenne_capital"
        },
        {
          "op": "journal",
          "payload": {
            "carte_id": "REL-005",
            "message": "Démission fracassante : le ministre claque la porte. Un remplaçant reviendra au prochain tour avec un capital proche de la moyenne du cabinet."
          }
        }
      ]
    },

    {
      "id": "MES-001",
      "nom": "Investir dans les hôpitaux",
      "type": "mesure",
      "copies": 1,
      "cout_attention": 3,
      "cout_cp": 0,
      "commandes": [
        { "op": "axes.delta", "axe": "social", "delta": 2 },
        { "op": "eco.delta_depenses", "postes": { "sante": 2 } },
        { "op": "eco.delta_dette", "montant": 2 },
        {
          "op": "journal",
          "type": "mesure",
          "payload": {
            "carte_id": "MES-001",
            "message": "Renforcement du système de santé."
          }
        }
      ]
    },
    {
      "id": "MES-002",
      "nom": "Coupures budgétaires ciblées",
      "type": "mesure",
      "copies": 2,
      "cout_attention": 2,
      "cout_cp": 0,
      "commandes": [
        { "op": "axes.delta", "axe": "social", "delta": -1 },
        { "op": "axes.delta", "axe": "economique", "delta": 1 },
        { "op": "eco.delta_depenses", "postes": { "administration": -2, "defense": -1 } },
        { "op": "eco.delta_dette", "montant": -2 },
        {
          "op": "journal",
          "payload": {
            "carte_id": "MES-002",
            "message": "Plan d’austérité ciblée annoncé."
          }
        }
      ]
    },
    {
      "id": "MES-003",
      "nom": "Plan vert national",
      "type": "mesure",
      "copies": 1,
      "cout_attention": 3,
      "cout_cp": 0,
      "commandes": [
        { "op": "axes.delta", "axe": "environnement", "delta": 2 },
        { "op": "axes.delta", "axe": "economique", "delta": -1 },
        { "op": "eco.delta_depenses", "postes": { "environnement": 3 } },
        { "op": "eco.delta_dette", "montant": 3 },
        {
          "op": "journal",
          "payload": {
            "carte_id": "MES-003",
            "message": "Lancement d’un grand plan de transition écologique."
          }
        }
      ]
    },
    {
      "id": "MES-004",
      "nom": "Baisse d’impôts pour les particuliers",
      "type": "mesure",
      "copies": 2,
      "cout_attention": 1,
      "cout_cp": 0,
      "commandes": [
        { "op": "axes.delta", "axe": "social", "delta": 1 },
        { "op": "axes.delta", "axe": "economique", "delta": 1 },
        { "op": "eco.delta_recettes", "bases": { "base_part": -2 } },
        { "op": "eco.delta_dette", "montant": 2 },
        {
          "op": "journal",
          "payload": {
            "carte_id": "MES-004",
            "message": "Allègement fiscal pour les ménages."
          }
        }
      ]
    },
    {
      "id": "MES-005",
      "nom": "Hausse d’impôts pour les entreprises",
      "type": "mesure",
      "copies": 2,
      "cout_attention": 1,
      "cout_cp": 0,
      "commandes": [
        { "op": "axes.delta", "axe": "economique", "delta": -1 },
        { "op": "axes.delta", "axe": "social", "delta": 1 },
        { "op": "eco.delta_recettes", "bases": { "base_ent": 2 } },
        { "op": "eco.delta_dette", "montant": -1 },
        {
          "op": "journal",
          "payload": {
            "carte_id": "MES-005",
            "message": "Augmentation de la fiscalité sur les entreprises."
          }
        }
      ]
    },
    {
      "id": "MES-006",
      "nom": "Grand plan d’infrastructures",
      "type": "mesure",
      "copies": 2,
      "cout_attention": 2,
      "cout_cp": 0,
      "commandes": [
        { "op": "axes.delta", "axe": "economique", "delta": 2 },
        { "op": "axes.delta", "axe": "social", "delta": 1 },
        { "op": "eco.delta_depenses", "postes": { "infrastructures": 3 } },
        { "op": "eco.delta_dette", "montant": 4 },
        {
          "op": "journal",
          "payload": {
            "carte_id": "MES-006",
            "message": "L’État lance un vaste plan d’infrastructures."
          }
        }
      ]
    },
    {
      "id": "MES-007",
      "nom": "Réforme institutionnelle",
      "type": "mesure",
      "copies": 2,
      "cout_attention": 2,
      "cout_cp": 0,
      "commandes": [
        { "op": "axes.delta", "axe": "institutionnel", "delta": 2 },
        {
          "op": "journal",
          "payload": {
            "carte_id": "MES-007",
            "message": "Réforme pour renforcer l’indépendance des institutions."
          }
        }
      ]
    },
    {
      "id": "MES-008",
      "nom": "Privatisation partielle",
      "type": "mesure",
      "copies": 1,
      "cout_attention": 1,
      "cout_cp": 0,
      "commandes": [
        { "op": "axes.delta", "axe": "economique", "delta": 2 },
        { "op": "axes.delta", "axe": "social", "delta": -2 },
        { "op": "eco.delta_depenses", "postes": { "administration": -2 } },
        { "op": "eco.delta_dette", "montant": -3 },
        {
          "op": "journal",
          "payload": {
            "carte_id": "MES-008",
            "message": "Privatisation partielle d’un service public stratégique."
          }
        }
      ]
    }
  ],

  "events": [
    {
      "id": "EVT-001",
      "nom": "Crise énergétique mondiale",
      "type": "evenement",
      "commandes": [
        { "op": "axes.delta", "axe": "economique", "delta": -2 },
        { "op": "axes.delta", "axe": "environnement", "delta": -1 },
        { "op": "eco.delta_recettes", "bases": { "base_ressources": -2 } },
        { "op": "eco.delta_depenses", "postes": { "infrastructures": 1, "environnement": 1 } },
        { "op": "opposition.capital.delta", "delta": 1 },
        {
          "op": "journal",
          "type": "evenement",
          "payload": {
            "evenement_id": "EVT-001",
            "message": "Une crise énergétique mondiale frappe le pays."
          }
        }
      ]
    },
    {
      "id": "OPP-001",
      "nom": "Scandale mal géré",
      "type": "evenement",
      "commandes": [
        { "op": "capital_collectif.delta", "delta": -4 },
        { "op": "opposition.capital.delta", "delta": 4 },
        {
          "op": "opposition.data.delta",
          "cle": "adhesion",
          "delta": 1
        }
      ]
    },
    {
      "id": "EVT-002",
      "nom": "Mouvement social d’ampleur",
      "type": "evenement",
      "commandes": [
        { "op": "axes.delta", "axe": "social", "delta": -2 },
        { "op": "axes.delta", "axe": "institutionnel", "delta": -1 },
        { "op": "eco.delta_depenses", "postes": { "sante": 1, "administration": 1 } },
        { "op": "capital_collectif.delta", "delta": -4 },
        { "op": "opposition.capital.delta", "delta": 4 },
        {
          "op": "journal",
          "payload": {
            "evenement_id": "EVT-002",
            "message": "Grèves et manifestations paralysent une partie du pays."
          }
        }
      ]
    },
    {
      "id": "EVT-003",
      "nom": "Boom économique inattendu",
      "type": "evenement",
      "commandes": [
        { "op": "axes.delta", "axe": "economique", "delta": 2 },
        { "op": "axes.delta", "axe": "social", "delta": 1 },
        { "op": "eco.delta_recettes", "bases": { "base_part": 2, "base_ent": 2 } },
        { "op": "eco.delta_dette", "montant": -3 },
        { "op": "opposition.capital.delta", "delta": 2 },
        {
          "op": "journal",
          "payload": {
            "evenement_id": "EVT-003",
            "message": "La croissance dépasse toutes les prévisions."
          }
        }
      ]
    },
  {
    "id": "EVT-004",
    "nom": "Crise sanitaire régionale",
    "type": "evenement",
    "commandes": [
      { "op": "axes.delta", "axe": "social", "delta": -1 },
      { "op": "axes.delta", "axe": "institutionnel", "delta": -1 },
      { "op": "eco.delta_depenses", "postes": { "sante": 2 } },
        { "op": "capital_collectif.delta", "delta": -4 },
        { "op": "opposition.capital.delta", "delta": 4 },
      {
        "op": "journal",
        "payload": {
          "evenement_id": "EVT-004",
          "message": "Une crise sanitaire régionale met sous pression les services de santé."
        }
      }
    ]
  },
  {
    "id": "EVT-005",
    "nom": "Dérapage budgétaire surprise",
    "type": "evenement",
    "commandes": [
      { "op": "eco.delta_depenses", "postes": { "administration": 2 } },
      { "op": "axes.delta", "axe": "institutionnel", "delta": -1 },
      { "op": "eco.delta_dette", "montant": 3 },
        { "op": "capital_collectif.delta", "delta": -4 },
        { "op": "opposition.capital.delta", "delta": 4 },
      {
        "op": "journal",
        "payload": {
          "evenement_id": "EVT-005",
          "message": "Un dérapage budgétaire surprise alimente les critiques sur la gestion publique."
        }
      }
    ]
  },
  {
    "id": "EVT-006",
    "nom": "Sécheresse prolongée",
    "type": "evenement",
    "commandes": [
      { "op": "axes.delta", "axe": "environnement", "delta": -2 },
      { "op": "axes.delta", "axe": "economique", "delta": -1 },
      { "op": "eco.delta_depenses", "postes": { "environnement": 1, "infrastructures": 1 } },
      {
        "op": "journal",
        "payload": {
          "evenement_id": "EVT-006",
          "message": "Une sécheresse prolongée fragilise les secteurs agricoles et énergétiques."
        }
      }
    ]
  },
  {
    "id": "EVT-007",
    "nom": "Révélations médiatiques",
    "type": "evenement",
    "commandes": [
      { "op": "capital_collectif.delta", "delta": -1 },
      { "op": "axes.delta", "axe": "institutionnel", "delta": -1 },
      { "op": "opposition.capital.delta", "delta": 2 },
      {
        "op": "journal",
        "payload": {
          "evenement_id": "EVT-007",
          "message": "Des révélations médiatiques fragilisent l’image du cabinet."
        }
      }
    ]
  },
  {
    "id": "EVT-008",
    "nom": "Partenariat économique international",
    "type": "evenement",
    "commandes": [
      { "op": "axes.delta", "axe": "economique", "delta": 2 },
      { "op": "eco.delta_depenses", "postes": { "infrastructures": 1 } },
      {
        "op": "journal",
        "payload": {
          "evenement_id": "EVT-008",
          "message": "Un partenariat économique international ouvre de nouveaux marchés."
        }
      }
    ]
  },
  {
    "id": "EVT-009",
    "nom": "Cyberattaque coordonnée",
    "type": "evenement",
    "commandes": [
      { "op": "axes.delta", "axe": "institutionnel", "delta": -2 },
      { "op": "eco.delta_depenses", "postes": { "administration": 2 } },
        { "op": "capital_collectif.delta", "delta": -2 },
        { "op": "opposition.capital.delta", "delta": 2 },
      {
        "op": "journal",
        "payload": {
          "evenement_id": "EVT-009",
          "message": "Une cyberattaque d’envergure perturbe les services gouvernementaux."
        }
      }
    ]
  },
  {
    "id": "EVT-010",
    "nom": "Mobilisation citoyenne positive",
    "type": "evenement",
    "commandes": [
      { "op": "axes.delta", "axe": "social", "delta": 1 },
      { "op": "axes.delta", "axe": "institutionnel", "delta": 1 },
      {
        "op": "journal",
        "payload": {
          "evenement_id": "EVT-010",
          "message": "Une mobilisation citoyenne constructive améliore le climat social."
        }
      }
    ]
  },
  {
    "id": "EVT-011",
    "nom": "Problème de corruption locale",
    "type": "evenement",
    "commandes": [
      { "op": "axes.delta", "axe": "institutionnel", "delta": -2 },
      { "op": "capital_collectif.delta", "delta": -1 },
      { "op": "opposition.capital.delta", "delta": 1 },
      {
        "op": "journal",
        "payload": {
          "evenement_id": "EVT-011",
          "message": "Un scandale local ravive les inquiétudes sur l’intégrité du pouvoir."
        }
      }
    ]
  },
  {
    "id": "EVT-012",
    "nom": "Innovation technologique majeure",
    "type": "evenement",
    "commandes": [
      { "op": "axes.delta", "axe": "economique", "delta": 2 },
      { "op": "axes.delta", "axe": "environnement", "delta": 1 },
      { "op": "eco.delta_recettes", "bases": { "base_ent": 1 } },
      {
        "op": "journal",
        "payload": {
          "evenement_id": "EVT-012",
          "message": "Une innovation technologique stimulante dynamise l’économie."
        }
      }
    ]
  },
  {
    "id": "EVT-013",
    "nom": "Blocage parlementaire",
    "type": "evenement",
    "commandes": [
      { "op": "axes.delta", "axe": "institutionnel", "delta": -1 },
        { "op": "capital_collectif.delta", "delta": -4 },
        { "op": "opposition.capital.delta", "delta": -1 },
      {
        "op": "journal",
        "payload": {
          "evenement_id": "EVT-013",
          "message": "Un blocage parlementaire entrave l’action gouvernementale."
        }
      }
    ]
  },
  {
    "id": "EVT-014",
    "nom": "Opportunité géopolitique",
    "type": "evenement",
    "commandes": [
      { "op": "axes.delta", "axe": "economique", "delta": 1 },
      { "op": "capital_collectif.delta", "delta": 1 },
      {
        "op": "journal",
        "payload": {
          "evenement_id": "EVT-014",
          "message": "Une opportunité géopolitique renforce la stature internationale du cabinet."
        }
      }
    ]
  },
{
  "id": "EVT-015",
  "nom": "Rapport indépendant favorable",
  "type": "evenement",
  "commandes": [
    { "op": "axes.delta", "axe": "institutionnel", "delta": 2 },
    { "op": "axes.delta", "axe": "social", "delta": 1 },
        { "op": "capital_collectif.delta", "delta": -4 },
        { "op": "opposition.capital.delta", "delta": 4 },
    {
      "op": "journal",
      "payload": {
        "evenement_id": "EVT-015",
        "message": "Un rapport indépendant conclut à une gestion rigoureuse des fonds publics, renforçant la confiance dans les institutions."
      }
    }
  ]
},
{
  "id": "EVT-016",
  "nom": "Réforme de transparence réussie",
  "type": "evenement",
  "commandes": [
    { "op": "axes.delta", "axe": "institutionnel", "delta": 2 },
    { "op": "axes.delta", "axe": "economique", "delta": 1 },
    { "op": "eco.delta_depenses", "postes": { "administration": -1 } },
    { "op": "eco.delta_dette", "montant": -1 },
    {
      "op": "journal",
      "payload": {
        "evenement_id": "EVT-016",
        "message": "Une réforme de transparence et de reddition de comptes simplifie l’administration et rassure les acteurs économiques."
      }
    }
  ]
},
{
  "id": "EVT-017",
  "nom": "Crise bancaire interne",
  "type": "evenement",
  "commandes": [
    { "op": "axes.delta", "axe": "economique", "delta": -3 },
    { "op": "axes.delta", "axe": "social", "delta": -1 },
    { "op": "eco.delta_recettes", "bases": { "base_part": -2, "base_ent": -2 } },
    { "op": "eco.delta_depenses", "postes": { "sante": 1, "administration": 1 } },
    { "op": "eco.delta_dette", "montant": 4 },
        { "op": "capital_collectif.delta", "delta": -2 },
        { "op": "opposition.capital.delta", "delta": 2 },
    {
      "op": "journal",
      "payload": {
        "evenement_id": "EVT-017",
        "message": "Une crise bancaire interne fait chuter la confiance des marchés et oblige l’État à intervenir massivement."
      }
    }
  ]
},
{
  "id": "EVT-018",
  "nom": "Hausse brutale des taux d’intérêt",
  "type": "evenement",
  "commandes": [
    { "op": "axes.delta", "axe": "economique", "delta": -2 },
    { "op": "axes.delta", "axe": "social", "delta": -1 },
    { "op": "eco.delta_depenses", "postes": { "administration": 1, "defense": 1 } },
    { "op": "eco.delta_dette", "montant": 3 },
        { "op": "capital_collectif.delta", "delta": -1 },
        { "op": "opposition.capital.delta", "delta": 1 },
    {
      "op": "journal",
      "payload": {
        "evenement_id": "EVT-018",
        "message": "Une hausse brutale des taux d’intérêt renchérit le service de la dette et freine l’investissement."
      }
    }
  ]
},
{
  "id": "EVT-019",
  "nom": "Tensions commerciales avec un partenaire clé",
  "type": "evenement",
  "commandes": [
    { "op": "axes.delta", "axe": "economique", "delta": -1 },
    { "op": "axes.delta", "axe": "institutionnel", "delta": -1 },
    { "op": "eco.delta_recettes", "bases": { "base_ent": -2, "base_ressources": -1 } },
        { "op": "capital_collectif.delta", "delta": -2 },
        { "op": "opposition.capital.delta", "delta": 2 },
    {
      "op": "journal",
      "payload": {
        "evenement_id": "EVT-019",
        "message": "Des tensions commerciales avec un partenaire stratégique perturbent les exportations et font douter de la capacité d’influence du gouvernement."
      }
    }
  ]
},
{
  "id": "EVT-020",
  "nom": "Inondations historiques",
  "type": "evenement",
  "commandes": [
    { "op": "axes.delta", "axe": "environnement", "delta": -3 },
    { "op": "axes.delta", "axe": "social", "delta": -1 },
    { "op": "eco.delta_depenses", "postes": { "sante": 1, "infrastructures": 2 } },
    { "op": "eco.delta_dette", "montant": 3 },
    {
      "op": "journal",
      "payload": {
        "evenement_id": "EVT-020",
        "message": "Des inondations historiques détruisent des infrastructures et forcent l’État à investir massivement dans la reconstruction."
      }
    }
  ]
},
{
  "id": "EVT-021",
  "nom": "Rupture dans la chaîne d’approvisionnement",
  "type": "evenement",
  "commandes": [
    { "op": "axes.delta", "axe": "economique", "delta": -2 },
    { "op": "eco.delta_depenses", "postes": { "infrastructures": 1 } },
    { "op": "eco.delta_recettes", "bases": { "base_ent": -1 } },
    {
      "op": "journal",
      "payload": {
        "evenement_id": "EVT-004",
        "message": "Une rupture dans la chaîne d’approvisionnement perturbe l’économie du pays."
      }
    }
  ]
},
{
  "id": "EVT-022",
  "nom": "Cyberattaque majeure",
  "type": "evenement",
  "commandes": [
    { "op": "axes.delta", "axe": "institutionnel", "delta": -2 },
    { "op": "axes.delta", "axe": "social", "delta": -1 },
    {
      "op": "journal",
      "payload": {
        "evenement_id": "EVT-005",
        "message": "Une cyberattaque paralyse une partie des services publics."
      }
    }
  ]
},
{
  "id": "EVT-023",
  "nom": "Conflit régional à la frontière",
  "type": "evenement",
  "commandes": [
    { "op": "axes.delta", "axe": "institutionnel", "delta": -1 },
    { "op": "axes.delta", "axe": "social", "delta": -1 },
    { "op": "eco.delta_depenses", "postes": { "defense": 2 } },
    {
      "op": "journal",
      "payload": {
        "evenement_id": "EVT-006",
        "message": "Un conflit régional chez un voisin demande une mobilisation diplomatique et militaire."
      }
    }
  ]
},
{
  "id": "EVT-024",
  "nom": "Catastrophe environnementale",
  "type": "evenement",
  "commandes": [
    { "op": "axes.delta", "axe": "environnement", "delta": -2 },
    { "op": "axes.delta", "axe": "social", "delta": -1 },
    { "op": "eco.delta_depenses", "postes": { "environnement": 3, "infrastructures": 2 } },
    { "op": "eco.delta_dette", "montant": 3 },
        { "op": "capital_collectif.delta", "delta": -2 },
        { "op": "opposition.capital.delta", "delta": 1 },
    {
      "op": "journal",
      "payload": {
        "evenement_id": "EVT-007",
        "message": "Une catastrophe environnementale exige une mobilisation nationale."
      }
    }
  ]
},
{
  "id": "EVT-025",
  "nom": "Résurgence d’un scandale passé",
  "type": "evenement",
  "commandes": [
    { "op": "capital_collectif.delta", "delta": -3 },
    { "op": "opposition.capital.delta", "delta": 3 },
    {
      "op": "opposition.data.delta",
      "cle": "adhesion",
      "delta": 1
    },
    {
      "op": "journal",
      "payload": {
        "evenement_id": "EVT-008",
        "message": "Un ancien scandale refait surface et fragilise la crédibilité du cabinet."
      }
    }
  ]
},
{
  "id": "EVT-026",
  "nom": "Percée technologique inattendue",
  "type": "evenement",
  "commandes": [
    { "op": "axes.delta", "axe": "economique", "delta": 2 },
    { "op": "axes.delta", "axe": "institutionnel", "delta": 1 },
    { "op": "eco.delta_recettes", "bases": { "base_ent": 2 } },
    {
      "op": "journal",
      "payload": {
        "evenement_id": "EVT-009",
        "message": "Une percée technologique majeure dope un secteur stratégique."
      }
    }
  ]
},

  ],

  "phases_tour": [
    "INIT_TOUR",
    "EVENEMENT_MONDIAL",
    "PHASE_PROGRAMME",
    "PHASE_VOTE",
    "PHASE_PERTURBATION_VOTE",
    "PHASE_RESOLUTION",
    "PHASE_TRANQUILLE",
    "FIN_TOUR"
  ],

  "phases_signals": {
    "init_tour": "signal.init_tour",
    "EVENEMENT_MONDIAL": "signal.evenement_mondial",
    "PHASE_PROGRAMME": "signal.programme_ouvert",
    "PHASE_VOTE": "signal.vote_ouvert",
    "PHASE_PERTURBATION_VOTE" : "signal.perturbation_vote",
    "PHASE_RESOLUTION": "signal.resolution_programme",
    "PHASE_TRANQUILLE" : "signal.saison_tranquille",
    "PHASE_AGITATION" : "signal.agitation",
    "FIN_TOUR": "signal.fin_tour",
  }
}

