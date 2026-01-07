# services/cabinet/skins/debut_mandat/config.py

SKIN_CONFIG = {
  "id": "nouveau_mandat",
  "nom": "Conseil des ministres – Deuxième mandat du parti du peuple",
  "description": "C'est le deuxième mandat du parti que représentent nos joueurs.  Le peuple est fatigué et l'opposition est en avance.  Notre cabinet doit démontrer de la résilience et avoir le couteau dans les dents !",
  "axes": [
    {
      "id": "social",
      "nom": "Cohésion sociale",
      "valeur_init": -2,
      "seuil_crise": -5,
      "seuil_excellence": 5,
      "poids": 1.0
    },
    {
      "id": "economique",
      "nom": "Performance économique",
      "valeur_init": 1,
      "seuil_crise": -5,
      "seuil_excellence": 5,
      "poids": 1.0
    },
    {
      "id": "environnement",
      "nom": "Transition écologique",
      "valeur_init": -1,
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
              "valeur": 1000,
              "poids_axes": { "institutionnel": -1, "economique": -1 }
          },
          "impot_ent": {
              "valeur": 500,
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
  "capital_opposition_init": 8,
  "opposition_skin_init": { "adhesion": 0 },
  "analyse_skin_init": { "pente_axes": 0 },
  "main_init": 5,
  "nb_tours_max": 7,

  "cartes": [
  
  {
    "id": "REL-601",
    "nom": "Alliance de corridor",
    "type": "relation",
    "copies": 1,
    "cout_attention": 1,
    "cout_cp": 0,
    "commandes": [
      { "op": "joueur.capital.delta", "joueur_id": "_auto", "delta": 2 },
      { "op": "joueur.capital.delta", "joueur_id": "_cible", "delta": 1 },
      {
        "op": "journal",
        "payload": {
          "carte_id": "REL-601",
          "message": "Une entente de corridor renforce l’influence du ministre et de son allié du moment."
        }
      }
    ]
  },
  {
    "id": "REL-602",
    "nom": "Coup de couteau dans le dos (amical)",
    "type": "relation",
    "copies": 1,
    "cout_attention": 2,
    "cout_cp": 0,
    "commandes": [
      { "op": "joueur.capital.delta", "joueur_id": "_cible", "delta": -2 },
      { "op": "joueur.capital.delta", "joueur_id": "_auto", "delta": 1 },
      {
        "op": "journal",
        "payload": {
          "carte_id": "REL-602",
          "message": "Un petit coup de couteau politique — rien de personnel — repositionne avantageusement le ministre."
        }
      }
    ]
  },
  {
    "id": "REL-603",
    "nom": "Rivalité silencieuse mais féroce",
    "type": "relation",
    "copies": 1,
    "cout_attention": 2,
    "cout_cp": 1,
    "commandes": [
      { "op": "joueur.capital.delta", "joueur_id": "_auto", "delta": 2 },
      { "op": "joueur.capital.delta", "joueur_id": "_cible", "delta": -1 },
      { "op": "cabinet.capital.delta", "delta": -1 },
      {
        "op": "journal",
        "payload": {
          "carte_id": "REL-603",
          "message": "Une rivalité feutrée au cabinet commence à miner subtilement la cohésion ministérielle."
        }
      }
    ]
  },
  {
    "id": "REL-604",
    "nom": "Soutien indéfectible (jusqu’à nouvel ordre)",
    "type": "relation",
    "copies": 1,
    "cout_attention": 1,
    "cout_cp": 1,
    "commandes": [
      { "op": "joueur.capital.delta", "joueur_id": "_auto", "delta": 1 },
      { "op": "cabinet.capital.delta", "delta": 2 },
      {
        "op": "journal",
        "payload": {
          "carte_id": "REL-604",
          "message": "Le ministre affirme son soutien total au cabinet… du moins pour aujourd’hui."
        }
      }
    ]
  },
  {
    "id": "REL-605",
    "nom": "Démission théâtrale en conférence de presse",
    "type": "relation",
    "copies": 1,
    "cout_attention": 3,
    "cout_cp": 0,
    "commandes": [
      { "op": "joueur.capital.delta", "joueur_id": "_auto", "delta": 3 },
      { "op": "cabinet.capital.delta", "delta": -2 },
      { "op": "opposition.capital.delta", "delta": 2 },
      {
        "op": "evenement.interne",
        "payload": {
          "type": "demission",
          "message": "Un ministre claque la porte en direct : la machine politique s’affole."
        }
      },
      {
        "op": "journal",
        "payload": {
          "carte_id": "REL-605",
          "message": "Une démission théâtrale secoue les médias et rebat les cartes au cabinet."
        }
      }
    ]
  },
  {
    "id": "INF-501",
    "nom": "Sortie du banc de neige à la Jean Chrétien",
    "type": "influence",
    "copies": 1,
    "cout_attention": 1,
    "cout_cp": 1,
    "commandes": [
      { "op": "cabinet.capital.delta", "delta": 2 },
      { "op": "joueur.capital.delta", "joueur_id": "_auto", "delta": 1 },
      {
        "op": "journal",
        "payload": {
          "carte_id": "INF-501",
          "message": "Avec un sourire (et un petit coup d’épaule), le ministre sort le cabinet d’un banc de neige politique."
        }
      }
    ]
  },
  {
    "id": "INF-502",
    "nom": "Parler franc comme Jean Garon",
    "type": "influence",
    "copies": 1,
    "cout_attention": 2,
    "cout_cp": 0,
    "commandes": [
      { "op": "cabinet.capital.delta", "delta": 3 },
      {
        "op": "journal",
        "payload": {
          "carte_id": "INF-502",
          "message": "Le ministre parle franc, sans flafla : le message passe, même si ça brasse un peu."
        }
      }
    ]
  },
  {
    "id": "INF-503",
    "nom": "Tirer la couverte mais la partager après",
    "type": "influence",
    "copies": 2,
    "cout_attention": 1,
    "cout_cp": 0,
    "commandes": [
      { "op": "cabinet.capital.delta", "delta": 1 },
      { "op": "joueur.capital.delta", "joueur_id": "_auto", "delta": 1 },
      {
        "op": "journal",
        "payload": {
          "carte_id": "INF-503",
          "message": "Le ministre tire la couverte vers son ministère… mais la redonne juste assez pour avoir l’air d’un team player."
        }
      }
    ]
  },
  {
    "id": "INF-504",
    "nom": "Faire une tournée des régions",
    "type": "influence",
    "copies": 1,
    "cout_attention": 2,
    "cout_cp": 0,
    "commandes": [
      { "op": "cabinet.capital.delta", "delta": 2 },
      { "op": "joueur.capital.delta", "joueur_id": "_auto", "delta": 1 },
      {
        "op": "journal",
        "payload": {
          "carte_id": "INF-504",
          "message": "Une tournée des régions bien orchestrée donne un air de proximité et de gros bon sens."
        }
      }
    ]
  },
  {
    "id": "INF-505",
    "nom": "Le grand numéro de gros bon sens",
    "type": "influence",
    "copies": 1,
    "cout_attention": 1,
    "cout_cp": 1,
    "commandes": [
      { "op": "cabinet.capital.delta", "delta": 2 },
      {
        "op": "journal",
        "payload": {
          "carte_id": "INF-505",
          "message": "Un discours rempli de gros bon sens fait oublier quelques maladresses du cabinet."
        }
      }
    ]
  },
  {
    "id": "INF-506",
    "nom": "Remonter les bretelles à la bonne franquette",
    "type": "influence",
    "copies": 1,
    "cout_attention": 2,
    "cout_cp": 0,
    "commandes": [
      { "op": "cabinet.capital.delta", "delta": 2 },
      { "op": "axes.delta", "axe": "institutionnel", "delta": 1 },
      {
        "op": "journal",
        "payload": {
          "carte_id": "INF-506",
          "message": "Le ministre remonte les bretelles à quelques cadres. Résultat : crédibilité accrue."
        }
      }
    ]
  },
  {
    "id": "INF-507",
    "nom": "Une poignée de main qui vaut de l’or",
    "type": "influence",
    "copies": 2,
    "cout_attention": 1,
    "cout_cp": 0,
    "commandes": [
      { "op": "cabinet.capital.delta", "delta": 1 },
      { "op": "joueur.capital.delta", "joueur_id": "_auto", "delta": 1 },
      {
        "op": "journal",
        "payload": {
          "carte_id": "INF-507",
          "message": "Une simple poignée de main captée par les caméras fait grimper la cote du cabinet."
        }
      }
    ]
  },
  {
    "id": "INF-508",
    "nom": "Gérer ça en bon père de famille",
    "type": "influence",
    "copies": 1,
    "cout_attention": 1,
    "cout_cp": 0,
    "commandes": [
      { "op": "cabinet.capital.delta", "delta": 2 },
      {
        "op": "journal",
        "payload": {
          "carte_id": "INF-508",
          "message": "Le ministre apaise les tensions avec un ton posé et rassembleur. « Bon père de famille », qu’ils disent."
        }
      }
    ]
  },
  {
    "id": "INF-509",
    "nom": "Déshabiller Pierre pour habiller Paul.",
    "type": "influence",
    "copies": 1,
    "cout_attention": 2,
    "cout_cp": 1,
    "commandes": [
      { "op": "cabinet.capital.delta", "delta": 3 },
      { "op": "joueur.capital.delta", "joueur_id": "_auto", "delta": 1 },
      {
        "op": "journal",
        "payload": {
          "carte_id": "INF-509",
          "message": "Une réplique bien placée fait éclater de rire l’Assemblée et fait oublier l’opposition quelques minutes."
        }
      }
    ]
  },
  {
    "id": "INF-510",
    "nom": "Opération cordonnier bien chaussé",
    "type": "influence",
    "copies": 1,
    "cout_attention": 1,
    "cout_cp": 0,
    "commandes": [
      { "op": "cabinet.capital.delta", "delta": 2 },
      { "op": "joueur.attention.delta", "delta": 1 },
      {
        "op": "journal",
        "payload": {
          "carte_id": "INF-510",
          "message": "Pour une fois, le cabinet applique à lui-même ce qu’il prêche. La population apprécie."
        }
      }
    ]
  },
  {
    "id": "CTC-401",
    "nom": "On s'autopeludebananise pas aujourd’hui",
    "type": "contre_coup",
    "copies": 2,
    "cout_attention": 1,
    "cout_cp": 0,
    "commandes": [
      { "op": "cabinet.capital.delta", "delta": 1 },
      { "op": "opposition.capital.delta", "delta": -1 },
      {
        "op": "journal",
        "payload": {
          "carte_id": "CTC-401",
          "message": "Le cabinet évite l’autopeludebananisation grâce à une sortie publique habile."
        }
      }
    ]
  },
  {
    "id": "CTC-402",
    "nom": "Clarification urgente (façon conférence de presse à 17h)",
    "type": "contre_coup",
    "copies": 1,
    "cout_attention": 1,
    "cout_cp": 0,
    "commandes": [
      { "op": "cabinet.capital.delta", "delta": 1 },
      { "op": "joueur.capital.delta", "joueur_id": "_auto", "delta": 1 },
      {
        "op": "journal",
        "payload": {
          "carte_id": "CTC-402",
          "message": "Une conférence de presse improvisée calme (un peu) les choses."
        }
      }
    ]
  },
  {
    "id": "CTC-403",
    "nom": "Le pogo le moins dégelé rassure la population",
    "type": "contre_coup",
    "copies": 2,
    "cout_attention": 1,
    "cout_cp": 0,
    "commandes": [
      { "op": "axes.delta", "axe": "social", "delta": 1 },
      { "op": "opposition.capital.delta", "delta": -1 },
      {
        "op": "journal",
        "payload": {
          "carte_id": "CTC-403",
          "message": "Contre toute attente, le pogo le moins dégelé de la boîte rassure tout le monde à la télévision."
        }
      }
    ]
  },
  {
    "id": "CTC-404",
    "nom": "Éteindre le feu avec un seau d’eau tiède",
    "type": "contre_coup",
    "copies": 1,
    "cout_attention": 2,
    "cout_cp": 0,
    "commandes": [
      { "op": "cabinet.capital.delta", "delta": 2 },
      { "op": "axes.delta", "axe": "institutionnel", "delta": 1 },
      {
        "op": "journal",
        "payload": {
          "carte_id": "CTC-404",
          "message": "Une intervention molle, mais efficace. Le feu médiatique s’essouffle."
        }
      }
    ]
  },
  {
    "id": "CTC-405",
    "nom": "Direction de crise : on sort l’artillerie lourde",
    "type": "contre_coup",
    "copies": 1,
    "cout_attention": 2,
    "cout_cp": 1,
    "commandes": [
      { "op": "cabinet.capital.delta", "delta": 2 },
      { "op": "opposition.capital.delta", "delta": -2 },
      {
        "op": "journal",
        "payload": {
          "carte_id": "CTC-405",
          "message": "Une gestion de crise musclée renverse temporairement le rapport de force."
        }
      }
    ]
  },
  {
    "id": "CTC-406",
    "nom": "« Ce n’est pas ça pantoute »",
    "type": "contre_coup",
    "copies": 2,
    "cout_attention": 1,
    "cout_cp": 0,
    "commandes": [
      { "op": "joueur.capital.delta", "joueur_id": "_auto", "delta": 1 },
      { "op": "axes.delta", "axe": "institutionnel", "delta": 1 },
      {
        "op": "journal",
        "payload": {
          "carte_id": "CTC-406",
          "message": "Le ministre affirme que « ce n’est pas ça pantoute ». Étonnamment, ça fonctionne."
        }
      }
    ]
  },
  {
    "id": "CTC-407",
    "nom": "Réponse préventive avant que ça dégénère",
    "type": "contre_coup",
    "copies": 1,
    "cout_attention": 2,
    "cout_cp": 0,
    "commandes": [
      { "op": "cabinet.capital.delta", "delta": 1 },
      { "op": "axes.delta", "axe": "social", "delta": 1 },
      { "op": "axes.delta", "axe": "institutionnel", "delta": 1 },
      {
        "op": "journal",
        "payload": {
          "carte_id": "CTC-407",
          "message": "Un geste préventif évite que la situation s’envenime."
        }
      }
    ]
  },
  {
    "id": "CTC-408",
    "nom": "Faire diversion avec un projet flou",
    "type": "contre_coup",
    "copies": 1,
    "cout_attention": 1,
    "cout_cp": 0,
    "commandes": [
      { "op": "opposition.capital.delta", "delta": -1 },
      { "op": "joueur.attention.delta", "delta": 1 },
      {
        "op": "journal",
        "payload": {
          "carte_id": "CTC-408",
          "message": "On annonce un projet flou qui attire l’attention des médias. L’opposition perd un peu son souffle."
        }
      }
    ]
  },
  {
    "id": "CTC-409",
    "nom": "On calme le jeu au salon bleu",
    "type": "contre_coup",
    "copies": 1,
    "cout_attention": 1,
    "cout_cp": 0,
    "commandes": [
      { "op": "axes.delta", "axe": "institutionnel", "delta": 2 },
      { "op": "cabinet.capital.delta", "delta": 1 },
      {
        "op": "journal",
        "payload": {
          "carte_id": "CTC-409",
          "message": "Une intervention habile au salon bleu apaise l’ambiance électrique."
        }
      }
    ]
  },
  {
    "id": "CTC-410",
    "nom": "C’est le chat du ministre, pas un scandale",
    "type": "contre_coup",
    "copies": 1,
    "cout_attention": 1,
    "cout_cp": 0,
    "commandes": [
      { "op": "joueur.capital.delta", "joueur_id": "_auto", "delta": 2 },
      { "op": "opposition.capital.delta", "delta": -1 },
      {
        "op": "journal",
        "payload": {
          "carte_id": "CTC-410",
          "message": "Après enquête, on confirme : ce n’était pas un scandale, juste le chat du ministre."
        }
      }
    ]
  },
  {
    "id": "MIN-301",
    "nom": "Réingénierie du ministère (pour vrai cette fois)",
    "type": "ministere",
    "copies": 1,
    "cout_attention": 1,
    "cout_cp": 0,
    "commandes": [
      { "op": "joueur.attention.delta", "delta": 2 },
      {
        "op": "journal",
        "payload": {
          "carte_id": "MIN-301",
          "message": "Une réingénierie qui ne se contente pas de changer les logos. Du jamais vu."
        }
      }
    ]
  },
  {
    "id": "MIN-302",
    "nom": "Création du Bureau des bureaux",
    "type": "ministere",
    "copies": 1,
    "cout_attention": 1,
    "cout_cp": 0,
    "commandes": [
      { "op": "joueur.attention.max_delta", "delta": 1 },
      { "op": "joueur.attention.delta", "delta": 1 },
      {
        "op": "journal",
        "payload": {
          "carte_id": "MIN-302",
          "message": "Un nouveau bureau chargé de coordonner les autres bureaux. Personne ne comprend, mais ça fonctionne."
        }
      }
    ]
  },
  {
    "id": "MIN-303",
    "nom": "Armée de stagiaires motivés",
    "type": "ministere",
    "copies": 1,
    "cout_attention": 0,
    "cout_cp": 0,
    "commandes": [
      { "op": "joueur.attention.delta", "delta": 3 },
      {
        "op": "journal",
        "payload": {
          "carte_id": "MIN-303",
          "message": "Une vague de CV enthousiaste submerge le ministère. Productivité en hausse, café en rupture."
        }
      }
    ]
  },
  {
    "id": "MIN-304",
    "nom": "Comité transversal intersectoriel synergique",
    "type": "ministere",
    "copies": 1,
    "cout_attention": 1,
    "cout_cp": 0,
    "commandes": [
      { "op": "joueur.pioche.delta", "delta": 2 },
      {
        "op": "journal",
        "payload": {
          "carte_id": "MIN-304",
          "message": "Un comité au nom très long produit des rapports étonnamment utiles."
        }
      }
    ]
  },
  {
    "id": "MIN-305",
    "nom": "Optimisation des procédures obscures",
    "type": "ministere",
    "copies": 1,
    "cout_attention": 2,
    "cout_cp": 0,
    "commandes": [
      { "op": "joueur.attention.delta", "delta": 2 },
      { "op": "joueur.attention.max_delta", "delta": 1 },
      {
        "op": "journal",
        "payload": {
          "carte_id": "MIN-305",
          "message": "On découvre que certaines règles existaient encore depuis 1978. On les retire et tout va mieux."
        }
      }
    ]
  },
  {
    "id": "MIN-306",
    "nom": "Accélérateur législatif",
    "type": "ministere",
    "copies": 1,
    "cout_attention": 1,
    "cout_cp": 1,
    "commandes": [
      { "op": "joueur.attention.delta", "delta": 1 },
      { "op": "joueur.attention_reduction_couts", "delta": 1 },
      {
        "op": "journal",
        "payload": {
          "carte_id": "MIN-306",
          "message": "Un mystérieux appareil accélère le traitement législatif. Certains y voient de la magie."
        }
      }
    ]
  },
  {
    "id": "MIN-307",
    "nom": "Intelligence artificielle à moitié fiable",
    "type": "ministere",
    "copies": 1,
    "cout_attention": 1,
    "cout_cp": 0,
    "commandes": [
      { "op": "joueur.pioche.delta", "delta": 1 },
      { "op": "joueur.attention.delta", "delta": 2 },
      {
        "op": "journal",
        "payload": {
          "carte_id": "MIN-307",
          "message": "L’IA règle 30 % des dossiers automatiquement. Les autres 70 % deviennent… créatifs."
        }
      }
    ]
  },
  {
    "id": "MIN-308",
    "nom": "Grand ménage des formulaires",
    "type": "ministere",
    "copies": 1,
    "cout_attention": 2,
    "cout_cp": 0,
    "commandes": [
      { "op": "joueur.attention.delta", "delta": 3 },
      {
        "op": "journal",
        "payload": {
          "carte_id": "MIN-308",
          "message": "On élimine 47 formulaires qui ne servaient plus. Le personnel fête en silence."
        }
      }
    ]
  },
  {
    "id": "MIN-309",
    "nom": "Sous-ministre superstar",
    "type": "ministere",
    "copies": 1,
    "cout_attention": 1,
    "cout_cp": 1,
    "commandes": [
      { "op": "joueur.attention.max_delta", "delta": 2 },
      { "op": "joueur.attention.delta", "delta": 2 },
      {
        "op": "journal",
        "payload": {
          "carte_id": "MIN-309",
          "message": "Ce sous-ministre gère trois crises avant 9h. Un talent rare."
        }
      }
    ]
  },
  {
    "id": "MIN-310",
    "nom": "Décentralisation improvisée",
    "type": "ministere",
    "copies": 1,
    "cout_attention": 0,
    "cout_cp": 0,
    "commandes": [
      { "op": "joueur.pioche.delta", "delta": 1 },
      { "op": "joueur.attention.delta", "delta": 1 },
      {
        "op": "journal",
        "payload": {
          "carte_id": "MIN-310",
          "message": "Chaque région décide un peu n’importe quoi… mais ça dégage de l’espace au ministère."
        }
      }
    ]
  },
  {
    "id": "MIN-311",
    "nom": "Modernisation du fax gouvernemental",
    "type": "ministere",
    "copies": 1,
    "cout_attention": 1,
    "cout_cp": 0,
    "commandes": [
      { "op": "joueur.attention.delta", "delta": 2 },
      { "op": "joueur.pioche.delta", "delta": 1 },
      {
        "op": "journal",
        "payload": {
          "carte_id": "MIN-311",
          "message": "On remplace enfin le fax de 1994. Les fonctionnaires pleurent de joie."
        }
      }
    ]
  },
  {
    "id": "MIN-312",
    "nom": "Plan Excel de consolidation",
    "type": "ministere",
    "copies": 1,
    "cout_attention": 2,
    "cout_cp": 0,
    "commandes": [
      { "op": "joueur.attention.max_delta", "delta": 1 },
      { "op": "joueur.pioche.delta", "delta": 2 },
      {
        "op": "journal",
        "payload": {
          "carte_id": "MIN-312",
          "message": "Un super-fichier Excel miraculeux qui agrège tout. Personne ne sait comment il marche."
        }
      }
    ]
  },
  {
    "id": "MIN-313",
    "nom": "Restructuration par organigramme vert",
    "type": "ministere",
    "copies": 1,
    "cout_attention": 1,
    "cout_cp": 0,
    "commandes": [
      { "op": "joueur.attention.delta", "delta": 1 },
      { "op": "joueur.attention_reduction_couts", "delta": 1 },
      {
        "op": "journal",
        "payload": {
          "carte_id": "MIN-313",
          "message": "Un nouvel organigramme « durable » réduit d’étranges doublons administratifs."
        }
      }
    ]
  },
  {
    "id": "MIN-314",
    "nom": "Groupe de travail secret (mais pas tant que ça)",
    "type": "ministere",
    "copies": 1,
    "cout_attention": 2,
    "cout_cp": 1,
    "commandes": [
      { "op": "joueur.pioche.delta", "delta": 3 },
      {
        "op": "journal",
        "payload": {
          "carte_id": "MIN-314",
          "message": "Un groupe de travail confidentiel génère des idées franchement brillantes."
        }
      }
    ]
  },
  {
    "id": "MIN-315",
    "nom": "Task force d’urgence sur tout et rien",
    "type": "ministere",
    "copies": 1,
    "cout_attention": 1,
    "cout_cp": 0,
    "commandes": [
      { "op": "joueur.attention.delta", "delta": 2 },
      { "op": "joueur.pioche.delta", "delta": 1 },
      {
        "op": "journal",
        "payload": {
          "carte_id": "MIN-315",
          "message": "Une task force qui semble toujours être « en réunion » mais livre des résultats surprenants."
        }
      }
    ]
  },
    {
      "id": "MES-201",
      "nom": "Grand plan béton d’infrastructures",
      "type": "mesure",
      "copies": 2,
      "cout_attention": 3,
      "cout_cp": 0,
      "commandes": [
        { "op": "axes.delta", "axe": "institutionnel", "delta": 2 },
        { "op": "axes.delta", "axe": "social", "delta": 1 },
        { "op": "eco.delta_depenses", "postes": { "infrastructures": 3 } },
        { "op": "eco.delta_dette", "montant": 2 },
        {
          "op": "journal",
          "type": "mesure",
          "payload": {
            "carte_id": "MES-201",
            "message": "L’État promet de rattraper 30 ans de retard en 4 ans. On ressort les cônes orange."
          }
        }
      ]
    },
    {
      "id": "MES-202",
      "nom": "Rabais électoral sur l’essence",
      "type": "mesure",
      "copies": 2,
      "cout_attention": 2,
      "cout_cp": 1,
      "commandes": [
        { "op": "axes.delta", "axe": "social", "delta": 2 },
        { "op": "axes.delta", "axe": "environnement", "delta": -2 },
        { "op": "eco.delta_recettes", "bases": { "base_part": -2 } },
        { "op": "eco.delta_dette", "montant": 1 },
        {
          "op": "journal",
          "type": "mesure",
          "payload": {
            "carte_id": "MES-202",
            "message": "Rabais temporaire à la pompe : tout le monde sait que c’est électoral, mais ça fait du bien pareil."
          }
        }
      ]
    },
    {
      "id": "MES-203",
      "nom": "Méga-plan climat turbo-vert",
      "type": "mesure",
      "copies": 1,
      "cout_attention": 4,
      "cout_cp": 1,
      "commandes": [
        { "op": "axes.delta", "axe": "environnement", "delta": 3 },
        { "op": "axes.delta", "axe": "economique", "delta": -2 },
        { "op": "eco.delta_recettes", "bases": { "base_ent": -1 } },
        { "op": "eco.delta_dette", "montant": 1 },
        {
          "op": "journal",
          "type": "mesure",
          "payload": {
            "carte_id": "MES-203",
            "message": "Le gouvernement annonce un plan climat « historique ». Les lobbyistes cherchent déjà la note en bas de page."
          }
        }
      ]
    },
    {
      "id": "MES-204",
      "nom": "Révolution administrative 4.0",
      "type": "mesure",
      "copies": 1,
      "cout_attention": 3,
      "cout_cp": 0,
      "commandes": [
        { "op": "axes.delta", "axe": "institutionnel", "delta": 1 },
        { "op": "axes.delta", "axe": "economique", "delta": 1 },
        { "op": "eco.delta_depenses", "postes": { "numerique": 2 } },
        { "op": "eco.delta_dette", "montant": 1 },
        {
          "op": "journal",
          "type": "mesure",
          "payload": {
            "carte_id": "MES-204",
            "message": "On promet de « simplifier l’État » en ajoutant trois nouveaux portails, deux comités et un identifiant unique."
          }
        }
      ]
    },
    {
      "id": "MES-205",
      "nom": "Opération séduction des aînés",
      "type": "mesure",
      "copies": 2,
      "cout_attention": 2,
      "cout_cp": 0,
      "commandes": [
        { "op": "axes.delta", "axe": "social", "delta": 2 },
        { "op": "eco.delta_depenses", "postes": { "sante": 1, "habitation": 1 } },
        { "op": "eco.delta_dette", "montant": 1 },
        {
          "op": "journal",
          "type": "mesure",
          "payload": {
            "carte_id": "MES-205",
            "message": "Chèque ciblé, crédits d’impôt, nouvelle pub avec un petit-fils : les aînés sont officiellement en tournée."
          }
        }
      ]
    },
    {
      "id": "MES-206",
      "nom": "Coupures discrètes dans les trucs plates",
      "type": "mesure",
      "copies": 1,
      "cout_attention": 2,
      "cout_cp": 0,
      "commandes": [
        { "op": "axes.delta", "axe": "social", "delta": -2 },
        { "op": "axes.delta", "axe": "economique", "delta": 1 },
        { "op": "eco.delta_recettes", "bases": { "base_part": 1 } },
        { "op": "eco.delta_dette", "montant": -1 },
        {
          "op": "journal",
          "type": "mesure",
          "payload": {
            "carte_id": "MES-206",
            "message": "On coupe dans « ce que personne ne regarde ». Surprise : quelqu’un regardait."
          }
        }
      ]
    },
    {
      "id": "MES-207",
      "nom": "Pacte fiscal soi-disant temporaire",
      "type": "mesure",
      "copies": 1,
      "cout_attention": 3,
      "cout_cp": 1,
      "commandes": [
        { "op": "axes.delta", "axe": "economique", "delta": 1 },
        { "op": "axes.delta", "axe": "social", "delta": -1 },
        { "op": "eco.delta_recettes", "bases": { "base_part": 2 } },
        { "op": "eco.delta_dette", "montant": -1 },
        {
          "op": "journal",
          "type": "mesure",
          "payload": {
            "carte_id": "MES-207",
            "message": "Un pacte fiscal « temporaire » qui a toutes les caractéristiques d’un truc permanent."
          }
        }
      ]
    },
    {
      "id": "MES-208",
      "nom": "Commission d’enquête préventive",
      "type": "mesure",
      "copies": 1,
      "cout_attention": 2,
      "cout_cp": 0,
      "commandes": [
        { "op": "axes.delta", "axe": "institutionnel", "delta": 2 },
        { "op": "eco.delta_depenses", "postes": { "justice": 2 } },
        { "op": "eco.delta_dette", "montant": 1 },
        {
          "op": "journal",
          "type": "mesure",
          "payload": {
            "carte_id": "MES-208",
            "message": "Le gouvernement lance une commission d’enquête avant même que le scandale n’éclate. On gagne du temps… peut-être."
          }
        }
      ]
    }
  ],

  "events": [
      {
        "id": "EVT-QC-001",
        "nom": "Crise du logement exacerbé",
        "type": "evenement",
        "commandes": [
          { "op": "axes.delta", "axe": "social", "delta": -3 },
          { "op": "axes.delta", "axe": "institutionnel", "delta": -1 },
          { "op": "eco.delta_depenses", "postes": { "habitation": 2 } },
          {
            "op": "opposition.capital.delta",
            "delta": 3
          },
          {
            "op": "journal",
            "payload": {
              "evenement_id": "EVT-QC-001",
              "message": "Une hausse explosive des loyers dans les grands centres alimente une crise du logement."
            }
          }
        ]
      },
      {
        "id": "EVT-QC-002",
        "nom": "Inondations printanières majeures",
        "type": "evenement",
        "commandes": [
          { "op": "axes.delta", "axe": "environnement", "delta": -3 },
          { "op": "axes.delta", "axe": "social", "delta": -1 },
          { "op": "eco.delta_depenses", "postes": { "urgence": 2 } },
          {
            "op": "opposition.capital.delta",
            "delta": 2
          },
          {
            "op": "journal",
            "payload": {
              "evenement_id": "EVT-QC-002",
              "message": "Des inondations printanières majeures forcent l’évacuation de milliers de citoyens."
            }
          }
        ]
      },
      {
        "id": "EVT-QC-003",
        "nom": "Conflit de travail dans le secteur public",
        "type": "evenement",
        "commandes": [
          { "op": "axes.delta", "axe": "social", "delta": -2 },
          { "op": "axes.delta", "axe": "institutionnel", "delta": -1 },
          { "op": "axes.delta", "axe": "economique", "delta": -1 },
          {
            "op": "opposition.capital.delta",
            "delta": 3
          },
          {
            "op": "journal",
            "payload": {
              "evenement_id": "EVT-QC-003",
              "message": "Un conflit de travail dans le secteur public entraîne grèves et perturbations des services."
            }
          }
        ]
      },
      {
        "id": "EVT-QC-004",
        "nom": "Défaillance d’un pont stratégique",
        "type": "evenement",
        "commandes": [
          { "op": "axes.delta", "axe": "institutionnel", "delta": -2 },
          { "op": "axes.delta", "axe": "social", "delta": -1 },
          { "op": "eco.delta_depenses", "postes": { "infrastructures": 3 } },
          { "op": "eco.delta_dette", "montant": 1 },
          {
            "op": "journal",
            "payload": {
              "evenement_id": "EVT-QC-004",
              "message": "La fermeture d’un pont stratégique révèle l’état critique des infrastructures."
            }
          }
        ]
      },
      {
        "id": "EVT-QC-005",
        "nom": "Crise dans les urgences hospitalières",
        "type": "evenement",
        "commandes": [
          { "op": "axes.delta", "axe": "social", "delta": -2 },
          { "op": "eco.delta_depenses", "postes": { "sante": 2 } },
          {
            "op": "opposition.capital.delta",
            "delta": 3
          },
          {
            "op": "journal",
            "payload": {
              "evenement_id": "EVT-QC-005",
              "message": "Les urgences hospitalières débordent et exposent les failles du réseau de la santé."
            }
          }
        ]
      },
      {
        "id": "EVT-QC-006",
        "nom": "Découverte d’un nouveau gisement nordique",
        "type": "evenement",
        "commandes": [
          { "op": "axes.delta", "axe": "economique", "delta": 3 },
          { "op": "axes.delta", "axe": "environnement", "delta": -1 },
          { "op": "eco.delta_recettes", "bases": { "base_ent": 2 } },
          {
            "op": "opposition.capital.delta",
            "delta": -1
          },
          {
            "op": "journal",
            "payload": {
              "evenement_id": "EVT-QC-006",
              "message": "La découverte d’un gisement nordique prometteur relance l’activité économique."
            }
          }
        ]
      },
      {
        "id": "EVT-QC-007",
        "nom": "Débâcle informatique gouvernementale",
        "type": "evenement",
        "commandes": [
          { "op": "axes.delta", "axe": "institutionnel", "delta": -3 },
          { "op": "opposition.capital.delta", "delta": 4 },
          { "op": "cabinet.capital.delta", "delta": -1 },
          {
            "op": "journal",
            "payload": {
              "evenement_id": "EVT-QC-007",
              "message": "L’échec retentissant d’un grand système informatique mine la confiance envers le gouvernement."
            }
          }
        ]
      },
      {
        "id": "EVT-QC-008",
        "nom": "Montée spectaculaire d’un parti tiers",
        "type": "evenement",
        "commandes": [
          { "op": "axes.delta", "axe": "institutionnel", "delta": -1 },
          { "op": "axes.delta", "axe": "social", "delta": -1 },
          { "op": "opposition.capital.delta", "delta": 5 },
          {
            "op": "journal",
            "payload": {
              "evenement_id": "EVT-QC-008",
              "message": "La montée d’un nouveau parti tiers bouleverse l’équilibre politique traditionnel."
            }
          }
        ]
      },
      {
        "id": "EVT-QC-009",
        "nom": "Surtension inflationniste",
        "type": "evenement",
        "commandes": [
          { "op": "axes.delta", "axe": "social", "delta": -2 },
          { "op": "axes.delta", "axe": "economique", "delta": -1 },
          { "op": "eco.delta_recettes", "bases": { "base_part": 1 } },
          { "op": "opposition.capital.delta", "delta": 3 },
          {
            "op": "journal",
            "payload": {
              "evenement_id": "EVT-QC-009",
              "message": "L’inflation sur l’épicerie et l’essence érode le pouvoir d’achat des ménages."
            }
          }
        ]
      },
      {
        "id": "EVT-QC-010",
        "nom": "Condamnation environnementale d’Ottawa",
        "type": "evenement",
        "commandes": [
          { "op": "axes.delta", "axe": "environnement", "delta": 1 },
          { "op": "axes.delta", "axe": "institutionnel", "delta": -2 },
          { "op": "opposition.capital.delta", "delta": 1 },
          {
            "op": "journal",
            "payload": {
              "evenement_id": "EVT-QC-010",
              "message": "Ottawa impose de nouvelles normes environnementales, exacerbant les tensions fédérales-provinciales."
            }
          }
        ]
      },
      {
        "id": "EVT-QC-011",
        "nom": "Pénurie de main-d’œuvre généralisée",
        "type": "evenement",
        "commandes": [
          { "op": "axes.delta", "axe": "economique", "delta": -1 },
          { "op": "axes.delta", "axe": "social", "delta": -1 },
          { "op": "opposition.capital.delta", "delta": 1 },
          {
            "op": "journal",
            "payload": {
              "evenement_id": "EVT-QC-011",
              "message": "Une pénurie de main-d’œuvre généralisée fragilise autant les services publics que le secteur privé."
            }
          }
        ]
      },
      {
        "id": "EVT-QC-012",
        "nom": "Crise de verglas prolongée",
        "type": "evenement",
        "commandes": [
          { "op": "axes.delta", "axe": "environnement", "delta": -2 },
          { "op": "axes.delta", "axe": "social", "delta": -2 },
          { "op": "eco.delta_depenses", "postes": { "urgence": 2 } },
          { "op": "opposition.capital.delta", "delta": 2 },
          {
            "op": "journal",
            "payload": {
              "evenement_id": "EVT-QC-012",
              "message": "Un épisode de verglas prolongé provoque de longues pannes d’électricité et des évacuations."
            }
          }
        ]
      },
      {
        "id": "EVT-QC-013",
        "nom": "Enquête journalistique majeure",
        "type": "evenement",
        "commandes": [
          { "op": "axes.delta", "axe": "institutionnel", "delta": -3 },
          { "op": "opposition.capital.delta", "delta": 4 },
          { "op": "cabinet.capital.delta", "delta": -1 },
          {
            "op": "journal",
            "payload": {
              "evenement_id": "EVT-QC-013",
              "message": "Une enquête journalistique majeure met en cause un proche du cabinet."
            }
          }
        ]
      },
      {
        "id": "EVT-QC-014",
        "nom": "Débat linguistique inflammatoire",
        "type": "evenement",
        "commandes": [
          { "op": "axes.delta", "axe": "social", "delta": -2 },
          { "op": "axes.delta", "axe": "institutionnel", "delta": -1 },
          { "op": "opposition.capital.delta", "delta": 2 },
          {
            "op": "journal",
            "payload": {
              "evenement_id": "EVT-QC-014",
              "message": "Un débat linguistique hautement médiatisé polarise la population."
            }
          }
        ]
      },
      {
        "id": "EVT-QC-015",
        "nom": "Montée de la désinformation",
        "type": "evenement",
        "commandes": [
          { "op": "axes.delta", "axe": "institutionnel", "delta": -2 },
          { "op": "axes.delta", "axe": "social", "delta": -1 },
          { "op": "opposition.capital.delta", "delta": 3 },
          {
            "op": "journal",
            "payload": {
              "evenement_id": "EVT-QC-015",
              "message": "La montée de la désinformation sur les réseaux sociaux fragilise la confiance envers les institutions."
            }
          }
        ]
      },
      {
        "id": "EVT-QC-016",
        "nom": "Conflit nordique sur des terres autochtones",
        "type": "evenement",
        "commandes": [
          { "op": "axes.delta", "axe": "institutionnel", "delta": -2 },
          { "op": "axes.delta", "axe": "environnement", "delta": -1 },
          { "op": "opposition.capital.delta", "delta": 2 },
          {
            "op": "journal",
            "payload": {
              "evenement_id": "EVT-QC-016",
              "message": "Un conflit sur des terres autochtones au Nord requiert une médiation délicate."
            }
          }
        ]
      },
      {
        "id": "EVT-QC-017",
        "nom": "Boom de l’industrie des batteries",
        "type": "evenement",
        "commandes": [
          { "op": "axes.delta", "axe": "economique", "delta": 3 },
          { "op": "axes.delta", "axe": "institutionnel", "delta": 1 },
          { "op": "axes.delta", "axe": "environnement", "delta": -1 },
          { "op": "eco.delta_recettes", "bases": { "base_ent": 2 } },
          { "op": "opposition.capital.delta", "delta": -1 },
          {
            "op": "journal",
            "payload": {
              "evenement_id": "EVT-QC-017",
              "message": "Un boom de l’industrie des batteries attire des investissements massifs au Québec."
            }
          }
        ]
      },
      {
        "id": "EVT-QC-018",
        "nom": "Faillite d’un grand détaillant canadien",
        "type": "evenement",
        "commandes": [
          { "op": "axes.delta", "axe": "economique", "delta": -2 },
          { "op": "axes.delta", "axe": "social", "delta": -1 },
          { "op": "opposition.capital.delta", "delta": 1 },
          {
            "op": "journal",
            "payload": {
              "evenement_id": "EVT-QC-018",
              "message": "La faillite d’un grand détaillant canadien laisse des milliers de travailleurs dans l’incertitude."
            }
          }
        ]
      },
      {
        "id": "EVT-QC-019",
        "nom": "Négociations difficiles avec Ottawa",
        "type": "evenement",
        "commandes": [
          { "op": "axes.delta", "axe": "institutionnel", "delta": -2 },
          { "op": "axes.delta", "axe": "economique", "delta": -1 },
          { "op": "opposition.capital.delta", "delta": 2 },
          {
            "op": "journal",
            "payload": {
              "evenement_id": "EVT-QC-019",
              "message": "Des négociations tendues avec Ottawa sur le financement ravivent les tensions intergouvernementales."
            }
          }
        ]
      },
      {
        "id": "EVT-QC-020",
        "nom": "Poursuite environnementale historique",
        "type": "evenement",
        "commandes": [
          { "op": "axes.delta", "axe": "environnement", "delta": 2 },
          { "op": "axes.delta", "axe": "economique", "delta": -1 },
          { "op": "opposition.capital.delta", "delta": 1 },
          {
            "op": "journal",
            "payload": {
              "evenement_id": "EVT-QC-020",
              "message": "Une poursuite environnementale historique force l’État à revoir ses engagements."
            }
          }
        ]
      },
      {
        "id": "EVT-QC-021",
        "nom": "Mobilisation étudiante et cégeps politisés",
        "type": "evenement",
        "commandes": [
          { "op": "axes.delta", "axe": "social", "delta": -2 },
          { "op": "axes.delta", "axe": "institutionnel", "delta": -1 },
          { "op": "opposition.capital.delta", "delta": 2 },
          {
            "op": "journal",
            "payload": {
              "evenement_id": "EVT-QC-021",
              "message": "Une vague de mobilisation étudiante politise les campus et relance le débat social."
            }
          }
        ]
      },
      {
        "id": "EVT-QC-022",
        "nom": "Crise de cyber-sécurité gouvernementale",
        "type": "evenement",
        "commandes": [
          { "op": "axes.delta", "axe": "institutionnel", "delta": -3 },
          { "op": "eco.delta_depenses", "postes": { "numerique": 2 } },
          { "op": "opposition.capital.delta", "delta": 3 },
          {
            "op": "journal",
            "payload": {
              "evenement_id": "EVT-QC-022",
              "message": "Une fuite de données sensibles révèle de graves lacunes en cyber-sécurité."
            }
          }
        ]
      },
      {
        "id": "EVT-QC-023",
        "nom": "Surplus budgétaire inattendu",
        "type": "evenement",
        "commandes": [
          { "op": "eco.delta_dette", "montant": -1 },
          { "op": "axes.delta", "axe": "institutionnel", "delta": 1 },
          { "op": "cabinet.capital.delta", "delta": 1 },
          {
            "op": "journal",
            "payload": {
              "evenement_id": "EVT-QC-023",
              "message": "Des revenus supérieurs aux prévisions génèrent un surplus budgétaire inattendu."
            }
          }
        ]
      },
      {
        "id": "EVT-QC-024",
        "nom": "Convention autochtone historique",
        "type": "evenement",
        "commandes": [
          { "op": "axes.delta", "axe": "institutionnel", "delta": 2 },
          { "op": "axes.delta", "axe": "environnement", "delta": 1 },
          { "op": "axes.delta", "axe": "social", "delta": 1 },
          { "op": "opposition.capital.delta", "delta": -1 },
          {
            "op": "journal",
            "payload": {
              "evenement_id": "EVT-QC-024",
              "message": "La signature d’une convention autochtone historique apaise des tensions de longue date."
            }
          }
        ]
      },
      {
        "id": "EVT-QC-025",
        "nom": "Immense feu de forêt",
        "type": "evenement",
        "commandes": [
          { "op": "axes.delta", "axe": "environnement", "delta": -4 },
          { "op": "axes.delta", "axe": "social", "delta": -1 },
          { "op": "eco.delta_depenses", "postes": { "urgence": 3 } },
          { "op": "opposition.capital.delta", "delta": 2 },
          {
            "op": "journal",
            "payload": {
              "evenement_id": "EVT-QC-025",
              "message": "Un immense feu de forêt force l’évacuation de communautés entières."
            }
          }
        ]
      },
      {
        "id": "EVT-QC-026",
        "nom": "Offensive diplomatique canadienne",
        "type": "evenement",
        "commandes": [
          { "op": "axes.delta", "axe": "institutionnel", "delta": 1 },
          { "op": "axes.delta", "axe": "economique", "delta": 1 },
          { "op": "cabinet.capital.delta", "delta": 1 },
          { "op": "opposition.capital.delta", "delta": -1 },
          {
            "op": "journal",
            "payload": {
              "evenement_id": "EVT-QC-026",
              "message": "Une offensive diplomatique canadienne couronnée de succès rehausse le prestige international."
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

