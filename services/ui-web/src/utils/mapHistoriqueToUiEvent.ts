// src/utils/mapHistoriqueToUiEvent.ts

export type AnyEvent = Record<string, any>;

export type UiKind = "story" | "phase" | "action" | "hand" | "system" | "tech";
export type UiSeverity = "info" | "success" | "warn" | "error";

export type UiEvent = {
  id: string;
  source: "moteur" | "ui-etat";
  tour?: number | null;
  at?: string | null;

  kind: UiKind;
  severity: UiSeverity;

  title?: string;
  message: string;

  rawType?: string;
  raw?: AnyEvent;
};

export type JournalRecentEvent = {
  event_id: string;
  occurred_at: string;
  category?: string | null;
  severity?: string | null;
  message: string;
  code?: string | null;
  meta?: Record<string, any> | null;
  audience?: Record<string, any> | null;
};

function asLower(v: unknown): string {
  return v == null ? "" : String(v).toLowerCase();
}

function normalizeType(raw: unknown): string {
  const t = asLower(raw).trim();
  // alias fréquents : les types “étape” arrivent parfois en MAJUSCULES
  if (t === "engager_carte") return "engager_carte";
  if (t === "vote") return "vote";
  if (t === "perturbation_vote") return "perturbation_vote";
  return t;
}

function getTourRaw(e: AnyEvent): number | null {
  const t = e?.tour;
  return typeof t === "number" && Number.isFinite(t) ? t : null;
}

function getMessageRaw(e: AnyEvent): string {
  const direct = e?.message ?? e?.texte ?? e?.payload?.message;
  if (typeof direct === "string") return direct;
  try {
    return JSON.stringify(e);
  } catch {
    return "(événement illisible)";
  }
}

function getStableId(e: AnyEvent, fallback: string): string {
  return String(
    e?.event_id ??
      e?.id ??
      e?.evenement_id ??
      e?.entree_uid ??
      e?.mission_id ??
      e?.carte_id ??
      fallback
  );
}

export function toUiSeverity(raw?: string | null): UiSeverity {
  const s = asLower(raw);
  if (s === "error" || s === "erreur") return "error";
  if (s === "warn" || s === "warning" || s === "avertissement") return "warn";
  if (s === "success" || s === "ok") return "success";
  return "info";
}

export function kindFromMoteurType(typeLower: string): UiKind {
  if (typeLower === "journal") return "story";

  if (
    typeLower === "phase" ||
    typeLower === "vote" ||
    typeLower === "engager_carte" ||
    typeLower === "perturbation_vote" ||
    typeLower === "programme_reset"
  )
    return "phase";

  if (
    typeLower === "programme_carte_engagee" ||
    typeLower === "vote_enregistre" ||
    typeLower === "contre_coup" ||
    typeLower === "joueur_jouer_carte_echec" ||
    typeLower === "ministre"
  )
    return "action";

  if (typeLower === "piocher" || typeLower === "defausser_carte") return "hand";

  if (
    typeLower === "partie_terminee" ||
    typeLower === "joueur_quitte_definitivement"
  )
    return "system";

  return "tech";
}

export function severityFromMoteurEvent(typeLower: string, e: AnyEvent): UiSeverity {
  if (e?.severity) return toUiSeverity(e.severity);

  if (typeLower === "partie_terminee") return "error";
  if (typeLower === "joueur_quitte_definitivement") return "warn";
  if (typeLower === "contre_coup") return "warn";
  if (typeLower === "joueur_jouer_carte_echec") return "warn";
  if (typeLower === "ministre") return "success";
  if (typeLower === "programme_carte_engagee") return "success";

  return "info";
}

export function titleFromMoteur(typeLower: string, e: AnyEvent): string | undefined {
  if (typeLower === "journal" && e?.indicateurs) return "Institut de la statistique";
  if (typeLower === "journal" && e?.mission_id) return "Opposition";

  if (typeLower === "programme_carte_engagee") return "Carte engagée";
  if (typeLower === "vote_enregistre") return "Vote enregistré";
  if (typeLower === "contre_coup") return "Contre-coup";
  if (typeLower === "joueur_jouer_carte_echec") return "Action refusée";
  if (typeLower === "ministre") return "Carte jouée";

  if (typeLower === "piocher") return "Pioche";
  if (typeLower === "defausser_carte") return "Défausse";

  if (typeLower === "partie_terminee") return "Fin de partie";
  if (typeLower === "joueur_quitte_definitivement") return "Joueur parti";

  if (typeLower === "phase") return "Phase";

  return undefined;
}

