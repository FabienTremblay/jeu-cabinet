// src/pages/LobbyPage.tsx
import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  listerTables,
  creerTable,
  listerSkins,
  joindreTable,
  listerJoueursLobby,
} from "../api/lobbyApi";
import type { TableInfo, SkinInfo, ReponseListeJoueursLobby } from "../types/lobby";
import { useSession } from "../context/SessionContext";
import Button from "../components/shared/Button";
import Loading from "../components/shared/Loading";
import { useSituationPolling } from "../hooks/useSituationPolling";

const LobbyPage: React.FC = () => {
  // 👉 ici : on récupère bien `joueur`, pas `session`
  const { joueur } = useSession();
  const navigate = useNavigate();
  const { ancrage, marqueurs } = useSituationPolling(
    joueur ? joueur.id_joueur : null,
    { intervalMs: 5000 }
  );
  const [tables, setTables] = useState<TableInfo[]>([]);
  const [skins, setSkins] = useState<SkinInfo[]>([]);
  const [skinChoisi, setSkinChoisi] = useState<string | null>(null);

  const [nomTable, setNomTable] = useState("");
  const [nbSieges, setNbSieges] = useState(3);
  const [creating, setCreating] = useState(false);
  const [loading, setLoading] = useState(true);
  const [erreur, setErreur] = useState<string | null>(null);
  const [joueursLobby, setJoueursLobby] = useState<
    ReponseListeJoueursLobby["joueurs"]
  >([]);

  // Rafraîchissement régulier des tables ouvertes (et des joueurs présents au lobby)
  useEffect(() => {
    if (!joueur) return;

    let cancelled = false;

    const refreshLobbyLight = async () => {
      try {
        const [tablesRes, joueursRes]: [TableInfo[], ReponseListeJoueursLobby] =
          await Promise.all([
            listerTables("ouverte"),
            listerJoueursLobby(),
          ]);

        if (cancelled) return;

        setTables(tablesRes);
        setJoueursLobby(joueursRes.joueurs);
      } catch (err) {
        // on log juste, on ne touche pas à l'état d'erreur global
        console.warn("Erreur lors du rafraîchissement du lobby :", err);
      }
    };

    const id = window.setInterval(refreshLobbyLight, 4000); // toutes les 4 s, par ex.

    // premier tir immédiat pour ne pas attendre 4 s
    refreshLobbyLight();

    return () => {
      cancelled = true;
      window.clearInterval(id);
    };
  }, [joueur]);

  useEffect(() => {
    // Si aucun joueur en session, on ne tente pas de charger les données
    if (!joueur) {
      return;
    }

    async function charger() {
      try {
        setLoading(true);
        setErreur(null);

        const [tablesRes, skinsRes, joueursRes] = await Promise.all([
          listerTables("ouverte"),
          listerSkins(),
          listerJoueursLobby(),
        ]);

        setTables(tablesRes);
        setSkins(skinsRes);
        setJoueursLobby(joueursRes.joueurs);

        // skin par défaut : premier de la liste, si présent
        if (skinsRes.length > 0 && !skinChoisi) {
          setSkinChoisi(skinsRes[0].id_skin);
        }
      } catch (err) {
        setErreur((err as Error).message);
      } finally {
        setLoading(false);
      }
    }

    charger();
  }, [joueur, skinChoisi, marqueurs?.retour_lobby]);

  useEffect(() => {
    if (!joueur) return;
    if (!ancrage) return;

    const type = (ancrage as any).type;
    const tableId =
      (ancrage as any).table_id ??
      (ancrage as any).id_table ??
      (ancrage as any).table ??
      null;
    const partieId =
      (ancrage as any).partie_id ??
      (ancrage as any).id_partie ??
      (ancrage as any).partie ??
      null;

    if (type === "table" && tableId) {
      navigate(`/tables/${tableId}`);
    } else if (type === "partie" && partieId) {
      navigate(`/parties/${partieId}`);
    }
  }, [joueur, ancrage, navigate]);

  // Si pas de joueur chargé, on affiche un message plutôt que de boucler
  if (!joueur) {
    return (
      <div className="space-y-2">
        <p>Vous devez être connecté pour accéder au lobby.</p>
        <Button onClick={() => navigate("/auth")}>
          Aller à la page de connexion
        </Button>
      </div>
    );
  }

  const handleCreateTable = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!nomTable.trim()) return;

    try {
      setCreating(true);
      setErreur(null);

      const table = await creerTable({
        id_hote: joueur.id_joueur,
        nom_table: nomTable.trim(),
        nb_sieges: nbSieges,
        skin_jeu: skinChoisi ?? null,
      });

      // redirection vers la vue détail de la table
      navigate(`/tables/${table.id_table}`);
    } catch (err) {
      setErreur((err as Error).message);
    } finally {
      setCreating(false);
    }
  };

  // 👉 IMPORTANT : cette fonction est maintenant DANS le composant,
  // donc elle voit `joueur`, `navigate` et `setErreur`.
  const handleJoinTable = async (tableId: string) => {
    try {
      setErreur(null);

      await joindreTable({
        id_table: tableId,
        id_joueur: joueur.id_joueur,
        role: "invite",
      });

      // Option simple : on va directement sur la page de la table
      navigate(`/tables/${tableId}`);
    } catch (err) {
      setErreur((err as Error).message);
    }
  };

  if (loading) {
    return <Loading label="Chargement du lobby…" />;
  }

  return (
    <div className="space-y-4 text-sm">
      <h2 className="text-xl font-semibold">Lobby</h2>

      <p className="text-xs opacity-80">
        Bienvenue, <span className="font-semibold">{joueur.alias ?? joueur.nom}</span>.{" "}
        Depuis ce lobby, tu peux créer une table ou rejoindre une table en
        préparation.
      </p>
      {/* Joueurs présents dans le lobby */}
      <section className="border border-slate-800 rounded p-3">
        <h3 className="font-semibold mb-2">Joueurs présents</h3>
        {joueursLobby.length === 0 ? (
          <p className="text-xs opacity-70">
            Aucun autre joueur dans le lobby pour l’instant.
          </p>
        ) : (
          <ul className="space-y-1 text-xs">
            {joueursLobby.map((j) => (
              <li key={j.id_joueur}>
                {j.alias ?? j.nom ?? idCourt(j.id_joueur)}
              </li>
            ))}
          </ul>
        )}
      </section>

      {/* Création de table */}
      <section className="border border-slate-800 rounded p-3">
        <h3 className="font-semibold mb-2">Créer une table</h3>

        {skins.length === 0 ? (
          <p className="text-xs opacity-70">
            Aucun skin de jeu n’est disponible pour l’instant.
          </p>
        ) : (
          <form onSubmit={handleCreateTable} className="space-y-2 text-xs">
            <div className="flex flex-col gap-1">
              <label className="text-xs opacity-80">Nom de la table</label>
              <input
                className="bg-slate-900 border border-slate-700 rounded px-2 py-1 text-xs"
                value={nomTable}
                onChange={(e) => setNomTable(e.target.value)}
                placeholder="Ex. Première partie de test"
              />
            </div>

            <div className="flex flex-col gap-1">
              <label className="text-xs opacity-80">Nombre de sièges</label>
              <input
                type="number"
                min={2}
                max={6}
                className="bg-slate-900 border border-slate-700 rounded px-2 py-1 text-xs"
                value={nbSieges}
                onChange={(e) => setNbSieges(Number(e.target.value))}
              />
            </div>

            <div className="flex flex-col gap-1">
              <label className="text-xs opacity-80">Skin de jeu</label>
              <select
                className="bg-slate-900 border border-slate-700 rounded px-2 py-1 text-xs"
                value={skinChoisi ?? ""}
                onChange={(e) => setSkinChoisi(e.target.value || null)}
              >
                {skins.map((s) => (
                  <option key={s.id_skin} value={s.id_skin}>
                    {s.nom}
                  </option>
                ))}
              </select>
            </div>

            <div className="pt-2">
              <Button
                type="submit"
                disabled={creating || !nomTable.trim() || skins.length === 0}
              >
                {creating ? "Création…" : "Créer la table"}
              </Button>
            </div>
          </form>
        )}
      </section>

      {/* Tables en préparation */}
      <section className="border border-slate-800 rounded p-3">
        <h3 className="font-semibold mb-2">Tables en préparation</h3>
        {tables.length === 0 ? (
          <p className="text-xs opacity-70">
            Aucune table en préparation pour l’instant.
          </p>
        ) : (
          <ul className="space-y-1 text-xs">
            {tables.map((t) => (
              <li
                key={t.id_table}
                className="flex justify-between items-center border border-slate-800 rounded px-2 py-1"
              >
                <div>
                  <div className="font-medium">{t.nom_table}</div>
                  <div className="opacity-70">
                    · sièges : {t.nb_sieges} · statut :{" "}
                    {t.statut}
                    {t.skin_jeu && ` · skin : ${t.skin_jeu}`}
                  </div>
                </div>
                <Button
                  size="sm"
                  variant="secondary"
                  onClick={() => handleJoinTable(t.id_table)}
                >
                  Rejoindre
                </Button>
              </li>
            ))}
          </ul>
        )}
      </section>

      {erreur && (
        <p className="text-xs text-red-400">
          Erreur : {erreur}
        </p>
      )}
    </div>
  );
};

export default LobbyPage;

