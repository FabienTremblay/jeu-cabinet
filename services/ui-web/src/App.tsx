// src/App.tsx
import React from "react";
import { BrowserRouter } from "react-router-dom";
import PageLayout from "./components/layout/PageLayout";
import AppRoutes from "./router";
import { useSessionHeartbeat } from "./hooks/useSessionHeartbeat";

const SessionHeartbeat: React.FC = () => {
  useSessionHeartbeat();
  return null;
};

/**
 * Racine de l'application : met en place le router et le layout global.
 */
const App: React.FC = () => {
  return (
    <BrowserRouter>
      <SessionHeartbeat />
      <PageLayout>
        <AppRoutes />
      </PageLayout>
    </BrowserRouter>
  );
};

export default App;
