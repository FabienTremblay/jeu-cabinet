import { useEffect } from "react";
import { useNavigate } from "react-router-dom";

import { envoyerHeartbeatSession } from "../api/lobbyApi";
import { useSession } from "../context/SessionContext";
import type { ApiErreur } from "../api/apiClient";

const INTERVALLE_HEARTBEAT_MS = 15_000;

export function useSessionHeartbeat() {
  const { joueur, setJoueur } = useSession();
  const navigate = useNavigate();
  const idSession = joueur?.jeton_session ?? null;

  useEffect(() => {
    function forcerReconnexion() {
      setJoueur(null);
      navigate("/auth?mode=login", { replace: true });
    }

    window.addEventListener("cabinet:session-expiree", forcerReconnexion);

    if (!idSession) {
      return () => {
        window.removeEventListener("cabinet:session-expiree", forcerReconnexion);
      };
    }

    let annule = false;

    async function envoyer() {
      try {
        await envoyerHeartbeatSession(idSession);
      } catch (err) {
        const erreur = err as Partial<ApiErreur>;
        if (!annule && erreur.type === "auth") {
          forcerReconnexion();
        }
      }
    }

    void envoyer();
    const timer = window.setInterval(() => {
      void envoyer();
    }, INTERVALLE_HEARTBEAT_MS);

    return () => {
      annule = true;
      window.clearInterval(timer);
      window.removeEventListener("cabinet:session-expiree", forcerReconnexion);
    };
  }, [idSession, navigate, setJoueur]);
}
