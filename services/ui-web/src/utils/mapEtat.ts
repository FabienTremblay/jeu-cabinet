// src/utils/mapEtat.ts
import type { 
  EtatPartieVue,
  CarteDansMain,
  CarteEngagee,
  JoueursEtat,
  JoueurEtat,
  EntreePalmares,
} from "../types/game";

type CarteDef = {
  id: string;
  nom?: string;
  type?: string;
  cout_attention?: number;
  cout_cp?: number;
  commandes?: any[];
};

type ResumeDetails = {
  resume: string;
  details: string[];
};

/* -------------------------------------------------------------------------- */
/*  Normalisation des champs de capital                                       */
/* -------------------------------------------------------------------------- */

function normaliserCapital(value: unknown): number {
  // cas simple : déjà un nombre
  if (typeof value === "number") {
    return value;
  }

  if (value && typeof value === "object") {
    const v = value as any;
    if (typeof v.capital_politique === "number") {
      return v.capital_politique;
    }
    if (typeof v.valeur === "number") {
      return v.valeur;
    }
  }

  // fallback safe
  return 0;
}

/* -------------------------------------------------------------------------- */
/*  Helpers pour les cartes                                                   */
/* -------------------------------------------------------------------------- */
// 🔧 Définitions d'événements (cartes d'événement) : selon la structure réelle du noyau
function extraireDefsEvenements(etat: any): any[] {
  const cfg = etat?.regles?.config;

  // 1) chemin canonique (celui de ton état)
  if (Array.isArray(cfg?.events)) return cfg.events;

  // 2) variantes possibles (au cas où certains skins bougent la structure)
  if (Array.isArray(cfg?.evenements)) return cfg.evenements;
  if (Array.isArray(etat?.events)) return etat.events;

  // 3) "etat.evenements" existe chez toi mais semble être la liste "tirée" (souvent vide) → pas ce qu'on veut
  return [];
}

function construireResumeEtDetails(def: CarteDef): ResumeDetails {
  const lignes: string[] = [];

  // dictionnaire de renommage pour les op NON-axes
  const RENOMMAGES_OP: Record<string, string> = {
    // opposition.capital.delta → opposition
    "opposition.capital": "opposition",
    "journal" : " ",
    "eco.delta_recette" : "impôts",
    "eco.delta_depenses" : "budget",
    "eco.delta_dette" : "dette",
    "eco.set_taux_interet" : "taux directeur",
    // joueur.attention.delta → attention
    "joueur.attention": "attention",

    // joueur.vote_poids.delta → vote_poids
    "joueur.vote_poids": "vote_poids",

    // joueur.capital.delta → capital_personnel
    "joueur.capital": "capital_personnel",

    // capital_collectif.delta → capital_cabinet
    "capital_collectif": "capital_cabinet",
  };

  function nomNormaliseCommande(rawOp: string, cmd: any): string {
    // 1) Cas spécial : axes → on affiche directement l’axe ("social", "economique", ...)
    if (rawOp.startsWith("axes") && typeof cmd?.axe === "string") {
      return cmd.axe; // ex. "social"
    }

    const parts = rawOp.split(".");
    const key2 = parts.slice(0, 2).join("."); // ex. "joueur.attention"
    const key1 = parts[0];                    // ex. "joueur" ou "capital_collectif"

    // 2) Renommages spécifiques (plus précis d’abord)
    if (RENOMMAGES_OP[key2]) return RENOMMAGES_OP[key2];
    if (RENOMMAGES_OP[key1]) return RENOMMAGES_OP[key1];

    // 3) Fall-back : on garde juste le préfixe avant le premier point
    //    ex. "recettes.base_part.delta" → "recettes"
    return key1 || rawOp;
  }

  if (Array.isArray(def.commandes) && def.commandes.length > 0) {
    const ops = def.commandes.map((cmd: any) => {
      const rawOp = typeof cmd.op === "string" ? cmd.op : "??";
      const nom = nomNormaliseCommande(rawOp, cmd);

      // Ajout du delta (+n / -n) s’il est présent
      let valeur: string | null = null;
      if (typeof cmd.delta === "number") {
        valeur = cmd.delta >= 0 ? `+${cmd.delta}` : `${cmd.delta}`;
      }

      return valeur ? `${nom} (${valeur})` : nom;
    });

    // --- Traduction "famille" des rafales d'événements (ex: "evt, evt, evt, ...") ---
    const evtCount = ops.filter((o) => String(o).toLowerCase() === "evt").length;

    // Cas ciblé : "Démission fracassante" (REL-005) -> narratif clair
    const estDemissionFracassante =
      def.id === "REL-005" ||
      String(def.nom ?? "").toLowerCase().includes("démission fracassante");

    if (estDemissionFracassante && evtCount >= 2) {
      lignes.push(
        "Une démission fracassante déclenche plusieurs événements imprévus, hors du contrôle du cabinet."
      );
    } else if (evtCount >= 2) {
      // Règle générale (si tu as d'autres cartes chaotiques)
      lignes.push("Déclenche plusieurs événements imprévus, hors du contrôle direct du cabinet.");
    } else {
    const evtCount = ops.filter((o) => String(o).toLowerCase() === "evt").length;
    const estDemissionFracassante =
      def.id === "REL-005" ||
      String(def.nom ?? "").toLowerCase().includes("démission fracassante");

    if (estDemissionFracassante && evtCount >= 2) {
      lignes.push(
        "Une démission fracassante déclenche plusieurs événements imprévus, hors du contrôle du cabinet."
      );
    } else if (evtCount >= 2) {
      lignes.push("Déclenche plusieurs événements imprévus, hors du contrôle direct du cabinet.");
    } else {
      lignes.push(ops.join(", "));
    }
    }
  }

  return {
    resume: lignes[0] ?? def.nom ?? def.id,
    details: lignes,
  };
}

