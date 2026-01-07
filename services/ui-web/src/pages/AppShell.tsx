// src/pages/AppShell.tsx
import React from "react";
import { useNavigate } from "react-router-dom";
import { useSession } from "../context/SessionContext";
import { useSituationPolling } from "../hooks/useSituationPolling";
import type { SituationUI } from "../types/uiEtat";

import LobbyPage from "./LobbyPage";
import TableWaitingPage from "./TableWaitingPage";
import GamePage from "./GamePage";
import Loading from "../components/shared/Loading";

function resolveRouteFromAncrage(situation: SituationUI) {
  const type = situation.ancrage?.type ?? null;
  const tableId = situation.ancrage?.table_id ?? null;
  const partieId = situation.ancrage?.partie_id ?? null;

  if (type === "lobby" || type === null) {
    return { kind: "lobby" as const };
  }
  if (type === "table" && tableId) {
    return { kind: "table" as const, tableId };
  }
  if (type === "partie" && partieId) {
    return { kind: "partie" as const, partieId };
  }

  // fallback ultra défensif
  return { kind: "lobby" as const };
}

const AppShell: React.FC = () => {
  const { session } = useSession(); // à adapter si ta session a un autre nom
  const navigate = useNavigate();

  const joueurId = session?.joueur?.id ?? null;
  const { situation, loading, error } = useSituationPolling(joueurId);

  // Pas de joueur → retour vers la page d’auth
  React.useEffect(() => {
    if (!joueurId) {
      navigate("/auth");
    }
  }, [joueurId, navigate]);

  if (!joueurId) {
    return <div>Veuillez vous connecter…</div>;
  }

  if (loading && !situation) {
    return <Loading text="Chargement de ta situation…" />;
  }

  if (error && !situation) {
    return (
      <div>
        Erreur de chargement de la situation UI.
        <pre>{error.message}</pre>
      </div>
    );
  }

  if (!situation) {
    return <div>Situation UI indisponible pour l’instant…</div>;
  }

  const route = resolveRouteFromAncrage(situation);

  // Tu peux passer `situation` en props pour afficher journal / actions.
  switch (route.kind) {
    case "lobby":
      return <LobbyPage />;

    case "table":
      return <TableWaitingPage tableId={route.tableId} />;

    case "partie":
      // GamePage peut, en plus, appeler /parties/{id}/etat comme prévu
      return <GamePage partieId={route.partieId} uiSituation={situation} />;

    default:
      return <LobbyPage />;
  }
};

export default AppShell;
