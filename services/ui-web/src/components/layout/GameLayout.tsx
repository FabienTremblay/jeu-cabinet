// src/components/layout/GameLayout.tsx
import React, { useState, useEffect, useMemo } from "react";
import TabBar, { OngletId, OngletMeta } from "../shared/TabBar";

interface GameLayoutProps {
  layoutMode?: "auto" | "desktop" | "mobile";
  header?: React.ReactNode;
  bandeauTour?: React.ReactNode;
  /** Petit indicateur global (ex: "Actions disponibles : 3") visible desktop + mobile */
  indicateurGlobal?: React.ReactNode;

  // vues logiques
  vueEtat?: React.ReactNode;
  vueProgramme?: React.ReactNode;
  vueActions?: React.ReactNode;
  vueJournal?: React.ReactNode;

  bottom?: React.ReactNode;

  /**
   * Métadonnées (label, badge, pulse) par onglet mobile.
   * Ex : { etat: { label: "Victoire", badge: "?", pulse: true } }
   */
  tabMeta?: Partial<Record<OngletId, OngletMeta>>;

  /**
   * Optionnel : notifié quand l’onglet actif change (utile pour marquer "vu").
   */
  onTabChange?: (onglet: OngletId) => void;
  /** Optionnel : contrôle externe de l’onglet actif (mobile) */
  activeTab?: OngletId;

}

export const GameLayout: React.FC<GameLayoutProps> = ({
  header,
  bandeauTour,
  vueEtat,
  vueProgramme,
  vueActions,
  vueJournal,
  tabMeta,
  bottom,
  layoutMode = "auto",
  onTabChange,
  activeTab,
  indicateurGlobal,
}) => {
  const [activeTabState, setActiveTabState] = useState<OngletId>("programme");
  const active = activeTab ?? activeTabState;

  const [largeurFenetre, setLargeurFenetre] = useState<number>(() => {
    if (typeof window === "undefined") return 1024;
    return window.innerWidth;
  });

  // 🔍 largeur réelle : utile pour basculer en "mobile" si le desktop devient trop coincé
  useEffect(() => {
    if (typeof window === "undefined") return;
    const onResize = () => setLargeurFenetre(window.innerWidth);
    onResize();
    window.addEventListener("resize", onResize);
    return () => window.removeEventListener("resize", onResize);
  }, []);

  const useMobileLayout = useMemo(() => {
    if (layoutMode === "mobile") return true;
    if (layoutMode === "desktop") return false;
    // auto : mobile si trop étroit pour 3 colonnes sans ratatiner
    const SEUIL_AUTO_MOBILE = 1024; // on garde le desktop jusqu'à ~tablet landscape
    return largeurFenetre < SEUIL_AUTO_MOBILE;
  }, [layoutMode, largeurFenetre]);

  const renderMobileContent = () => {
    let contenu: React.ReactNode = null;

    switch (active) {
      case "etat":
        contenu = vueEtat ?? null;
        break;
      case "programme":
        contenu = vueProgramme ?? null;
        break;
      case "actions":
        contenu = vueActions ?? null;
        break;
      case "journal":
        contenu = vueJournal ?? null;
        break;
      default:
        contenu = null;
    }

    return (
      <div className="flex-1 overflow-hidden px-3 py-2 flex flex-col gap-2">
        {/* Bandeau sticky "prochaine étape" (optionnel) */}
        {bandeauTour ? (
          <div className="sticky top-0 z-30 border border-bleu-glacier bg-bleu-boreal/90 backdrop-blur rounded-card px-3 py-2">
            {bandeauTour}
          </div>
        ) : null}

        {/* barre d’onglets mobile */}
        <TabBar
          actif={active}
          onChange={(onglet) => {
            setActiveTabState(onglet);
            onTabChange?.(onglet);
          }}
          meta={tabMeta}
          mobile={true}
        />

        {/* panneau actif */}
        <div className="flex-1 overflow-y-auto mt-1">
          <div className="flex flex-col gap-3">{contenu}</div>
        </div>

        {bottom && <div className="mt-2">{bottom}</div>}
      </div>
    );
  };

  const renderDesktopContent = () => (
    <div className="flex-1 overflow-hidden px-3 py-2">
      <div className="grid gap-3 h-full grid-rows-[minmax(0,1fr)_auto]">
        {/* Desktop "normal" d'abord : 1 col < xl, 2 cols >= xl, 3 cols seulement >= 2xl */}
        <div
          className={[
            "grid gap-3 h-full",
            // base: 1 colonne (évite l'effet "super écran" sur laptop)
            "grid-cols-1",
            // xl: 2 colonnes (centre + journal). La victoire se stacke au-dessus du centre.
            "xl:grid-cols-[minmax(0,1fr)_minmax(320px,420px)]",
            // 2xl: 3 colonnes (victoire | centre | journal)
            "2xl:grid-cols-[minmax(320px,420px)_minmax(0,1fr)_minmax(320px,420px)]",
          ].join(" ")}
        >
          {/* Colonne gauche (2xl seulement) : état général */}
          <div className="hidden 2xl:flex flex-col gap-4 overflow-y-auto pr-1">
            {vueEtat}
          </div>

          {/* Colonne centrale : (en <2xl) inclut aussi la victoire en haut */}
          <div className="flex flex-col gap-4 overflow-hidden">
            <div className="2xl:hidden">
              {/* en desktop normal, on évite une colonne dédiée : on stacke l'état */}
              {vueEtat}
            </div>
            {vueProgramme}
            {vueActions}
          </div>

          {/* Colonne droite : journal (en base < xl, il passe sous le centre) */}
          <div className="flex flex-col gap-4 overflow-y-auto pr-1">
            {vueJournal}
          </div>
        </div>

        <div className="mt-1">{bottom}</div>
      </div>
    </div>
  );

  return (
    <div className="flex flex-col h-full w-full bg-bleu-boreal text-blanc-nordique">
      <header className="border-b border-bleu-glacier px-4 py-2 flex flex-col gap-2">
        {header}
        {indicateurGlobal ? (
          <div className="text-[12px] text-blanc-nordique/80">
            {indicateurGlobal}
          </div>
        ) : null}
      </header>

      {/* 🔁 branchement explicite mobile vs desktop */}
      {useMobileLayout ? renderMobileContent() : renderDesktopContent()}
    </div>
  );
};

export default GameLayout;