function signed(n: number | undefined): string {
  if (typeof n !== "number" || isNaN(n)) return "";
  return n > 0 ? `+${n}` : `${n}`;
}

function commandeToFragment(cmd: any): string {
  switch (cmd.op) {
    case "axes.delta":
      return `${cmd.axe} ${signed(cmd.delta)}`;

    case "axes.poids.delta":
      return `poids ${cmd.axe} ${signed(cmd.delta)}`;

    case "capital_collectif.delta":
      return `capital collectif ${signed(cmd.delta)}`;

    case "depenses.delta":
      return `dépenses ${cmd.poste} ${signed(cmd.delta)}`;

    case "recettes.base_part.delta":
      return `recettes base_part ${signed(cmd.delta)}`;

    case "recettes.base_ent.delta":
      return `recettes base_ent ${signed(cmd.delta)}`;

    case "dette.delta":
      return `dette ${signed(cmd.delta)}`;

    case "joueur.capital.delta":
      return `capital joueur ${signed(cmd.delta)}`;

    default:
      return cmd.op ?? "";
  }
}

/** Construit un résumé lisible pour une carte (non utilisé directement mais conservé) */
function buildCarteResume(def: any): string {
  if (!def) return "";

  const lignes: string[] = [];

  if (def.type) lignes.push(`type : ${def.type}`);
  if (typeof def.cout_attention === "number") {
    lignes.push(`coût d’attention : ${def.cout_attention}`);
  }
  if (typeof def.cout_cp === "number") {
    lignes.push(`coût politique : ${def.cout_cp}`);
  }

  const effets = (def.commandes ?? [])
    .map(commandeToFragment)
    .filter((x: string) => x.length > 0);

  if (effets.length > 0) {
    lignes.push(effets.join("; "));
  }

  return lignes.join("\n");
}

/** Détail ligne-par-ligne pour affichage secondaire (non utilisé directement mais conservé) */
function buildCarteDetails(def: any): string[] {
  if (!def) return [];

  const effets = (def.commandes ?? [])
    .map(commandeToFragment)
    .filter((x: string) => x.length > 0);

  return effets;
}

/* -------------------------------------------------------------------------- */
/*             Fonction principale : transforme l'état vers la vue            */
/* -------------------------------------------------------------------------- */

