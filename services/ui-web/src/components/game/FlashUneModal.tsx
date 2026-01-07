// src/components/game/FlashUneModal.tsx

import React, { useEffect } from "react";

export type FlashUneArticle = {
  key: string; // ex: "P000001:tour-3:EVT-006"
  tour: number | null;
  evenement_id: string;
  titre: string;
  chapo: string;
  impacts?: string | null;
  badge?: string | null;
};

type Props = {
  ouvert: boolean;
  file: FlashUneArticle[]; // queue
  onSuivant: () => void;
  onFermer: () => void;
  onToutLire?: () => void;
};

function stop(e: React.MouseEvent) {
  e.stopPropagation();
}

export default function FlashUneModal({
  ouvert,
  file,
  onSuivant,
  onFermer,
  onToutLire,
}: Props) {
  const courant = file[0] ?? null;

  // ESC pour fermer ; Enter = suivant
  useEffect(() => {
    if (!ouvert) return;

    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") onFermer();
      if (e.key === "Enter") {
        if (file.length > 1) onSuivant();
        else onFermer();
      }
    };

    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [ouvert, file.length, onFermer, onSuivant]);

  // Empêcher le scroll de la page sous la modal (mobile surtout)
  useEffect(() => {
    if (!ouvert) return;
    const prev = document.body.style.overflow;
    document.body.style.overflow = "hidden";
    return () => {
      document.body.style.overflow = prev;
    };
  }, [ouvert]);

  if (!ouvert || !courant) return null;

  const idxLabel = file.length > 1 ? `1/${file.length}` : "";
  const tourLabel =
    typeof courant.tour === "number" ? `tour ${courant.tour}` : "tour ?";
  const titreAffiche =
    courant.titre && courant.titre !== courant.evenement_id
      ? courant.titre
      : "édition spéciale";

  return (
    <div
      className="fixed inset-0 z-[80] bg-black/70 backdrop-blur-[2px] flex items-center justify-center p-3 sm:p-4"
      onClick={onFermer}
      role="dialog"
      aria-modal="true"
      aria-label="Flash médiatique"
    >
      <div
        className="
          w-full max-w-[720px]
          max-h-[calc(100vh-1.25rem)]
          sm:max-h-[calc(100vh-2rem)]
          rounded-card shadow-modal border border-bleuGlacier/40 bg-bleuBoreal/95 overflow-hidden
          flex flex-col
        "
        onClick={stop}
        style={{
          paddingTop: "max(0.75rem, env(safe-area-inset-top))",
          paddingBottom: "max(0.75rem, env(safe-area-inset-bottom))",
        }}
      >
        {/* Bandeau FLASH */}
        <div className="px-3 py-2 sm:px-4 sm:py-3 border-b border-white/10 flex items-center justify-between gap-3">
          <div className="min-w-0">
            <div className="flex items-center gap-2">
              <span className="text-[10px] uppercase tracking-widest font-semibold text-rougeErable">
                FLASH
              </span>
              <span className="text-[10px] uppercase tracking-widest text-blancNordique/70">
                cabinet info
              </span>
              <span className="text-[10px] text-blancNordique/50">•</span>
              <span className="text-[10px] uppercase tracking-wide text-blancNordique/70">
                {tourLabel}
              </span>
            </div>

            <div className="hidden sm:block text-[11px] text-blancNordique/60 mt-1">
              Un tour ≈ quelques mois — impacts immédiats sur le rapport de force.
            </div>
          </div>

          <div className="flex items-center gap-2">
            {idxLabel ? (
              <span className="text-[10px] px-2 py-[2px] rounded-full border border-white/15 text-blancNordique/70">
                {idxLabel}
              </span>
            ) : null}
            <button
              type="button"
              onClick={onFermer}
              className="text-[11px] px-2 py-1 rounded border border-white/15 hover:bg-white/5"
              aria-label="Fermer"
            >
              ✕
            </button>
          </div>
        </div>

        {/* Corps (scroll interne) */}
        <div className="flex-1 overflow-y-auto px-3 py-3 sm:px-4 sm:py-4">
          {/* Badge */}
          <div className="flex items-center gap-2 mb-3">
            <span className="text-[10px] px-2 py-[2px] rounded-full border border-bleuGlacier/40 text-bleuGlacier bg-white/5">
              {courant.badge ?? "actualité"}
            </span>

            {/* ID technique, discret (tu peux le masquer si tu veux) */}
            <span className="ml-auto text-[10px] text-blancNordique/35">
              {courant.evenement_id}
            </span>
          </div>

          <h3 className="font-titre text-xl sm:text-2xl md:text-3xl leading-snug text-blancNordique">
            {titreAffiche}
          </h3>

          <p className="mt-3 text-[12px] sm:text-[13px] md:text-[14px] text-blancNordique/85 whitespace-pre-wrap">
            {courant.chapo}
          </p>

          {courant.impacts ? (
            <div className="mt-4 rounded-card border border-white/10 bg-black/20 px-3 py-2">
              <div className="text-[10px] uppercase tracking-wide text-blancNordique/60">
                répercussions immédiates
              </div>
              <div className="text-[12px] text-blancNordique/85 mt-1">
                {courant.impacts}
              </div>
            </div>
          ) : null}
        </div>

        {/* Actions (empilées sur mobile) */}
        <div className="px-3 py-2 sm:px-4 sm:py-3 border-t border-white/10 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2 sm:gap-3">
          <div className="flex items-center gap-2">
            {typeof onToutLire === "function" && file.length > 1 ? (
              <button
                type="button"
                onClick={onToutLire}
                className="w-full sm:w-auto text-[11px] px-3 py-2 rounded-card border border-white/15 hover:bg-white/5"
              >
                Tout lire
              </button>
            ) : null}
          </div>

          <div className="flex items-center gap-2 justify-end">
            {file.length > 1 ? (
              <button
                type="button"
                onClick={onSuivant}
                className="w-full sm:w-auto text-[11px] px-3 py-2 rounded-card bg-bleuGlacier/20 border border-bleuGlacier/40 hover:bg-bleuGlacier/30"
              >
                Suivant ▸
              </button>
            ) : (
              <button
                type="button"
                onClick={onFermer}
                className="w-full sm:w-auto text-[11px] px-3 py-2 rounded-card bg-bleuGlacier/20 border border-bleuGlacier/40 hover:bg-bleuGlacier/30"
              >
                Continuer
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

