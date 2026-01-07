// src/components/game/HandView.tsx
import React, { useEffect, useState } from "react";
import type { CarteDansMain } from "../../types/game";
import carteContreCoupBg from "../../assets/contre_coup.png";
import carteInfluenceBg from "../../assets/influence.png";
import carteMesureBg from "../../assets/mesure.png";
import carteMinistereBg from "../../assets/ministere.png";
import carteRelationBg from "../../assets/relation.png";

function normaliserTypeCarte(carte: CarteDansMain): string {
  return String((carte as any)?.type ?? "")
    .trim()
    .toLowerCase()
    .replace("-", "_");
}

function assetPourCarte(carte: CarteDansMain): string {
  const t = normaliserTypeCarte(carte);
  switch (t) {
    case "contre_coup":
      return carteContreCoupBg;
    case "mesure":
      return carteMesureBg;
    case "ministere":
      return carteMinistereBg;
    case "relation":
      return carteRelationBg;
    case "influence":
    default:
      // fallback demandé
      return carteInfluenceBg;
  }
}

type PaletteTexteCarte = {
  titre: string;
  corps: string;
  ombre: React.CSSProperties;
};

function paletteTextePourCarte(carte: CarteDansMain): PaletteTexteCarte {
  const t = normaliserTypeCarte(carte);

  // mesure est très claire → texte foncé lisible
  if (t === "mesure") {
    return {
      titre: "text-slate-900",
      corps: "text-slate-900",
      ombre: {}, // inutile ici
    };
  }

  // le reste est plutôt sombre/moyen → texte clair + ombre
  return {
    titre: "text-white",
    corps: "text-white",
    ombre: { textShadow: "0 1px 2px rgba(0,0,0,0.65)" },
  };
}
export interface JouerCarteParams {
  effort_attention?: number;
  effort_cp?: number;
}

interface HandViewProps {
  main: CarteDansMain[] | null | undefined;
  attentionDisponible?: number | null;
  attentionMax?: number | null;
  /** Nom affiché pour l'incarnation (ex: "Fabien") */
  nomJoueur?: string | null;
  /** Carte à mettre en évidence (ex: venant de l'onglet Programme -> Détails) */
  selectedCardId?: string | null;
  /** Notifie la sélection (utile si on veut un clic pour fixer la carte) */
  onSelectCard?: (carteId: string) => void;
  onPlayCardImmediate?: (carteId: string, params?: JouerCarteParams) => void;
}

