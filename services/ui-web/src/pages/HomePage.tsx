// src/pages/HomePage.tsx
import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useSession } from "../context/SessionContext";
import { lireSituationJoueur } from "../api/uiEtatJoueur";
import Button from "../components/shared/Button";

export function HomePage() {
  const { joueur } = useSession();
  const navigate = useNavigate();
  const [checking, setChecking] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // pas de joueur → simple accueil
    if (!joueur) return;

    let cancelled = false;
    setChecking(true);
    setError(null);

    lireSituationJoueur(joueur.id_joueur)
      .then((situation) => {
        if (cancelled) return;

        // même logique que dans AuthPage.tsx
        const brutAncrage =
          (situation as any).ancrage ??
          (situation as any).ancrage_courant ??
          {};
        const type = brutAncrage.type;

        const partieId =
          brutAncrage.partie_id ??
          brutAncrage.id_partie ??
          brutAncrage.partie ??
          null;

        const tableId =
          brutAncrage.table_id ??
          brutAncrage.id_table ??
          brutAncrage.table ??
          null;

        if (type === "partie" && partieId) {
          navigate(`/parties/${partieId}`);
        } else if (type === "table" && tableId) {
          navigate(`/tables/${tableId}`);
        } else {
          navigate("/lobby");
        }
      })
      .catch((err) => {
        if (cancelled) return;
        console.error("erreur situation joueur", err);
        setError("impossible de récupérer votre situation de jeu.");
      })
      .finally(() => {
        if (cancelled) return;
        setChecking(false);
      });

    return () => {
      cancelled = true;
    };
  }, [joueur, navigate]);

  // cas 1 : pas de joueur → accueil
  if (!joueur) {
    return (
      <div className="page page-home">
        <main className="home-main home-hero">
          <h1 className="home-titre">conseil des ministres</h1>

          <div className="home-intro">
            <p>bienvenue au cabinet : l’endroit où les bonnes intentions meurent de surcharge.</p>

            <p>
              votre monnaie, c’est <strong>l’attention</strong>. votre carburant,
              c’est le <strong>capital politique</strong>. votre fardeau, c’est le{" "}
              <strong>programme</strong>.
            </p>

            <p>
              entre les coups de coude internes et les crises qui tombent sans prévenir,{" "}
              <strong>l’opposition</strong> n’a pas besoin d’être brillante : elle doit juste
              vous regarder trébucher.
            </p>

            <p>
              faites passer des mesures. gardez la coalition en vie. et si possible… évitez
              de devenir le bouc émissaire du jour.
            </p>
          </div>

          <div className="home-actions">
            <Button onClick={() => navigate("/auth")}>
              me connecter
            </Button>

            <Button
              variant="secondary"
              onClick={() => navigate("/auth?mode=signup")}
            >
              m’inscrire
            </Button>

            <Button
              variant="ghost"
              onClick={() => navigate("/aide")}
            >
              comprendre le jeu
            </Button>
          </div>

        </main>
      </div>
    );
  }

  // cas 2 : joueur connu, on vérifie sa situation
  return (
    <div className="page page-home">
      <main className="home-main">
        <p>bonjour, {joueur.alias}.</p>
        {checking && <p>on retrouve votre partie en cours…</p>}
        {error && (
          <>
            <p>{error}</p>
            <div className="home-actions">
              <Button onClick={() => navigate("/lobby")}>aller au lobby</Button>
              <button
                type="button"
                className="home-lien-aide"
                onClick={() => navigate("/aide")}
              >
                comprendre le jeu
              </button>
            </div>
          </>
        )}
      </main>
    </div>
  );
}

export default HomePage;

