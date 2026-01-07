import React, { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { useSession } from "../context/SessionContext";
import {
  listerTables,
  listerJoueursTable,
  joueurPret,
  lancerPartie
} from "../api/lobbyApi";
import type { ReponseListeJoueursTable } from "../types/lobby";
import Button from "../components/shared/Button";
import Loading from "../components/shared/Loading";
import { useSituationPolling } from "../hooks/useSituationPolling";
import { idCourt } from "../utils/idCourt";

function memoriserNomTablePourPartie(partieId: string, nomTable?: string | null) {
  const nom = (nomTable ?? "").trim();
  if (!partieId || !nom) return;
  try {
    localStorage.setItem(`cab.partie.nom_table:${partieId}`, nom);
  } catch {
    // pas bloquant
  }
}

const TableWaitingPage: React.FC = () => {
  const { tableId } = useParams<{ tableId: string }>();
  const { joueur } = useSession();
  const navigate = useNavigate();
  // On poll ui-etat-joueur pour savoir si on est passé en mode "partie"
  const { situation, marqueurs, ancrage } =
    useSituationPolling(joueur?.id_joueur, { intervalMs: 2000 });


  const [etatTable, setEtatTable] = useState<ReponseListeJoueursTable | null>(null);
  const [nomTable, setNomTable] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [erreur, setErreur] = useState<string | null>(null);
  const [lancementEnCours, setLancementEnCours] = useState(false);

  useEffect(() => {
    if (!joueur) {
      navigate("/auth");
      return;
    }
    if (!tableId) return;

    async function charger() {
      try {
        setLoading(true);
        setErreur(null);
        // joueurs à la table
        const data = await listerJoueursTable(tableId);
        setEtatTable(data);

        // nom de la table (source: /api/tables)
        try {
          const tables = await listerTables();
          const t = tables.find((x) => x.id_table === tableId);
          setNomTable(t?.nom_table ?? null);
        } catch {
          // pas bloquant (fallback idCourt)
          setNomTable(null);
        }
      } catch (err) {
        setErreur((err as Error).message);
      } finally {
        setLoading(false);
      }
    }

    charger();
    const interval = setInterval(charger, 3000);
    return () => clearInterval(interval);
  }, [joueur, tableId, navigate]);

  // Quand ui-etat-joueur indique que la partie est lancée pour ce joueur,
  // on bascule automatiquement vers la page de jeu.
  useEffect(() => {
    if (!situation) return;

    // 1) Si l’ancrage indique déjà une partie, on redirige
    if (ancrage?.type === "partie" && ancrage.partie_id) {
      memoriserNomTablePourPartie(ancrage.partie_id, nomTable);
      navigate(`/parties/${ancrage.partie_id}`);
      return;
    }

    // 2) Sinon on se base sur les marqueurs "en_partie"
    if (marqueurs.en_partie && ancrage?.partie_id) {
      memoriserNomTablePourPartie(ancrage.partie_id, nomTable);
      navigate(`/parties/${ancrage.partie_id}`);
      return;
    }

    // 3) ui-état demande un retour au lobby (fin de partie ou dissolution)
    if (marqueurs.retour_lobby) {
      navigate("/lobby");
      return;
    }
  }, [situation, marqueurs, ancrage, navigate, nomTable]);


  if (!joueur || !tableId) return null;

  if (loading || !etatTable) {
    return <Loading message="Chargement de la table…" />;
  }

  const moi = etatTable.joueurs.find((j) => j.id_joueur === joueur.id_joueur);
  const estHote = moi?.role === "hote";
  const tousPrets =
    etatTable.joueurs.length > 0 &&
    etatTable.joueurs.every((j) => j.pret === true);

  async function handlePret() {
    try {
      await joueurPret({ id_table: tableId, id_joueur: joueur.id_joueur });
      const data = await listerJoueursTable(tableId);
      setEtatTable(data);
    } catch (err) {
      setErreur((err as Error).message);
    }
  }

  async function handleLancer() {
    if (!estHote) return;
    setLancementEnCours(true);
    try {
      const resp = await lancerPartie({
        id_table: tableId,
        id_hote: joueur.id_joueur
      });
      memoriserNomTablePourPartie(resp.id_partie, nomTable);
      navigate(`/parties/${resp.id_partie}`);
    } catch (err) {
      setErreur((err as Error).message);
      setLancementEnCours(false);
    }
  }

  return (
    <div className="space-y-4">
      <h2 className="text-xl font-semibold">
        {nomTable ?? `table ${idCourt(etatTable.id_table)}`}
      </h2>
      <p className="text-sm opacity-80">
        En attente des joueurs. Quand tout le monde est prêt, l’hôte peut lancer
        la partie.
      </p>

      <div className="border border-slate-800 rounded p-3 space-y-2">
        <h3 className="font-semibold text-sm">Joueurs</h3>
        <ul className="space-y-1 text-sm">
          {etatTable.joueurs.map((j) => (
            <li
              key={j.id_joueur}
              className="flex items-center justify-between border border-slate-800 rounded px-2 py-1"
            >
              <div>
                <div className="font-medium">
                  {j.alias ?? j.nom ?? idCourt(j.id_joueur)} ({j.role})
                  {j.id_joueur === joueur.id_joueur && " · vous"}
                </div>
                <div className="text-xs opacity-70">{j.courriel}</div>
              </div>
              <span className="text-xs">
                {j.pret ? "✅ prêt" : "⏳ en attente"}
              </span>
            </li>
          ))}
        </ul>
      </div>

      <div className="flex gap-3">
        <Button onClick={handlePret} disabled={moi?.pret}>
          {moi?.pret ? "Vous êtes prêt" : "Je suis prêt"}
        </Button>

        {estHote && (
          <Button
            variant="secondary"
            onClick={handleLancer}
            disabled={!tousPrets || lancementEnCours}
          >
            {lancementEnCours ? "Lancement…" : "Lancer la partie"}
          </Button>
        )}
      </div>

      {erreur && <p className="text-sm text-red-400">{erreur}</p>}
    </div>
  );
};

export default TableWaitingPage;