export function messageFromMoteur(typeLower: string, e: AnyEvent): string {
  if (typeLower === "programme_carte_engagee") {
    const j = e?.joueur_id ?? e?.joueur ?? "joueur ?";
    const c = e?.carte_id ?? e?.carte ?? "carte ?";
    return `${j} engage ${c} au programme.`;
  }

  if (typeLower === "vote_enregistre") {
    const j = e?.payload?.joueur_id ?? e?.joueur_id ?? "joueur ?";
    const v = e?.payload?.valeur ?? e?.valeur ?? "?";
    return `${j} a voté (${v}).`;
  }

  if (typeLower === "piocher") {
    const j = e?.joueur ?? e?.joueur_id ?? "joueur ?";
    const n = Array.isArray(e?.cartes) ? e.cartes.length : null;
    return n != null ? `${j} pioche ${n} cartes.` : `${j} pioche des cartes.`;
  }

  if (typeLower === "defausser_carte") {
    const j = e?.joueur ?? e?.joueur_id ?? "joueur ?";
    const c = e?.carte ?? e?.carte_id ?? "carte ?";
    return `${j} défausse ${c}.`;
  }

  if (typeLower === "phase") {
    const ph = e?.phase ?? "tour";
    const sp = e?.sous_phase ? ` / ${e.sous_phase}` : "";
    return `${ph}${sp}`;
  }

  if (typeLower === "programme_reset") {
    const n = typeof e?.nb_entrees === "number" ? e.nb_entrees : null;
    if (n === 0) return "Programme réinitialisé (vide).";
    if (n != null) return `Programme réinitialisé (${n} entrée${n > 1 ? "s" : ""}).`;
    return "Programme réinitialisé.";
  }

  if (typeLower === "joueur_jouer_carte_echec") {
    const p = e?.payload ?? {};
    const j = p?.joueur_id ?? e?.joueur_id ?? e?.joueur ?? "joueur ?";
    const c = p?.carte_id ?? e?.carte_id ?? e?.carte ?? "carte ?";
    return `Action refusée : ${j} ne peut pas jouer ${c}.`;
  }

  if (typeLower === "ministre") {
    const j = e?.joueur ?? e?.joueur_id ?? "joueur ?";
    const c = e?.carte ?? e?.carte_id ?? "carte ?";
    // Si une commande "journal" existe, on préfère son message (plus narratif)
    const cmds = Array.isArray(e?.commandes) ? e.commandes : [];
    const journalCmd = cmds.find((x: any) => x?.op === "journal" && x?.payload?.message);
    if (journalCmd?.payload?.message) return String(journalCmd.payload.message);
    return `${j} joue ${c}.`;
  }

  // Étapes “procédure” (souvent reçues sans texte) : on évite le fallback JSON
  if (typeLower === "engager_carte") return "Engagement des cartes (en cours)";
  if (typeLower === "vote") return "Vote (en cours)";
  if (typeLower === "perturbation_vote") return "Perturbation du vote (en cours)";

  if (typeLower === "partie_terminee") {
    const r = e?.raison ? ` (${e.raison})` : "";
    return `Partie terminée${r}.`;
  }

  if (typeLower === "joueur_quitte_definitivement") {
    const j = e?.joueur_id ?? "joueur ?";
    return `${j} a quitté définitivement la partie.`;
  }

  return getMessageRaw(e);
}

export function mapHistoriqueToUiEvents(
  journalMoteur: AnyEvent[] | null | undefined
): UiEvent[] {
  const moteurRaw: AnyEvent[] = Array.isArray(journalMoteur) ? journalMoteur : [];

  return moteurRaw.map((e, idx) => {
    const typeLower = normalizeType(e?.type ?? e?.category ?? "");
    const tour = getTourRaw(e);
    const kind = kindFromMoteurType(typeLower);
    const severity = severityFromMoteurEvent(typeLower, e);
    const id = getStableId(e, `moteur-${tour ?? "?"}-${idx}-${typeLower || "evt"}`);

    return {
      id,
      source: "moteur",
      tour,
      at: null,
      kind,
      severity,
      title: titleFromMoteur(typeLower, e),
      message: messageFromMoteur(typeLower, e),
      rawType: typeLower,
      raw: e,
    };
  });
}

function tryParseJsonMessage(message: any): any | null {
  if (typeof message !== "string") return null;
  const s = message.trim();
  if (!s.startsWith("{") || !s.endsWith("}")) return null;
  try {
    return JSON.parse(s);
  } catch {
    return null;
  }
}

export function mapJournalRecentToUiEvents(
  journalRecent: JournalRecentEvent[] | null | undefined
): UiEvent[] {
  const uiEtatRaw = Array.isArray(journalRecent) ? journalRecent : [];

  return uiEtatRaw.map((e) => {
    const cat = asLower(e.category);
    let kind: UiKind =
      cat === "deroulement" ? "phase"
      : cat === "action" ? "action"
      : cat === "systeme" ? "system"
      : cat === "message" ? "story"
      : "tech";

    // Stop-gap : certains backends envoient le payload brut dans message (JSON string)
    // On le convertit en message humain + meta exploitable + urgence si nécessaire.
    const parsed = tryParseJsonMessage(e.message);
    let message = e.message;
    let severity = toUiSeverity(e.severity);
    let title = e.category ? String(e.category) : "Système";
    let rawType = e.category ? asLower(e.category) : "system";
    let meta = (e.meta ?? null) as any;

    if (parsed && typeof parsed === "object") {
      // merge meta
      meta = { ...(meta ?? {}), ...parsed };

      // cas connu : échec d’engagement faute d’attention → doit être urgent
      if (parsed.type === "programme_engagement_attention_insuffisante") {
        const carteId = parsed.carte_id ?? "carte";
        message = `Échec : attention insuffisante pour engager ${carteId}.`;
        severity = "error";
        kind = "action";
        title = "Action";
        rawType = "action";
      }
    }

    return {
      id: String(e.event_id),
      source: "ui-etat",
      tour: null,
      at: e.occurred_at ?? null,
      kind,
      severity,
      title,
      message,
      rawType,
      raw: { ...e, meta } as any,
    };
  });
}

export function computePhaseBanner(moteurEvents: UiEvent[]): string | null {
  const lastPhase = [...moteurEvents].reverse().find((ev) => ev.kind === "phase");
  return lastPhase?.message ?? null;
}
