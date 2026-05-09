// src/pages/AuthPage.tsx
import React, { useEffect, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";

import Button from "../components/shared/Button";
import { inscription, connexion } from "../api/lobbyApi";
import { useSession } from "../context/SessionContext";
import { resoudreDestinationJoueur } from "../utils/navigationJoueur";

const AuthPage: React.FC = () => {
  const location = useLocation();

  const modeInit: "login" | "signup" = (() => {
    const params = new URLSearchParams(location.search);
    const m = params.get("mode");
    return m === "signup" ? "signup" : "login";
  })();

  const [mode, setMode] = useState<"login" | "signup">(modeInit);
  const [nom, setNom] = useState("");
  const [alias, setAlias] = useState("");
  const [courriel, setCourriel] = useState("");
  const [motDePasse, setMotDePasse] = useState("");
  const [loading, setLoading] = useState(false);
  const [erreur, setErreur] = useState<string | null>(null);

  const { setJoueur } = useSession();
  const navigate = useNavigate();

  
  useEffect(() => {
    const params = new URLSearchParams(location.search);
    const m = params.get("mode");

    if (m === "signup") {
      setMode("signup");
      setErreur(null);
    } else if (m === "login") {
      setMode("login");
      setErreur(null);
    }
  }, [location.search]);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setErreur(null);
    setLoading(true);

    try {
      let joueur;

      if (mode === "signup") {
        // --- Création d’un nouveau joueur ---
        joueur = await inscription({
          nom,
          alias,
          courriel,
          mot_de_passe: motDePasse,
        });
      } else {
        // --- Connexion d’un joueur existant ---
        joueur = await connexion({
          courriel,
          mot_de_passe: motDePasse,
        });
      }

      // 1) On mémorise la session côté front (dans sessionStorage via le contexte)
      setJoueur(joueur);

      const destination = await resoudreDestinationJoueur(joueur.id_joueur);
      navigate(destination);

    } catch (err) {
      const msg =
        (err as Error).message || "Erreur lors de l’authentification.";

      if (
        mode === "login" &&
        msg.toLowerCase().includes("inconnu")
      ) {
        // Bascule automatique en mode inscription
        setMode("signup");
        setErreur(
          "Ce joueur n’existe pas encore. Complète les champs Nom / Alias puis clique sur « Créer mon compte »."
        );
      } else {
        setErreur(msg);
      }
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="max-w-md space-y-4">
      {/* Toggle Connexion / Inscription */}
      <div className="flex gap-2 text-sm">
        <button
          type="button"
          className={`px-2 py-1 rounded ${
            mode === "login"
              ? "bg-emerald-600 text-white"
              : "bg-slate-800 text-slate-100"
          }`}
          onClick={() => {
            setMode("login");
            setErreur(null);
          }}
        >
          Connexion
        </button>
        <button
          type="button"
          className={`px-2 py-1 rounded ${
            mode === "signup"
              ? "bg-emerald-600 text-white"
              : "bg-slate-800 text-slate-100"
          }`}
          onClick={() => {
            setMode("signup");
            setErreur(null);
          }}
        >
          Inscription
        </button>
      </div>

      <h2 className="text-xl font-semibold">
        {mode === "signup" ? "Créer un compte" : "Se connecter"}
      </h2>

      <form onSubmit={handleSubmit} className="space-y-3 text-sm">
        {mode === "signup" && (
          <>
            <div className="space-y-1">
              <label>Nom complet</label>
              <input
                className="w-full rounded border border-slate-700 bg-slate-900 px-2 py-1"
                value={nom}
                onChange={(e) => setNom(e.target.value)}
                required
              />
            </div>
            <div className="space-y-1">
              <label>Alias</label>
              <input
                className="w-full rounded border border-slate-700 bg-slate-900 px-2 py-1"
                value={alias}
                onChange={(e) => setAlias(e.target.value)}
                required
              />
            </div>
          </>
        )}

        <div className="space-y-1">
          <label>Courriel</label>
          <input
            type="email"
            className="w-full rounded border border-slate-700 bg-slate-900 px-2 py-1"
            value={courriel}
            onChange={(e) => setCourriel(e.target.value)}
            required
          />
        </div>

        <div className="space-y-1">
          <label>Mot de passe</label>
          <input
            type="password"
            className="w-full rounded border border-slate-700 bg-slate-900 px-2 py-1"
            value={motDePasse}
            onChange={(e) => setMotDePasse(e.target.value)}
            required
          />
        </div>

        {erreur && <p className="text-red-400">{erreur}</p>}

        <Button type="submit" disabled={loading}>
          {loading
            ? mode === "signup"
              ? "Création en cours…"
              : "Connexion en cours…"
            : mode === "signup"
            ? "Créer mon compte"
            : "Se connecter"}
        </Button>
      </form>
    </div>
  );
};

export default AuthPage;
