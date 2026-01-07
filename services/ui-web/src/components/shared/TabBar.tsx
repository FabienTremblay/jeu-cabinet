// src/components/shared/TabBar.tsx
import React from "react";

export type OngletId = "etat" | "programme" | "actions" | "journal";

export type OngletMeta = {
  /** libellé (ex: "Victoire" au lieu de "État") */
  label?: string;
  /** petit badge (ex: "?" ou "!" ou "3") */
  badge?: string | null;
  /** attire l'attention (mobile surtout) */
  pulse?: boolean;
};

interface Onglet {
  id: OngletId;
  label: string;
}

const ONGLET_LISTE: Onglet[] = [
  { id: "etat", label: "État" },
  { id: "programme", label: "Programme" },
  { id: "actions", label: "Actions" },
  { id: "journal", label: "Journal" },
];

interface TabBarProps {
  actif: OngletId;
  onChange: (onglet: OngletId) => void;
  /** personnalisation légère (label/badge/pulse) */
  meta?: Partial<Record<OngletId, OngletMeta>>;
  /** ajuste le style pour la barre d'onglets mobile */
  mobile?: boolean;
}

export const TabBar: React.FC<TabBarProps> = ({
  actif,
  onChange,
  meta,
  mobile = false,
}) => {
  return (
    <div
      className={
        "flex rounded-md overflow-hidden border border-bleu-glacier " +
        (mobile ? "text-[12px]" : "text-sm")
      }
    >
      {ONGLET_LISTE.map((onglet) => {
        const m = meta?.[onglet.id];
        const label = (m?.label ?? onglet.label).trim();
        const badge = m?.badge ?? null;
        const pulse = !!m?.pulse;

        const actifCls =
          onglet.id === actif
            ? " bg-blanc-nordique text-bleu-boreal"
            : " bg-bleu-boreal text-blanc-nordique/80";

        return (
          <button
            key={onglet.id}
            type="button"
            onClick={() => onChange(onglet.id)}
            className={
              "relative flex-1 px-2 py-2 text-center flex items-center justify-center gap-2" +
              actifCls +
              (pulse && onglet.id !== actif ? " animate-pulse" : "")
            }
          >
            <span className="truncate max-w-[9rem]">{label}</span>
            {badge ? (
              <span
                className={
                  "inline-flex items-center justify-center min-w-[18px] h-[18px] px-1 rounded-full border text-[11px] " +
                  (onglet.id === actif
                    ? "border-bleu-boreal/30 bg-bleu-boreal/10"
                    : "border-white/20 bg-white/10")
                }
                aria-label={`Indicateur ${label}`}
              >
                {badge}
              </span>
            ) : null}
          </button>
        );
      })}
    </div>
  );
};

export default TabBar;

