import React from "react";
import { useNavigate, useLocation } from "react-router-dom";
import Button from "../shared/Button";

const PageLayout: React.FC<React.PropsWithChildren> = ({ children }) => {
  const navigate = useNavigate();
  const location = useLocation();

  const onAide = location.pathname.startsWith("/aide");
  const onPrincipes = location.pathname.startsWith("/principes");

  return (
    <div className="min-h-screen bg-bleu-boreal text-blanc-nordique">
      {/* barre globale : accès constant */}
      <div className="sticky top-0 z-50 border-b border-slate-700/60 bg-slate-950/70 backdrop-blur">
        <div className="px-4 py-2 flex items-center justify-between gap-2">
          <Button
            variant="ghost"
            size="sm"
            onClick={() => navigate("/")}
            aria-label="Accueil"
          >
            accueil
          </Button>

          <div className="flex items-center gap-2">
            <Button
              variant={onAide ? "secondary" : "ghost"}
              size="sm"
              onClick={() => navigate("/aide")}
            >
              aide
            </Button>
            <Button
              variant={onPrincipes ? "secondary" : "ghost"}
              size="sm"
              onClick={() => navigate("/principes")}
            >
              principes
            </Button>
          </div>
        </div>
      </div>

      <main className="px-4 py-4">{children}</main>
    </div>
  );
};

export default PageLayout;

