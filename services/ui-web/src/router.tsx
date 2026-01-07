import React from "react";
import { Routes, Route, Navigate } from "react-router-dom";
import HomePage from "./pages/HomePage";
import AuthPage from "./pages/AuthPage";
import LobbyPage from "./pages/LobbyPage";
import TableWaitingPage from "./pages/TableWaitingPage";
import GamePage from "./pages/GamePage";

import AideJeuPage from "./pages/AideJeuPage";
import PrincipesPage from "./pages/PrincipesPage";
import AideProgrammePage from "./pages/AideProgrammePage";

const AppRoutes: React.FC = () => {
  return (
    <Routes>
      <Route path="/" element={<HomePage />} />

      <Route path="/aide" element={<AideJeuPage />} />
      <Route path="/aide/programme" element={<AideProgrammePage />} />
      <Route path="/principes" element={<PrincipesPage />} />

      <Route path="/auth" element={<AuthPage />} />
      <Route path="/lobby" element={<LobbyPage />} />
      <Route path="/tables/:tableId" element={<TableWaitingPage />} />
      <Route path="/parties/:partieId" element={<GamePage />} />

      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
};

export default AppRoutes;

