// src/pages/GamePage.tsx
import React, { useEffect, useRef, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";

import { useSession } from "../context/SessionContext";
import { useEtatPartie } from "../hooks/useEtatPartie";
import { useSituationPolling } from "../hooks/useSituationPolling";
import { useJournalRecentPolling } from "../hooks/useJournalRecentPolling";
import { idCourt } from "../utils/idCourt";

import Loading from "../components/shared/Loading";

import PlayerStatusPanel from "../components/game/PlayerStatusPanel";
import ProgrammeView from "../components/game/ProgrammeView";
import HandView, { JouerCarteParams } from "../components/game/HandView";
import JournalView from "../components/game/JournalView";
import { ActionsPanel } from "../components/game/ActionsPanel";
import { jouerCarteDirectement, soumettreAction } from "../api/moteurApi";
import GameLayout from "../components/layout/GameLayout";
import FlashUneModal, { FlashUneArticle } from "../components/game/FlashUneModal";

import FinPartiePage from "./FinPartiePage";

function signed(n: number): string {
  return n > 0 ? `+${n}` : `${n}`;
}

function clampSegments(parts: string[], max: number): string {
  if (parts.length <= max) return parts.join(" · ");
  return parts.slice(0, max).join(" · ") + " · …";
}

function resumerImpactsDepuisCommandes(commandes: any[] | undefined): string | null {
  if (!Array.isArray(commandes) || commandes.length === 0) return null;

  const axes: Record<string, number> = {};
  const depenses: Record<string, number> = {};
  const recettes: Record<string, number> = {};
  let dette = 0;

  let cabinet = 0;
  let oppo = 0;
  const oppoData: Record<string, number> = {};

  for (const c of commandes) {
    if (!c || typeof c.op !== "string") continue;
    if (c.op === "journal") continue;

    if (c.op === "axes.delta" && typeof c.axe === "string" && typeof c.delta === "number") {
      axes[c.axe] = (axes[c.axe] ?? 0) + c.delta;
    }

    if (c.op === "eco.delta_depenses" && c.postes && typeof c.postes === "object") {
      for (const [poste, d] of Object.entries(c.postes)) {
        if (typeof d === "number") depenses[poste] = (depenses[poste] ?? 0) + d;
      }
    }

    if (c.op === "eco.delta_recettes" && c.bases && typeof c.bases === "object") {
      for (const [base, d] of Object.entries(c.bases)) {
        if (typeof d === "number") recettes[base] = (recettes[base] ?? 0) + d;
      }
    }

    if (c.op === "eco.delta_dette" && typeof c.delta === "number") {
      dette += c.delta;
    }

    if (c.op === "capital_collectif.delta" && typeof c.delta === "number") {
      cabinet += c.delta;
    }

    if (c.op === "opposition.capital.delta" && typeof c.delta === "number") {
      oppo += c.delta;
    }

    if (
      c.op === "opposition.data.delta" &&
      typeof c.cle === "string" &&
      typeof c.delta === "number"
    ) {
      oppoData[c.cle] = (oppoData[c.cle] ?? 0) + c.delta;
    }
  }

  const parts: string[] = [];

  // signal politique d'abord
  if (cabinet !== 0) parts.push(`cabinet ${signed(cabinet)}`);
  if (oppo !== 0) parts.push(`opposition ${signed(oppo)}`);

  // axes (on garde les plus marqués)
  const axesParts = Object.entries(axes)
    .filter(([, v]) => v !== 0)
    .sort((a, b) => Math.abs(b[1]) - Math.abs(a[1]))
    .map(([k, v]) => `${k} ${signed(v)}`);
  if (axesParts.length) parts.push(clampSegments(axesParts, 2));

  // éco compact
  const ecoParts: string[] = [];
  const dep = Object.entries(depenses).filter(([, v]) => v !== 0);
  const rec = Object.entries(recettes).filter(([, v]) => v !== 0);

  if (rec.length) {
    const total = rec.reduce((s, [, v]) => s + v, 0);
    ecoParts.push(`recettes ${signed(total)}`);
  }
  if (dep.length) {
    const total = dep.reduce((s, [, v]) => s + v, 0);
    ecoParts.push(`dépenses ${signed(total)}`);
  }
  if (dette !== 0) ecoParts.push(`dette ${signed(dette)}`);

  if (ecoParts.length) parts.push(clampSegments(ecoParts, 2));

  // opposition data (optionnel, si tu veux)
  const od = Object.entries(oppoData).filter(([, v]) => v !== 0);
  if (od.length) {
    const top = od
      .sort((a, b) => Math.abs(b[1]) - Math.abs(a[1]))
      .slice(0, 1)
      .map(([k, v]) => `${k} ${signed(v)}`)
      .join(", ");
    parts.push(`opposition : ${top}`);
  }

  return parts.length ? clampSegments(parts, 3) : null;
}

function determinerBadge(commandes: any[] | undefined): string | null {
  if (!Array.isArray(commandes)) return null;

  // axe dominant
  const axes: Record<string, number> = {};
  let cabinet = 0, oppo = 0;
  let eco = 0;

  for (const c of commandes) {
    if (!c || typeof c.op !== "string") continue;
    if (c.op === "axes.delta" && typeof c.axe === "string" && typeof c.delta === "number") {
      axes[c.axe] = (axes[c.axe] ?? 0) + c.delta;
    }
    if (c.op === "capital_collectif.delta" && typeof c.delta === "number") cabinet += c.delta;
    if (c.op === "opposition.capital.delta" && typeof c.delta === "number") oppo += c.delta;

    if (c.op === "eco.delta_recettes" || c.op === "eco.delta_depenses" || c.op === "eco.delta_dette") {
      eco += 1;
    }
  }

  const axesSorted = Object.entries(axes)
    .sort((a, b) => Math.abs(b[1]) - Math.abs(a[1]));
  if (axesSorted.length && Math.abs(axesSorted[0][1]) > 0) return axesSorted[0][0];

  if (cabinet !== 0 || oppo !== 0) return "politique";
  if (eco > 0) return "économie";

  return "actualité";
}

function titreDepuisChapo(chapo: string): string | null {
  const s = (chapo ?? "").trim();
  if (!s) return null;

  // prend jusqu'au premier point (ou limite)
  const idx = s.indexOf(".");
  const base = (idx > 12 ? s.slice(0, idx) : s).trim();

  // raccourci si trop long
  const max = 54;
  const t = base.length > max ? base.slice(0, max - 1).trim() + "…" : base;

  // mini “dynamisation”
  // ex: "Une innovation technologique stimulante dynamise l’économie"
  // -> "Innovation tech : l’économie accélère"
  // (simple, sans NLP lourd)
  if (t.toLowerCase().startsWith("une ")) return t.slice(4);
  if (t.toLowerCase().startsWith("des ")) return t.slice(4);
  if (t.toLowerCase().startsWith("grèves")) return "Grèves : le pays ralentit";
  return t;
}

function lireNomTablePourPartie(partieId?: string | null): string | null {
  if (!partieId) return null;
  try {
    const v = localStorage.getItem(`cab.partie.nom_table:${partieId}`);
    const s = (v ?? "").trim();
    return s ? s : null;
  } catch {
    return null;
  }
}

const GamePage: React.FC = () => {
  const { partieId } = useParams<{ partieId: string }>();
  const { joueur } = useSession();
  const navigate = useNavigate();

  useEffect(() => {
    if (!joueur) {
      navigate("/auth");
    }
  }, [joueur, navigate]);

  const [layoutMode, setLayoutMode] = useState<"auto" | "desktop" | "mobile">(
    "auto"
  );

  const [sidePanelOpen, setSidePanelOpen] = useState(false);

  const {
    etat: etatVue,
    loading,
    erreur,
    forceRefresh,
  } = useEtatPartie(partieId, joueur?.id_joueur);

  const { ancrage } = useSituationPolling(joueur?.id_joueur, {
    intervalMs: 2000,
  });

  const { journalRecent } = useJournalRecentPolling(joueur?.id_joueur, {
    intervalMs: 2000,
  });

  // --- Mini ToastHost (warn/error) ---
  type Toast = { id: string; severity: "warn" | "error"; title?: string; message: string };
  const [toasts, setToasts] = useState<Toast[]>([]);
  const seenToastIds = useRef<Set<string>>(new Set());
  const [mobileTab, setMobileTab] = useState<"etat"|"programme"|"actions"|"journal">("programme");
 
  // Carte sélectionnée : permet de passer de Programme -> Actions en montrant le détail.
  const [carteSelectionneeId, setCarteSelectionneeId] = useState<string | null>(null);

  useEffect(() => {
    if (!Array.isArray(journalRecent)) return;
    const incoming = journalRecent
      .filter((e) => (e.severity === "warn" || e.severity === "error") && !!e.event_id)
      .filter((e) => !seenToastIds.current.has(e.event_id))
      .slice(0, 3);

    if (incoming.length === 0) return;

    for (const e of incoming) seenToastIds.current.add(e.event_id);
    const newToasts: Toast[] = incoming.map((e) => ({
      id: e.event_id,
      severity: e.severity as "warn" | "error",
      title: e.category ?? "Système",
      message: e.message,
    }));

    setToasts((prev) => [...newToasts, ...prev].slice(0, 3));
    for (const t of newToasts) {
      window.setTimeout(() => setToasts((prev) => prev.filter((x) => x.id !== t.id)), 6000);
    }
  }, [journalRecent]);

  // 🔹 NOUVEAUX HOOKS ET ACTEUR ICI (toujours appelés, avant tout return)

  // --- FLASH (push médiatique) : queue + dédup ---
  const [flashOuvert, setFlashOuvert] = useState(false);
  const [flashQueue, setFlashQueue] = useState<FlashUneArticle[]>([]);
  const seenFlashKeys = useRef<Set<string>>(new Set());

  const storageKeyFlashLu = partieId && joueur
    ? `cab.flash.lu:${joueur.id_joueur}:${partieId}`
    : null;

  // IMPORTANT : éviter toute contamination/persistance entre parties
  // React Router peut réutiliser GamePage avec un nouveau param (partieId) sans unmount complet.
  useEffect(() => {
    // on ferme/vidange l'état UI de la flash
    setFlashOuvert(false);
    setFlashQueue([]);

    // on reset la dédup en mémoire (sinon le Set grossit et peut créer des effets de bord)
    seenFlashKeys.current = new Set();
  }, [partieId, joueur?.id_joueur]);

  useEffect(() => {
    if (!etatVue || !partieId || !joueur) return;

    const tour = typeof etatVue.tour === "number" ? etatVue.tour : null;
    if (tour == null) return;

    // éviter de rejouer après refresh (F5)
    const dejaLu = storageKeyFlashLu ? Number(localStorage.getItem(storageKeyFlashLu) ?? "0") : 0;
    if (tour <= dejaLu) return;

    const hist = Array.isArray(etatVue.journal) ? etatVue.journal : [];
    const evenements = Array.isArray((etatVue as any).evenements) ? (etatVue as any).evenements : [];

    const mapEvt = new Map<string, any>();
    for (const e of evenements) {
      if (e && typeof e.id === "string") mapEvt.set(e.id, e);
    }

    // articles du tour : journal avec evenement_id
    const articlesBruts = hist
      .filter((h: any) => h && h.tour === tour && h.type === "journal" && typeof h.evenement_id === "string")
      .map((h: any) => {
        const evtId = String(h.evenement_id);
        const def = mapEvt.get(evtId);
        const chapo = typeof h.message === "string" ? h.message : "";

        const titreDef = (def && typeof def.nom === "string") ? def.nom : null;
        const titreFallback = titreDepuisChapo(chapo);
        const titre = titreDef ?? titreFallback ?? evtId;

        const commandes = def?.commandes;
        const impacts = resumerImpactsDepuisCommandes(commandes);
        const badge = determinerBadge(commandes);

        const key = `${partieId}:tour-${tour}:${evtId}`;

        const article: FlashUneArticle = {
          key,
          tour,
          evenement_id: evtId,
          titre,
          chapo,
          impacts,
          badge,
        };
        return article;
      });

    // rien à montrer → on marque le tour comme “lu” pour ne pas rechecker en boucle
    if (articlesBruts.length === 0) {
      if (storageKeyFlashLu) localStorage.setItem(storageKeyFlashLu, String(tour));
      return;
    }

    const nouveaux = articlesBruts.filter((a) => !seenFlashKeys.current.has(a.key));
    if (nouveaux.length === 0) return;

    nouveaux.forEach((a) => seenFlashKeys.current.add(a.key));

    setFlashQueue((prev) => {
      const merged = [...prev, ...nouveaux];
      return merged;
    });

    setFlashOuvert(true);
  }, [etatVue, partieId, joueur, storageKeyFlashLu]);


  const acteurId = joueur?.id_joueur ?? "";
  const [quitterEnCours, setQuitterEnCours] = useState(false);
  const [erreurQuitter, setErreurQuitter] = useState<string | null>(null);

  const [arreterEnCours, setArreterEnCours] = useState(false);
  const [erreurArreter, setErreurArreter] = useState<string | null>(null);

  type ItemMenu = {
    id: string;
    libelle: string;
    description?: string;
    danger?: boolean;
    disabled?: boolean;
    onClick: () => void | Promise<void>;
  };
  type SectionMenu = {
    id: string;
    titre: string;
    items: ItemMenu[];
  };

  const copierTexte = async (texte: string) => {
    try {
      await navigator.clipboard.writeText(texte);
    } catch {
      // fallback simple
      window.prompt("Copiez ce texte :", texte);
    }
  };

  const handleQuitterPartie = async () => {
    if (!partieId || !joueur) return;

    setQuitterEnCours(true);
    setErreurQuitter(null);

    try {
      await soumettreAction(partieId, {
        acteur: joueur.id_joueur,
        type_action: "partie.joueur_quitte_definitivement",
        donnees: {
          // joueur_id est de toute façon complété dans soumettreAction,
          // mais on le met pour que ce soit explicite
          joueur_id: joueur.id_joueur,
        },
      });

      // Ici on NE navigue PAS directement.
      // On attend que ui-etat ré-ancre le joueur sur le lobby.
      // useSituationPolling détectera ancrage.type === "lobby"
      // et fera navigate("/lobby").
    } catch (err: any) {
      console.error("Erreur lors de la demande de quitter la partie :", err);
      setErreurQuitter(
        "Impossible de quitter la partie pour le moment. Veuillez réessayer."
      );
    } finally {
      setQuitterEnCours(false);
    }
  };
 
  const handleArreterPartie = async () => {
    if (!partieId || !joueur) return;

    const defaut = "La partie a été arrêtée par l’hôte.";
    const saisie = window.prompt(
      "Raison (texte affiché aux joueurs) :",
      defaut
    );
    if (saisie === null) return; // annuler

    const raison = (saisie ?? "").trim();
    if (!raison) {
      alert("La raison ne peut pas être vide.");
      return;
    }

    const ok = window.confirm(
      "Confirmer l’arrêt de la partie ?\n\nCette action met fin à la partie et affichera les résultats à tous les joueurs."
    );
    if (!ok) return;

    setArreterEnCours(true);
    setErreurArreter(null);

    try {
      await soumettreAction(partieId, {
        acteur: joueur.id_joueur,
        type_action: "partie.terminer",
        donnees: { raison },
      });
      // pas de navigate : on laisse le moteur + projection faire basculer l’UI (fin_jeu)
    } catch (err: any) {
      console.error("Erreur lors de l'arrêt de la partie :", err);
      setErreurArreter("Impossible d’arrêter la partie pour le moment. Veuillez réessayer.");
    } finally {
      setArreterEnCours(false);
    }
  };


  const handlePlayCardImmediate = async (
    carteId: string,
    params?: JouerCarteParams
  ) => {
    if (!etatVue || !etatVue.partie_id || !acteurId) return;

    const partieIdCourante = etatVue.partie_id;

    try {
      await jouerCarteDirectement(partieIdCourante, acteurId, carteId, params);
      await forceRefresh();
    } catch (err) {
      console.error("Erreur lors de l'utilisation d'une carte :", err);
    }
  };

  // 🔹 useEffect ancrage APRÈS les hooks, c'est ok (c’est un hook lui aussi)
  useEffect(() => {
    if (!ancrage) return;
    if (ancrage.type === "lobby") {
      // toast possible ici
      navigate("/lobby");
    }
  }, [ancrage, navigate]);

  // 🔹 ENSUITE SEULEMENT : les return conditionnels

  if (!joueur || !partieId) {
    return <div className="p-4">Partie introuvable ou session expirée.</div>;
  }

  if (loading && !etatVue) {
    return <Loading label="Chargement de la partie…" />;
  }

  if (!etatVue) {
    return (
      <div className="p-4">
        <p className="text-red-400">
          Impossible de charger l’état de la partie.
        </p>
        {erreur && (
          <pre className="text-xs mt-2 whitespace-pre-wrap">{erreur}</pre>
        )}
      </div>
    );
  }

  // --- Données transversales nécessaires y compris pour fin de partie ---
  const joueursPanel = Object.entries(etatVue.joueurs ?? {}).map(
    ([id, j]: [string, any]) => ({
      id,
      alias: (j as any).alias ?? idCourt(id),
      role: (j as any).role,
      pret: (j as any).pret,
      capital_politique: (j as any).capital_politique,
      poids_vote: (j as any).poids_vote,
    })
  );

  const estHote = joueursPanel.some(
    (j) => j.id === acteurId && j.role === "hote"
  );

  const capitalCollectif = etatVue.indicateurs?.capital_collectif ?? 0;
  const capitalOpposition = etatVue.indicateurs?.opposition ?? 0;

  const estFinJeu =
    etatVue.phase === "fin_jeu" || etatVue.termine === true;

  if (estFinJeu) {
    return (
      <FinPartiePage
        palmares={etatVue.palmares}
        raison={etatVue.raison_fin}
        tour={etatVue.tour}
        capitalCollectif={capitalCollectif}
        capitalOpposition={capitalOpposition}
        joueurs={joueursPanel}
        joueurId={acteurId}
        onQuitterPartie={handleQuitterPartie}
        quitterEnCours={quitterEnCours}
        erreurQuitter={erreurQuitter}
      />
    );
  }
  
  const aliasParJoueur: Record<string, string> = Object.fromEntries(
    joueursPanel.map((j) => [j.id, j.alias ?? idCourt(j.id)])
  );

  const handleActionSent = (op: string) => {
    forceRefresh();

    const s = (op ?? "").toLowerCase();
    const doitAllerProgramme =
      s.includes("programme.") ||
      s.includes("vote") ||
      s.includes("voter") ||
      s.includes("confirmer") ||
      (s.includes("terminer") && s.includes("engagement"));

    if (doitAllerProgramme) setMobileTab("programme");
  };

  // --- Onglet mobile "Victoire" : badge "?" si en péril ou non assurée ---
  const victoireEnPeril = capitalCollectif <= 0 || capitalOpposition >= capitalCollectif;

  const victoireNonAssuree =
    !victoireEnPeril && (capitalCollectif <= 1 || capitalOpposition === capitalCollectif - 1);

  const actionsRestantes = typeof etatVue.attention_disponible === "number"
    ? etatVue.attention_disponible
    : null;

  const tabMeta = {
    etat: {
      label: "Victoire",
      badge: (victoireEnPeril || victoireNonAssuree) ? "?" : null,
      pulse: victoireEnPeril,
    },
    programme: {
      label: "À l’agenda",
    },
    actions: {
      label: `Actions (${actionsRestantes ?? "?"})`,
    },
    journal: {
      label: "Journal",
    },
  };
  const axes = (etatVue as any).axes ?? (etatVue as any).indicateurs?.axes ?? null;

  // budget : on agrège depuis eco.recettes/eco.depenses si elles sont ventilées
  const budget = (() => {
    const eco = (etatVue as any).eco ?? null;

    // Normalise les ventilations qui peuvent être:
    // - { poste: 123 }
    // - { poste: { nom: "...", valeur: 123, ... } }
    const normaliserVentilation = (raw: any): Record<string, number> | null => {
      if (!raw || typeof raw !== "object") return null;
      const out: Record<string, number> = {};
      for (const [k, v] of Object.entries(raw)) {
        if (typeof v === "number" && Number.isFinite(v)) {
          out[k] = v;
          continue;
        }
        if (v && typeof v === "object") {
          const vv = (v as any).valeur;
          if (typeof vv === "number" && Number.isFinite(vv)) {
            out[k] = vv;
            continue;
        }
        }
        // sinon on ignore (0 implicite)
      }
      return Object.keys(out).length ? out : null;
    };

    const sum = (r: Record<string, number> | null) =>
      r ? Object.values(r).reduce((s, v) => s + (Number.isFinite(v) ? v : 0), 0) : null;

    const recettes = normaliserVentilation(eco?.recettes);
    const depensesBrutes = normaliserVentilation(eco?.depenses);

    // Sépare les intérêts si jamais la ventilation des dépenses les contient déjà
    const isInteretKey = (k: string) => /interet/i.test(k) || /int[eé]r[eê]t/i.test(k);
    const depenses: Record<string, number> | null = depensesBrutes
      ? Object.fromEntries(Object.entries(depensesBrutes).filter(([k]) => !isInteretKey(k)))
      : null;

    const recettes_total =
      typeof eco?.recettes_total === "number"
        ? eco.recettes_total
        : sum(recettes);
    const depenses_total =
      typeof eco?.depenses_total === "number"
        ? eco.depenses_total
        : sum(depenses);

    const dette =
      typeof eco?.dette === "number"
        ? eco.dette
        : (typeof (etatVue as any).indicateurs?.dette === "number" ? (etatVue as any).indicateurs.dette : null);

    const taux_interet =
      typeof eco?.taux_interet === "number"
        ? eco.taux_interet
        : (typeof eco?.taux_interet_annuel === "number" ? eco.taux_interet_annuel : null);

    const interets =
      (typeof eco?.interets === "number" ? eco.interets : null) ??
      (typeof dette === "number" && typeof taux_interet === "number" ? dette * taux_interet : null);

    return { dette, recettes_total, depenses_total, interets, recettes, depenses, taux_interet };
  })();

  const attenteType = etatVue.attente?.type ?? null;
  const uiActionsRaw = etatVue.attente?.meta?.ui?.actions ?? [];

  const uiActions = uiActionsRaw.map((a: any) => ({
    op: a.op ?? a.payload?.op ?? a.code,            // <<< clé
    label: a.label,
    fields: a.fields ?? a.payload?.fields ?? [],
    // tu peux aussi recopier a.code / a.payload si tu en as besoin
  }));

  const actionsProgramme = uiActions.filter((a) => {
    const op = (a.op ?? "").toLowerCase();
    const label = (a.label ?? "").toLowerCase();

    const fields = Array.isArray(a.fields) ? a.fields : [];
    const hasCarteMain = fields.some((f: any) => f?.domain === "carte_main");
    const hasChoice = fields.some(
      (f: any) => typeof f?.domain === "string" && f.domain.startsWith("choice:")
    );

    return (
      hasCarteMain ||
      hasChoice ||
      op.includes("programme") ||
      op.includes("vote") ||
      label.includes("vote") ||
      label.includes("engagement") ||
      label.includes("engager") ||
      label.includes("terminer") ||
      label.includes("enregistrer") ||
      label.includes("confirmer")
    );
  });

  const actionsReste = uiActions.filter((a) => !actionsProgramme.includes(a));


  // --- BANDEAU "PROCHAINE ÉTAPE DU TOUR" (mobile-first) ---
  const prochaineEtape = (() => {
    const tour = etatVue.tour ?? "?";
    const phase = etatVue.phase ?? "?";
    const sous = etatVue.sous_phase ? ` / ${etatVue.sous_phase}` : "";

    // Cible par défaut : programme si on a des actions "de tour" / vote / engagement
    let cible: "programme" | "actions" | "journal" | "etat" = "programme";
    let titre = `Tour ${tour} · ${phase}${sous}`;
    let detail = "";

    // Priorité perturbations UNIQUEMENT hors PHASE_PROGRAMME
    if (
      String(etatVue.sous_phase).toUpperCase() === "PHASE_PERTURBATION_VOTE" &&
      String(etatVue.phase).toUpperCase() !== "PHASE_PROGRAMME"
    ) {
      cible = "actions";
      detail =
        "Perturbations : jouer une carte (si possible) ou indiquer qu’il n’y en a aucune.";
      return { titre, detail, cible };
    }

    // 1) Attente explicite
    if (attenteType) {
      const a = String(attenteType).toLowerCase();
      if (a.includes("programme") || a.includes("vote")) {
        cible = "programme";
        detail = "Étape en cours : programme / vote.";
      } else if (a.includes("action") || a.includes("carte") || a.includes("main")) {
        cible = "actions";
        detail = "Étape en cours : jouer une carte / action.";
      } else {
        // inconnu → on privilégie programme si dispo sinon actions
        cible = actionsProgramme.length > 0 ? "programme" : (actionsReste.length > 0 ? "actions" : "journal");
        detail = "Étape en cours : action attendue.";
      }
    } else {
      // 2) Déduction via les actions proposées
      if (actionsProgramme.length > 0) {
        cible = "programme";
        detail = `${actionsProgramme.length} action(s) de programme / vote disponible(s).`;
      } else if (actionsReste.length > 0) {
        cible = "actions";
        detail = `${actionsReste.length} autre(s) action(s) disponible(s).`;
      } else {
        cible = "journal";
        detail = "Aucune action immédiate : surveille le journal / système.";
      }
    }

    return { titre, detail, cible };
  })();

  const bandeauTour = (
    <div className="flex items-start justify-between gap-3">
      <div className="min-w-0">
        <div className="text-sm font-semibold text-blancNordique/95 truncate">
          {prochaineEtape.titre}
        </div>
        <div className="text-xs text-blancNordique/80 whitespace-pre-wrap break-words">
          {prochaineEtape.detail}
        </div>
      </div>
      <button
        type="button"
        onClick={() => setMobileTab(prochaineEtape.cible)}
        className="shrink-0 text-[11px] px-3 py-2 rounded-full border border-bleu-glacier bg-slate-900/40 hover:bg-slate-800 transition"
        aria-label="Aller à l'étape"
        title="Aller à l'étape"
      >
        Aller
      </button>
    </div>
  );


  // HEADER : titre + tour + phase
  const nomTablePourPartie = lireNomTablePourPartie(etatVue.partie_id ?? partieId);
  const titrePartie = nomTablePourPartie
    ? nomTablePourPartie
    : `Partie ${idCourt(etatVue.partie_id)}`;

  const header = (
    <div className="flex flex-col gap-2 w-full">
      <div className="flex items-start justify-between w-full gap-4">
        <div>
          <h1 className="text-2xl font-semibold">
            <span>{titrePartie}</span>
          </h1>
          <p className="text-sm opacity-80">
            Tour {etatVue.tour ?? "?"} · phase {etatVue.phase}
            {etatVue.sous_phase ? ` / ${etatVue.sous_phase}` : ""}
          </p>
        </div>

        {/* Rappel clair du joueur courant */}
        <div className="flex items-center gap-2 text-xs">
          <div className="inline-flex items-center gap-2 rounded-full border border-bleu-glacier px-3 py-1 bg-slate-900/70">
            <span className="text-[10px] uppercase tracking-wide opacity-70">
              Ministre
            </span>
            <span className="font-semibold">
              {joueur.alias ?? joueur.nom ?? idCourt(joueur.id_joueur)}
            </span>
          </div>

          {/* bouton pour ouvrir la barre latérale */}
          <button
            type="button"
            onClick={() => setSidePanelOpen(true)}
            className="inline-flex items-center gap-1 rounded-full border border-bleu-glacier px-2 py-1 bg-slate-900/70 hover:bg-slate-800 transition text-[10px] uppercase tracking-wide"
          >
            <span>Vue &amp; profil</span>
          </button>
        </div>
      </div>
    </div>
  );


  // VUE ÉTAT GÉNÉRAL
  const vueEtat = (
    <PlayerStatusPanel
      joueurs={joueursPanel}
      tour={etatVue.tour}
      capitalCollectif={capitalCollectif}
      capitalOpposition={capitalOpposition}
      partieId={etatVue.partie_id}
      joueurId={acteurId}
      axes={axes}
      budget={budget}
    />
  );


  // VUE PROGRAMME
  const vueProgramme = (
    <ProgrammeView
      programme={etatVue.programme_cabinet}
      main={etatVue.main_joueur_courant}
      partieId={etatVue.partie_id}
      acteurId={acteurId}
      aliasParJoueur={aliasParJoueur}
      attenteType={attenteType}
      actionsProgramme={actionsProgramme}
      uiActions={uiActions}
      programmeVotes={(etatVue as any).programme_votes}
      programmeVerdict={(etatVue as any).programme_verdict}
      onVoirCarteDetails={(carteId: string) => {
        setCarteSelectionneeId(carteId);
        setMobileTab("actions");
      }}
      onActionSent={handleActionSent}
    />
  );


  // VUE ACTIONS / MAIN
  const vueActions = (
    <div className="flex flex-col gap-4">
      <HandView
        main={etatVue.main_joueur_courant}
        attentionDisponible={etatVue.attention_disponible}
        attentionMax={etatVue.attention_max}
        nomJoueur={joueur?.alias ?? joueur?.nom ?? joueur?.joueur_id ?? null}
        selectedCardId={carteSelectionneeId}
        onSelectCard={(id) => setCarteSelectionneeId(id)}
        onPlayCardImmediate={handlePlayCardImmediate}
      />
      {/* Option A : pas de bloc s'il n'y a rien à dire */}
      {Array.isArray(actionsReste) && actionsReste.length > 0 ? (
        <ActionsPanel
          partieId={etatVue.partie_id}
          acteurId={acteurId}
          phase={etatVue.phase}
          sousPhase={etatVue.sous_phase}
          attenteType={attenteType}
          actionsReste={actionsReste}
          uiActions={uiActions}
          main={etatVue.main_joueur_courant}
          onActionSent={handleActionSent}
        />
      ) : null}
    </div>
  );

  // VUE JOURNAL
  const vueJournal = (
    <div className="flex flex-col gap-4">
      <JournalView
        journal={etatVue.journal}
        journalRecent={journalRecent}
        currentTour={etatVue.tour ?? undefined}
      />
    </div>
  );


  const sectionsVueProfil: SectionMenu[] = [
    {
      id: "affichage",
      titre: "mode d’affichage",
      items: [
        {
          id: "layout-auto",
          libelle: "auto (selon l’écran)",
          disabled: layoutMode === "auto",
          onClick: () => setLayoutMode("auto"),
        },
        {
          id: "layout-desktop",
          libelle: "vue large (bureau)",
          disabled: layoutMode === "desktop",
          onClick: () => setLayoutMode("desktop"),
        },
        {
          id: "layout-mobile",
          libelle: "vue mobile (panneaux)",
          disabled: layoutMode === "mobile",
          onClick: () => setLayoutMode("mobile"),
        },
      ],
    },
    {
      id: "profil",
      titre: "profil du joueur",
      items: [
        {
          id: "copier-id",
          libelle: "copier mon identifiant",
          description: joueur.id_joueur,
          onClick: () => copierTexte(joueur.id_joueur),
        },
        ...(joueur.alias
          ? [
              {
                id: "copier-alias",
                libelle: "copier mon alias",
                description: joueur.alias,
                onClick: () => copierTexte(joueur.alias as string),
              },
            ]
          : []),
        ...(joueur.courriel
          ? [
              {
                id: "copier-courriel",
                libelle: "copier mon courriel",
                description: joueur.courriel,
                onClick: () => copierTexte(joueur.courriel as string),
              },
            ]
          : []),
      ],
    },
    {
      id: "partie",
      titre: "partie",
      items: [
        {
          id: "quitter",
          libelle: quitterEnCours ? "quitter… (en cours)" : "quitter la partie",
          description: "retour au lobby (via l’ancrage)",
          disabled: quitterEnCours,
          onClick: handleQuitterPartie,
        },
        ...(estHote
          ? [
              {
                id: "arreter",
                libelle: arreterEnCours ? "arrêter… (en cours)" : "arrêter la partie",
                description: "met fin à la partie et affiche les résultats",
                danger: true,
                disabled: arreterEnCours,
                onClick: handleArreterPartie,
              },
            ]
          : []),
      ],
    },
  ];
  return (
    <>
      <GameLayout
        layoutMode={layoutMode}
        header={header}
        bandeauTour={bandeauTour}
        vueEtat={vueEtat}
        vueProgramme={vueProgramme}
        vueActions={vueActions}
        vueJournal={vueJournal}
        tabMeta={tabMeta}
        activeTab={mobileTab}
        onTabChange={setMobileTab}
        indicateurGlobal={
          <span>
            Actions disponibles :{" "}
            <span className="font-semibold text-blanc-nordique">
              {typeof etatVue.attention_disponible === "number"
                ? etatVue.attention_disponible
                : "?"}
            </span>
          </span>
        }
      />

      {/* Toasts (haut droite) */}
      {toasts.length > 0 ? (
        <div className="fixed top-3 right-3 z-[60] w-[320px] max-w-[90vw] space-y-2">
          {toasts.map((t) => (
            <div
              key={t.id}
              className={
                "rounded-card px-3 py-2 shadow-modal border ring-1 ring-white/10 backdrop-blur-sm " +
                (t.severity === "error"
                  ? "bg-slate-950 border-rougeErable/70"
                  : "bg-slate-950 border-bleuGlacier/60")
              }
            >
              <div className="flex items-start justify-between gap-2">
                <div className="min-w-0">
                  <div className="text-xs font-semibold text-blancNordique truncate">
                    {t.title}
                  </div>
                  <div className="text-xs text-blancNordique/90 whitespace-pre-wrap break-words">
                    {t.message}
                  </div>
                </div>
                <button
                  type="button"
                  className="text-[11px] px-2 py-1 rounded border border-white/20 hover:bg-white/10"
                  onClick={() => setToasts((prev) => prev.filter((x) => x.id !== t.id))}
                  aria-label="Fermer"
                >
                  ✕
                </button>
              </div>
            </div>
          ))}
        </div>
      ) : null}

      {/* barre latérale escamotable */}
      {sidePanelOpen && (
        <>
          {/* overlay cliquable pour fermer */}
          <div
            className="fixed inset-0 bg-black/40 z-40"
            onClick={() => setSidePanelOpen(false)}
          />

          <aside className="fixed top-0 right-0 h-full w-72 max-w-full bg-slate-900 border-l border-bleu-glacier z-50 flex flex-col">
            <div className="flex items-center justify-between px-3 py-2 border-b border-bleu-glacier">
              <h2 className="text-sm font-semibold">
                Vue &amp; profil
              </h2>
              <button
                type="button"
                onClick={() => setSidePanelOpen(false)}
                className="text-xs px-2 py-1 rounded border border-bleu-glacier hover:bg-slate-800"
              >
                Fermer
              </button>
            </div>

            <div className="flex-1 overflow-y-auto px-3 py-2 text-xs space-y-4">
              {sectionsVueProfil.map((sec) => (
                <section key={sec.id}>
                  <h3 className="text-[11px] font-semibold mb-1 uppercase tracking-wide opacity-80">
                    {sec.titre}
                  </h3>
                  <div className="space-y-1">
                    {sec.items.map((it) => (
                      <button
                        key={it.id}
                        type="button"
                        disabled={!!it.disabled}
                        onClick={() => it.onClick()}
                        className={
                          "w-full text-left px-2 py-1 rounded border text-[11px] transition " +
                          (it.danger
                            ? "border-rougeErable/60 text-rougeErable hover:bg-rougeErable/10"
                            : (it.disabled
                              ? "border-transparent opacity-60 cursor-not-allowed"
                              : "border-transparent hover:bg-slate-800/60"))
                        }
                        title={it.description}
                      >
                        <div className="flex flex-col">
                          <span className="font-semibold">{it.libelle}</span>
                          {it.description ? (
                            <span className="text-[10px] opacity-75">{it.description}</span>
                          ) : null}
                        </div>
                      </button>
                    ))}
                  </div>

                  {sec.id === "partie" && (erreurQuitter || erreurArreter) ? (
                    <div className="mt-2 text-[11px] text-rougeErable/90 whitespace-pre-wrap">
                      {erreurQuitter ?? erreurArreter}
                    </div>
                  ) : null}
                </section>
              ))}
            </div>
          </aside>
        </>
      )}
      <FlashUneModal
        ouvert={flashOuvert && flashQueue.length > 0}
        file={flashQueue}
        onSuivant={() => {
          setFlashQueue((q) => q.slice(1));
        }}
        onFermer={() => {
          setFlashOuvert(false);
          setFlashQueue([]);

          // si on ferme, on considère le tour lu (pour éviter replay au refresh)
          const tour = typeof etatVue.tour === "number" ? etatVue.tour : null;
          if (tour != null && storageKeyFlashLu) {
            localStorage.setItem(storageKeyFlashLu, String(tour));
          }

          // on vide la queue (option : tu peux la garder si tu veux “revoir”)
          setFlashQueue([]);
        }}
        onToutLire={() => {
          // On vide la queue courante
         setFlashQueue([]);

          // On ferme la modal
          setFlashOuvert(false);

          // On considère le tour "lu" (même logique que Fermer)
          const tour = typeof etatVue.tour === "number" ? etatVue.tour : null;
          if (tour != null && storageKeyFlashLu) {
            localStorage.setItem(storageKeyFlashLu, String(tour));
          }

        }}
      />
    </>
  );

};

export default GamePage;

