// src/components/game/JournalView.tsx

import React, { useMemo, useState } from "react";
import type { EtatPartieVue } from "../../types/game";
import {
  mapHistoriqueToUiEvents,
  mapJournalRecentToUiEvents,
  computePhaseBanner,
  type JournalRecentEvent,
  type UiEvent,
  type UiKind,
  type UiSeverity,
} from "../../utils/mapHistoriqueToUiEvent";


// ---------- Types locaux (tolérants) ----------

  type TabKey = "story" | "actions" | "system";

  interface JournalViewProps {
    journal: EtatPartieVue["journal"] | null | undefined;
    journalRecent?: JournalRecentEvent[] | null | undefined;
    currentTour?: number;
  }

    function pillClass(sev: UiSeverity): string {
      switch (sev) {
        case "error":
          return "border border-rougeErable/60 text-rougeErable";
        case "warn":
          return "border border-bleuGlacier/40 text-bleuGlacier";
        case "success":
          return "border border-bleuMinistre/50 text-bleuMinistre";
        default:
          return "border border-white/15 text-blancNordique/80";
      }
    }

    function iconForKind(kind: UiKind): string {
      switch (kind) {
        case "story":
          return "📖";
        case "action":
          return "⚙️";
        case "hand":
          return "🗂";
        case "phase":
          return "📌";
        case "system":
          return "⚠️";
        default:
          return "•";
      }
    }

  const JournalView: React.FC<JournalViewProps> = ({ journal, journalRecent, currentTour }) => {
    const [tab, setTab] = useState<TabKey>("story");

    const eventsMoteur = useMemo(() => mapHistoriqueToUiEvents(journal as any), [journal]);
    const eventsUiEtat = useMemo(() => mapJournalRecentToUiEvents(journalRecent as any), [journalRecent]);
    const phaseBanner = useMemo(() => computePhaseBanner(eventsMoteur), [eventsMoteur]);

    const filterForTab = (ev: UiEvent): boolean => {
      if (tab === "story") return ev.kind === "story";
      if (tab === "actions") return ev.kind === "action";
      // system: on accepte system/tech + phase + hand (utile pour comprendre ce qui bloque)
      return ev.kind === "system" || ev.kind === "tech" || ev.kind === "phase" || ev.kind === "hand";
    };

    const groupedByTour = useMemo(() => {
      const map = new Map<string, UiEvent[]>();

      for (const ev of eventsMoteur) {
        const key = ev.tour != null ? `tour-${ev.tour}` : "tour-?";
        if (!map.has(key)) map.set(key, []);
        map.get(key)!.push(ev);
      }

      const keys = Array.from(map.keys()).sort((a, b) => {
        const ta = Number(a.replace("tour-", ""));
        const tb = Number(b.replace("tour-", ""));
        if (Number.isFinite(ta) && Number.isFinite(tb)) return tb - ta;
        if (a === "tour-?") return 1;
        if (b === "tour-?") return -1;
        return a.localeCompare(b);
      });

      return keys.map((k) => ({ key: k, events: map.get(k)! }));
    }, [eventsMoteur]);

  return (
    <div className="w-full h-full flex flex-col">
      <div className="flex items-center justify-between mb-2">
        <h2 className="font-titre text-sm text-blancNordique">Journal</h2>
        {phaseBanner ? (
          <span className="text-[11px] px-2 py-[2px] rounded-full border border-white/15 text-blancNordique/80 max-w-[65%] truncate">
            📌 {phaseBanner}
          </span>
        ) : null}
      </div>

      {/* Tabs (réutilise tes styles globaux .tab-bar) */}
      <div className="tab-bar rounded-card overflow-hidden shadow-carte mb-2">
        <button
          className={`tab-bar__bouton ${tab === "story" ? "tab-bar__bouton--actif" : ""}`}
          onClick={() => setTab("story")}
          type="button"
        >
          Histoire
        </button>
        <button
          className={`tab-bar__bouton ${tab === "actions" ? "tab-bar__bouton--actif" : ""}`}
          onClick={() => setTab("actions")}
          type="button"
        >
          Actions
        </button>
        <button
          className={`tab-bar__bouton ${tab === "system" ? "tab-bar__bouton--actif" : ""}`}
          onClick={() => setTab("system")}
          type="button"
        >
          Système
        </button>
      </div>

      <div className="flex-1 overflow-y-auto pr-1 space-y-3">
        {/* MOTEUR : groupé par tour */}
        {(() => {
          const isTourKey = (key: string) => key !== "tour-?";
          const keyToNumber = (key: string) => (isTourKey(key) ? Number(key.replace("tour-", "")) : null);

          const currentKey =
            typeof currentTour === "number" ? `tour-${currentTour}` : null;

          const currentBlock = currentKey
            ? groupedByTour.find((b) => b.key === currentKey)
            : null;

          const unknownBlock = groupedByTour.find((b) => b.key === "tour-?");

          const previousBlocks = groupedByTour.filter((b) => {
            if (!isTourKey(b.key)) return false; // on garde tour-? à part
            const n = keyToNumber(b.key);
            return typeof n === "number" && typeof currentTour === "number" ? n < currentTour : true;
          });

          const renderTourSection = ({ key, events }: { key: string; events: UiEvent[] }) => {
          const tourLabel =
            key === "tour-?"
              ? "Tour ?"
              : `Tour ${key.replace("tour-", "")}`;

          const tourNumber =
            key === "tour-?" ? null : Number(key.replace("tour-", ""));
          const isCurrentTour =
            typeof currentTour === "number" &&
            Number.isFinite(tourNumber) &&
            tourNumber === currentTour;

          const shown = events.filter(filterForTab);

          if (shown.length === 0) return null;

          return (
            <section
              key={key}
              className={
                "rounded-card border shadow-carte " +
                (isCurrentTour
                  ? "border-bleuGlacier/60 bg-bleuBoreal/40"
                  : "border-white/10 bg-bleuBoreal/30")
              }
            >
              <div className="px-3 py-2 border-b border-white/10 flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <h3 className="text-xs font-semibold text-bleuGlacier">{tourLabel}</h3>
                  {isCurrentTour ? (
                    <span className="text-[10px] px-2 py-[1px] rounded-full border border-bleuGlacier/50 text-bleuGlacier">
                      Tour en cours
                    </span>
                  ) : null}
                </div>
                <span className="text-[11px] text-blancNordique/60">
                  {shown.length} entrée{shown.length > 1 ? "s" : ""}
                </span>
              </div>

              <ul className="px-3 py-2 space-y-2">
                {shown.map((ev) => {
                  // Hand events en repliable (tab system uniquement)
                  const isHand = ev.kind === "hand";

                  const header = (
                    <div className="flex items-start gap-2">
                      <span className="mt-[1px]">{iconForKind(ev.kind)}</span>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2">
                          {ev.title ? (
                            <span className="text-[12px] font-semibold text-blancNordique/90">
                              {ev.title}
                            </span>
                          ) : null}
                          <span className={`text-[10px] px-2 py-[1px] rounded-full ${pillClass(ev.severity)}`}>
                            {ev.severity}
                          </span>
                        </div>
                      <div className="text-[12px] text-blancNordique/85 whitespace-pre-wrap break-words">
                        {(() => {
                          const s = String(ev.message ?? "").trim();
                          const looksJson = s.startsWith("{") && s.endsWith("}");
                          if (!looksJson) return ev.message;
                          try {
                            const obj = JSON.parse(s);
                            if (obj?.type === "programme_engagement_attention_insuffisante") {
                              return `Échec : attention insuffisante pour engager ${obj.carte_id ?? "carte"}.`;
                            }
                            return ev.message;
                          } catch {
                            return ev.message;
                          }
                        })()}
                      </div>
                      </div>
                    </div>
                  );

                  if (isHand && tab === "system") {
                    const details =
                      Array.isArray(ev.raw?.cartes) ? ev.raw.cartes :
                      typeof ev.raw?.carte === "string" ? [ev.raw.carte] :
                      null;

                    return (
                      <li key={ev.id} className="rounded-card border border-white/10 bg-bleuBoreal/40 px-2 py-2">
                        <details>
                          <summary className="cursor-pointer list-none">
                            {header}
                            <div className="text-[10px] text-blancNordique/50 mt-1">
                              Cliquer pour détails
                            </div>
                          </summary>
                          {details ? (
                            <div className="mt-2 pl-6">
                              <ul className="space-y-1">
                                {details.map((c: string, i: number) => (
                                  <li key={`${ev.id}-c-${i}`} className="text-[11px] text-blancNordique/75">
                                    – {c}
                                  </li>
                                ))}
                              </ul>
                            </div>
                          ) : (
                            <div className="mt-2 pl-6 text-[11px] text-blancNordique/60">
                              (pas de détails disponibles)
                            </div>
                          )}
                        </details>
                      </li>
                    );
                  }

                  return (
                    <li key={ev.id} className="rounded-card border border-white/10 bg-bleuBoreal/40 px-2 py-2">
                      {header}
                    </li>
                  );
                })}
              </ul>
            </section>
          );
          };

          return (
            <>
              {/* Toujours visible : tour en cours */}
              {currentBlock ? renderTourSection(currentBlock) : null}

              {/* Optionnel : tour inconnu (si présent) */}
              {unknownBlock ? renderTourSection(unknownBlock) : null}

              {/* Volet : tours précédents */}
              {previousBlocks.length > 0 ? (
                <section className="rounded-card border border-white/10 bg-bleuBoreal/20 shadow-carte">
                  <details>
                    <summary className="cursor-pointer list-none px-3 py-2 flex items-center justify-between">
                      <span className="text-xs font-semibold text-bleuGlacier">
                        Tours précédents
                      </span>
                      <span className="text-[11px] text-blancNordique/60">
                        {previousBlocks.length} tour{previousBlocks.length > 1 ? "s" : ""}
                      </span>
                    </summary>
                    <div className="px-3 pb-3 space-y-3">
                      {previousBlocks.map(renderTourSection)}
                    </div>
                  </details>
                </section>
              ) : null}
            </>
          );
        })()}

        {/* UI-ETAT : uniquement sur l’onglet Système */}
        {tab === "system" && (eventsUiEtat?.length ?? 0) > 0 ? (
          <section className="rounded-card border border-white/10 bg-bleuBoreal/20 shadow-carte">
            <div className="px-3 py-2 border-b border-white/10 flex items-center justify-between">
              <h3 className="text-xs font-semibold text-bleuGlacier">Système (temps réel)</h3>
              <span className="text-[11px] text-blancNordique/60">
                {eventsUiEtat.length} entrée{eventsUiEtat.length > 1 ? "s" : ""}
              </span>
            </div>

            <ul className="px-3 py-2 space-y-2">
              {eventsUiEtat.slice(0, 20).map((ev) => (
                <li key={ev.id} className="rounded-card border border-white/10 bg-bleuBoreal/40 px-2 py-2">
                  <div className="flex items-start gap-2">
                    <span className="mt-[1px]">{iconForKind(ev.kind)}</span>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2">
                        {ev.title ? (
                          <span className="text-[12px] font-semibold text-blancNordique/90">
                            {ev.title}
                          </span>
                        ) : null}
                        <span className={`text-[10px] px-2 py-[1px] rounded-full ${pillClass(ev.severity)}`}>
                          {ev.severity}
                        </span>
                        {ev.at ? (
                          <span className="text-[10px] text-blancNordique/45 truncate">
                            {ev.at}
                          </span>
                        ) : null}
                      </div>

                      <div className="text-[12px] text-blancNordique/85 whitespace-pre-wrap break-words">
                        {ev.message}
                      </div>
                    </div>
                  </div>
                </li>
              ))}
            </ul>

            {eventsUiEtat.length > 20 ? (
              <div className="px-3 pb-2 text-[10px] text-blancNordique/50">
                (Affichage limité aux 20 derniers.)
              </div>
            ) : null}
          </section>
        ) : null}

        {/* empty state */}
        {eventsMoteur.length === 0 && (eventsUiEtat?.length ?? 0) === 0 ? (
          <div className="text-[12px] text-blancNordique/70">
            Aucun événement à afficher.
          </div>
        ) : null}
      </div>
    </div>
  );
};

export default JournalView;