export function mapEtatToGameState(
  repEtat: any,
  joueurIdCourant: string
): EtatPartieVue {
  const etat = repEtat?.etat ?? {};

  /* --------------------------- Joueurs ------------------------------------- */

  const joueursBruts = etat.joueurs ?? {};
  const joueurs: JoueursEtat = {};

  for (const [id, j] of Object.entries(joueursBruts)) {
    const brut = j as any;

    const joueurProj: JoueurEtat & { main_codes?: string[] } = {
      id: brut.id ?? id,
      alias:
        brut.alias ??
        brut.nom ??
        brut.donnees_skin?.alias ??
        id,
      capital_politique: normaliserCapital(brut.capital_politique),

      attention_max:
        typeof brut.attention_max === "number"
          ? brut.attention_max
          : undefined,
      attention_dispo:
        typeof brut.attention_dispo === "number"
          ? brut.attention_dispo
          : undefined,
      poids_vote:
        typeof brut.poids_vote === "number"
          ? brut.poids_vote
          : undefined,
      peut_voter:
        typeof brut.peut_voter === "boolean"
          ? brut.peut_voter
          : undefined,

      role: brut.role ?? brut.donnees_skin?.role ?? undefined,
      pret: brut.pret ?? brut.donnees_skin?.pret ?? undefined,

      // on garde la main de façon normalisée (codes de cartes uniquement)
      main_codes: Array.isArray(brut.main) ? [...brut.main] : [],
    };

    joueurs[id] = joueurProj;
  }

  const joueurActif = joueurs[joueurIdCourant] as
    | (JoueurEtat & { main_codes?: string[] })
    | undefined;

  const cartes_def: Record<string, CarteDef> = etat.cartes_def ?? {};

  /* --------------------------- Attention joueur courant -------------------- */

  const attention_disponible: number | null =
    typeof joueurActif?.attention_dispo === "number"
      ? joueurActif.attention_dispo!
      : null;

  const attention_max: number | null =
    typeof joueurActif?.attention_max === "number"
      ? joueurActif.attention_max!
      : null;

  /* --------------------------- Main du joueur courant ---------------------- */

  const mainCodes: string[] = joueurActif?.main_codes ?? [];

  const main_joueur_courant: CarteDansMain[] = mainCodes.map(
    (code: string) => {
      const def = cartes_def?.[code];

      if (!def) {
        return {
          id: code,
          nom: code,
          type: "inconnu",
          resume: "(définition de carte introuvable)",
          cout_attention: 0,
          cout_cp: 0,
          details: [],
        };
      }

      const { resume, details } = construireResumeEtDetails(def);

      return {
        id: code,
        nom: def.nom ?? code,
        type: def.type ?? "inconnu",
        resume,
        cout_attention: def.cout_attention ?? 0,
        cout_cp: def.cout_cp ?? 0,
        details,
      };
    }
  );

  /* --------------------------- Programme cabinet --------------------------- */

  const programme_cabinet: CarteEngagee[] =
    Array.isArray((etat as any).programme?.entrees)
      ? (etat as any).programme.entrees.map((entree: any) => {
          // On tolère plusieurs conventions possibles, mais on privilégie carte_id
          const idCarte =
            entree.carte_id ??
            entree.carte ??
            (typeof entree === "string" ? entree : entree.id);

          const def = cartes_def?.[idCarte];

          if (!def) {
            return {
              uid: entree.uid ?? undefined,
              auteur_id: entree.auteur_id ?? entree.auteur ?? undefined,
              attention_engagee: entree.attention_engagee ?? entree.attention ?? undefined,
              id: idCarte,
              nom: idCarte,
              type: "inconnu",
              resume: "(définition de carte introuvable)",
              cout_attention: 0,
              cout_cp: 0,
              details: [],
            };
          }
          const { resume, details } = construireResumeEtDetails(def);
          return {
              uid: entree.uid ?? undefined,
              auteur_id: entree.auteur_id ?? entree.auteur ?? undefined,
              attention_engagee: entree.attention_engagee ?? entree.attention ?? undefined,
              id: idCarte,
            nom: def.nom ?? idCarte,
            type: def.type ?? "inconnu",
            resume: resume ?? "",
            cout_attention: def.cout_attention ?? 0,
            cout_cp: def.cout_cp ?? 0,
            details: details ?? [],
          };
        })
      : [];

  // Votes et verdict du programme (si la phase y est rendue)
  const programme_votes: Record<string, number> =
    ((etat as any).programme?.votes as Record<string, number>) ?? {};
  const programme_verdict: boolean | null =
    typeof (etat as any).programme?.verdict === "boolean"
      ? (etat as any).programme.verdict
      : null;

  /* --------------------------- Indicateurs globaux ------------------------- */

  const axesBruts = etat.axes ?? {};
  const axesProj: Record<string, number> = {};

  for (const [id, axe] of Object.entries(axesBruts)) {
    const v = (axe as any)?.valeur;
    axesProj[id] = typeof v === "number" ? v : 0;
  }

  const indicateurs = {
    // ici on normalise aussi pour éviter l’objet {capital_politique, donnees_skin}
    capital_collectif: normaliserCapital(etat.capital_collectif),
    opposition: normaliserCapital(etat.opposition),
    axes: axesProj,
  };

  /* --------------------------- Fin de partie / palmarès -------------------- */

  const termine: boolean = Boolean(etat.termine);
  const raison_fin: string | null =
    typeof etat.raison_fin === "string" ? etat.raison_fin : null;

  let palmares: EntreePalmares[] | undefined = undefined;

  if (Array.isArray((etat as any).palmares)) {
    // On fait confiance au backend mais on normalise légèrement
    const palBrut = (etat as any).palmares as any[];
    palmares = palBrut.map((p, index) => {
      const joueurId: string =
        p.joueur_id ?? p.id ?? p.joueur ?? `J${index + 1}`;
      const joueurRef = joueurs[joueurId];

      const alias: string =
        p.alias ??
        p.joueur_alias ??
        joueurRef?.alias ??
        joueurId;

      const score: number =
        typeof p.score_total === "number"
          ? p.score_total
          : typeof p.points === "number"
          ? p.points
          : typeof joueurRef?.capital_politique === "number"
          ? joueurRef.capital_politique
          : 0;

      const rang: number =
        typeof p.rang === "number" ? p.rang : index + 1;

      const scores_axes: Record<string, number> | undefined =
        typeof p.scores_axes === "object" && p.scores_axes !== null
          ? (p.scores_axes as Record<string, number>)
          : undefined;

      return {
        joueur_id: joueurId,
        alias,
        score_total: score,
        rang,
        scores_axes,
      };
    });
  } else if (termine) {
    // Si la partie est terminée mais aucun palmarès explicite,
    // on le calcule à partir des joueurs (tri sur capital_politique).
    const entries: EntreePalmares[] = Object.values(joueurs).map((j) => {
      const score =
        typeof j.capital_politique === "number"
          ? j.capital_politique
          : 0;

      return {
        joueur_id: j.id,
        alias: j.alias,
        score_total: score,
        rang: 0, // rang calculé plus bas
      };
    });

    // Tri décroissant sur score_total
    entries.sort((a, b) => b.score_total - a.score_total);

    // Attribution des rangs (ex aequo gardent le même rang)
    let lastScore: number | null = null;
    let currentRank = 0;

    entries.forEach((e, index) => {
      if (lastScore === null || e.score_total < lastScore) {
        currentRank = index + 1;
        lastScore = e.score_total;
      }
      e.rang = currentRank;
    });

    palmares = entries;
  }
  
  const evenements = extraireDefsEvenements(etat);

  /* --------------------------- Vue finale ---------------------------------- */

  // eco/budget : on copie si présent, sans imposer une structure trop rigide
  const eco = (() => {
    const e = (etat as any)?.eco;
    if (!e || typeof e !== "object") return null;
    const recettes = (e as any).recettes;
    const depenses = (e as any).depenses;
    const dette = typeof (e as any).dette === "number" ? (e as any).dette : null;
    const taux_interet =
      typeof (e as any).taux_interet === "number" ? (e as any).taux_interet :
      typeof (e as any).taux_interet_annuel === "number" ? (e as any).taux_interet_annuel :
      typeof (e as any).taux_interet_directeur === "number" ? (e as any).taux_interet_directeur :
      typeof (e as any).taux_interet_gouv === "number" ? (e as any).taux_interet_gouv :
      typeof (e as any).taux_interet === "number" ? (e as any).taux_interet : null;
    return {
      recettes: (recettes && typeof recettes === "object") ? recettes : undefined,
      depenses: (depenses && typeof depenses === "object") ? depenses : undefined,
      dette,
      taux_interet,
    };
  })();

  const vue: EtatPartieVue = {
    partie_id: repEtat.partie_id ?? etat.partie_id ?? "",
    tour: etat.tour ?? null,
    phase: etat.phase ?? "",
    sous_phase: etat.sous_phase ?? "",

    termine,
    raison_fin,
    palmares,

    joueurs,
    indicateurs,
    programme_cabinet,
    programme_votes,
    programme_verdict,
    main_joueur_courant,
    journal: etat.historiques ?? [],
    attente: etat.attente ?? null,
    attention_disponible,
    attention_max,
    evenements,
    eco,
  };



  return vue;
}

