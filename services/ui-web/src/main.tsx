// src/main.tsx
import React from "react";
import { createRoot } from "react-dom/client";
import App from "./App";
import "./index.css";
import { SessionProvider } from "./context/SessionContext";

const container = document.getElementById("root");

if (container) {
  const root = createRoot(container);
  root.render(
    <React.StrictMode>
      <SessionProvider>
        <App />
      </SessionProvider>
    </React.StrictMode>
  );
}