const HandView: React.FC<HandViewProps> = ({
  main,
  attentionDisponible,
  attentionMax,
  nomJoueur,
  selectedCardId,
  onSelectCard,
  onPlayCardImmediate,
}) => {
  const cartes = main ?? [];

  // carte pour laquelle on est en train de régler l'effort
  const [carteIdEnPreparation, setCarteIdEnPreparation] = useState<string | null>(null);
  const [effortAttention, setEffortAttention] = useState<string>("");
  const [effortCp, setEffortCp] = useState<string>("");

  // reset si la main change
  useEffect(() => {
    setCarteIdEnPreparation(null);
    setEffortAttention("");
    setEffortCp("");
  }, [cartes.length]);

  // Scroll vers la carte sélectionnée (utile quand on vient de l'onglet Programme)
  useEffect(() => {
    if (!selectedCardId) return;
    // laisse React peindre
    const t = window.setTimeout(() => {
      const el = document.getElementById(`carte-main-${selectedCardId}`);
      if (el && typeof (el as any).scrollIntoView === "function") {
        (el as any).scrollIntoView({ behavior: "smooth", block: "nearest", inline: "center" });
      }
    }, 0);
    return () => window.clearTimeout(t);
  }, [selectedCardId, cartes.length]);
  const cardClass =
    "rounded-card border border-slate-700 bg-slate-900/70 shadow-carte p-3";
  const cardTitleClass =
    "text-xs font-semibold text-slate-100 mb-2 tracking-wide";

  const handleClickUtiliser = (carte: CarteDansMain) => {
    if (!onPlayCardImmediate) return;

    // ⚠️ on regarde si la carte a des jokers d'effort
    const demandeEffortAttention =
      (carte as any).demande_effort_attention === true;
    const demandeEffortCp = (carte as any).demande_effort_cp === true;
    const cartePeutAjusterEffort = demandeEffortAttention || demandeEffortCp;

    // si aucun joker d'effort → on joue immédiatement, sans params
    if (!cartePeutAjusterEffort) {
      onPlayCardImmediate(carte.id);
      return;
    }

    // sinon, on ouvre le panneau de paramétrage,
    // en pré-remplissant avec les coûts de base quand ils existent
    setCarteIdEnPreparation(carte.id);
    setEffortAttention(
      demandeEffortAttention && typeof carte.cout_attention === "number"
        ? String(carte.cout_attention)
        : ""
    );
    setEffortCp(
      demandeEffortCp && typeof carte.cout_cp === "number"
        ? String(carte.cout_cp)
        : ""
    );
  };

  const handleConfirmerCarte = (carte: CarteDansMain) => {
    if (!onPlayCardImmediate) return;

    const demandeEffortAttention =
      (carte as any).demande_effort_attention === true;
    const demandeEffortCp =
      (carte as any).demande_effort_cp === true;

    const params: JouerCarteParams = {};

    if (demandeEffortAttention) {
      const attTrim = effortAttention.trim();
      if (attTrim !== "") {
        const n = Number(attTrim);
        if (!Number.isNaN(n)) {
          params.effort_attention = n;
        }
      }
    }

    if (demandeEffortCp) {
      const cpTrim = effortCp.trim();
      if (cpTrim !== "") {
        const n = Number(cpTrim);
        if (!Number.isNaN(n)) {
          params.effort_cp = n;
        }
      }
    }

    // si aucun param n’a été effectivement renseigné,
    // on laisse le moteur utiliser les valeurs par défaut
    if (Object.keys(params).length === 0) {
      onPlayCardImmediate(carte.id);
    } else {
      onPlayCardImmediate(carte.id, params);
    }

    setCarteIdEnPreparation(null);
    setEffortAttention("");
    setEffortCp("");
  };

  const handleAnnulerPreparation = () => {
    setCarteIdEnPreparation(null);
    setEffortAttention("");
    setEffortCp("");
  };


  return (
    <div className={cardClass}>
      <div className="mb-2">
        <h3 className={cardTitleClass}>
          Les cartes de {nomJoueur?.trim() ? nomJoueur : "moi"}
        </h3>
        <div className="text-[11px] text-slate-300">
          L’utilisation de ces cartes ici affecte directement le jeu.
        </div>
      </div>

      {/* carrousel horizontal */}
      <div className="flex items-stretch gap-3 overflow-x-auto pb-1">
        {cartes.map((carte, index) => {
          const effetTexte = carte.details ?? "";

          const conditions: React.ReactNode[] = [];
          if (typeof carte.cout_attention === "number") {
            if (carte.cout_attention > 0) {
              conditions.push(
                <div key="cond-att">🕒 Coûte {carte.cout_attention} action(s) ce tour</div>
              );
            }
          }
          if (typeof carte.cout_cp === "number") {
            if (carte.cout_cp > 0) {
              conditions.push(
                <div key="cond-cp">⭐ Demande du soutien politique</div>
              );
            }
          }
          const conditionsBloc = conditions.length > 0 ? conditions : [<div key="cond-vide">—</div>];

          const estEnPreparation = carteIdEnPreparation === carte.id;
          const palette = paletteTextePourCarte(carte);

          const demandeEffortAttention =
            (carte as any).demande_effort_attention === true;
          const demandeEffortCp =
            (carte as any).demande_effort_cp === true;

          return (
            <div
              key={carte.uid ?? `${carte.id}-${index}`}
              id={`carte-main-${carte.id}`}
              className="flex flex-col items-stretch min-w-[220px] max-w-[240px]"
              onClick={() => onSelectCard?.(carte.id)}
            >
              {/* Carte skinnée */}
              <div className="relative w-full aspect-[2/3]">
                <img
                  src={assetPourCarte(carte)}
                  alt=""
                  className="absolute inset-0 h-full w-full rounded-card shadow-carte pointer-events-none select-none"
                />

                <div className="absolute inset-0 flex flex-col px-4 pt-8 pb-8">
                  <div className={`text-center leading-tight ${palette.titre}`} style={palette.ombre}>
                    <div className="text-[10px] font-semibold tracking-wide">
                      {carte.id}
                    </div>
                    <div className="mt-1 text-[13px] font-semibold whitespace-pre-line">
                      {carte.nom}
                    </div>
                  </div>

                <div className="flex-1 flex items-center justify-center pt-16 pb-1 overflow-hidden">
                  {effetTexte && (
                    <p
                      className={`text-[11px] leading-snug text-center ${palette.corps} line-clamp-4`}
                      style={palette.ombre}
                    >
                      {effetTexte}
                    </p>
                  )}
                </div>

                  <div className="mt-auto mb-7">
                    <div
                      className={`text-[11px] leading-snug text-center ${palette.corps}`}
                      style={palette.ombre}
                    >
                      {conditionsBloc}
                    </div>
                  </div>

                </div>
              </div>

              {/* Bouton principal sous la carte */}
              <button
                type="button"
                onClick={() => handleClickUtiliser(carte)}
                className="mt-2 w-full inline-flex justify-center rounded-card bg-bleu-ministre hover:bg-bleu-glacier text-[11px] font-medium text-blanc-nordique py-1.5 transition-colors"
                disabled={!onPlayCardImmediate}
              >
                Jouer immédiatement
              </button>

              {/* Panneau d'effort uniquement si la carte a des jokers d'effort */}
              {estEnPreparation && (demandeEffortAttention || demandeEffortCp) && (
                <div className="mt-2 w-full rounded-card border border-slate-700 bg-slate-900/80 px-2 py-2 space-y-2">
                  <div className="text-[10px] font-semibold text-slate-200">
                    Intensité de l&apos;action
                  </div>
                  <div className="flex gap-2">
                    {demandeEffortAttention && (
                      <label className="flex-1 flex flex-col text-[10px] text-slate-200">
                        Effort d&apos;attention
                        <input
                          type="number"
                          className="mt-0.5 rounded border border-slate-700 bg-slate-950 px-1 py-0.5 text-[11px]"
                          value={effortAttention}
                          onChange={(e) => setEffortAttention(e.target.value)}
                          min={0}
                        />
                      </label>
                    )}
                    {demandeEffortCp && (
                      <label className="flex-1 flex flex-col text-[10px] text-slate-200">
                        Effort de capital politique
                        <input
                          type="number"
                          className="mt-0.5 rounded border border-slate-700 bg-slate-950 px-1 py-0.5 text-[11px]"
                          value={effortCp}
                          onChange={(e) => setEffortCp(e.target.value)}
                          min={0}
                        />
                      </label>
                    )}
                  </div>
                  <div className="flex justify-end gap-2 pt-1">
                    <button
                      type="button"
                      className="text-[11px] px-2 py-1 rounded border border-slate-600 text-slate-200 hover:bg-slate-800"
                      onClick={handleAnnulerPreparation}
                    >
                      Annuler
                    </button>
                    <button
                      type="button"
                      className="text-[11px] px-3 py-1 rounded bg-bleu-glacier text-slate-900 font-semibold disabled:opacity-60"
                      onClick={() => handleConfirmerCarte(carte)}
                      disabled={!onPlayCardImmediate}
                    >
                      Confirmer
                    </button>
                  </div>
                </div>
              )}
            </div>
          );
        })}

        {cartes.length === 0 && (
          <p className="text-xs text-slate-400">Aucune carte en main.</p>
        )}
      </div>
    </div>
  );
};

export default HandView;

