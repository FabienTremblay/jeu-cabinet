import React, { useEffect, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import { useSession } from "../context/SessionContext";
import {
  listerTables,
  listerJoueursTable,
  joueurPret,
  lancerPartie,
  modifierConfigurationTable
} from "../api/lobbyApi";
import type { ReponseListeJoueursTable, ReponseTable } from "../types/lobby";
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

type UniteDelaiTimeout = "minutes" | "heures";

function formatterDelaiTimeout(secondes: number): string {
  if (secondes >= 3600 && secondes % 3600 === 0) {
    const heures = secondes / 3600;
    return `${heures} heure${heures > 1 ? "s" : ""}`;
  }

  const minutes = Math.max(1, Math.round(secondes / 60));
  return `${minutes} minute${minutes > 1 ? "s" : ""}`;
}

function delaiVersEdition(secondes: number): {
  valeur: number;
  unite: UniteDelaiTimeout;
} {
  if (secondes >= 3600 && secondes % 3600 === 0) {
    return { valeur: secondes / 3600, unite: "heures" };
  }
  return { valeur: Math.max(1, Math.round(secondes / 60)), unite: "minutes" };
}

function delaiEditionVersSecondes(valeur: number, unite: UniteDelaiTimeout): number {
  const entier = Math.max(1, Math.floor(Number.isFinite(valeur) ? valeur : 1));
  return unite === "heures" ? entier * 3600 : entier * 60;
}

function etatsTableIdentiques(
  gauche: ReponseListeJoueursTable | null,
  droite: ReponseListeJoueursTable
): boolean {
  if (!gauche || gauche.id_table !== droite.id_table) return false;
  if (gauche.joueurs.length !== droite.joueurs.length) return false;

  return gauche.joueurs.every((joueur, index) => {
    const autre = droite.joueurs[index];
    return (
      autre &&
      joueur.id_joueur === autre.id_joueur &&
      joueur.alias === autre.alias &&
      joueur.nom === autre.nom &&
      joueur.courriel === autre.courriel &&
      joueur.pret === autre.pret &&
      joueur.role === autre.role
    );
  });
}

function tablesIdentiques(
  gauche: ReponseTable | null,
  droite: ReponseTable | null
): boolean {
  if (!gauche || !droite) return gauche === droite;
  return (
    gauche.id_table === droite.id_table &&
    gauche.nom_table === droite.nom_table &&
    gauche.nb_sieges === droite.nb_sieges &&
    gauche.id_hote === droite.id_hote &&
    gauche.statut === droite.statut &&
    gauche.skin_jeu === droite.skin_jeu &&
    gauche.politique_timeout_partie?.version ===
      droite.politique_timeout_partie?.version &&
    gauche.politique_timeout_partie?.active ===
      droite.politique_timeout_partie?.active &&
    gauche.politique_timeout_partie?.delai_inactivite_secondes ===
      droite.politique_timeout_partie?.delai_inactivite_secondes
  );
}

const TableWaitingPage: React.FC = () => {
  const { tableId } = useParams<{ tableId: string }>();
  const { joueur } = useSession();
  const navigate = useNavigate();
  // On poll ui-etat-joueur pour savoir si on est passé en mode "partie"
  const { situation, marqueurs, ancrage } =
    useSituationPolling(joueur?.id_joueur ?? null, { intervalMs: 2000 });


  const [etatTable, setEtatTable] = useState<ReponseListeJoueursTable | null>(null);
  const [table, setTable] = useState<ReponseTable | null>(null);
  const [loading, setLoading] = useState(true);
  const [erreur, setErreur] = useState<string | null>(null);
  const [lancementEnCours, setLancementEnCours] = useState(false);
  const [timeoutActif, setTimeoutActif] = useState(true);
  const [delaiTimeoutValeur, setDelaiTimeoutValeur] = useState(60);
  const [delaiTimeoutUnite, setDelaiTimeoutUnite] =
    useState<UniteDelaiTimeout>("minutes");
  const [editionTimeoutDirty, setEditionTimeoutDirty] = useState(false);
  const [sauvegardeTimeoutEnCours, setSauvegardeTimeoutEnCours] = useState(false);
  const [messageTimeout, setMessageTimeout] = useState<string | null>(null);

  useEffect(() => {
    if (!joueur) {
      navigate("/auth");
      return;
    }
    if (!tableId) return;
    const idTableCourante = tableId;

    async function charger(chargementInitial = false) {
      try {
        if (chargementInitial) {
          setLoading(true);
        }
        // joueurs à la table
        const data = await listerJoueursTable(idTableCourante);
        setEtatTable((etatCourant) =>
          etatsTableIdentiques(etatCourant, data) ? etatCourant : data
        );

        // nom de la table (source: /api/tables)
        try {
          const tables = await listerTables();
          const t = tables.find((x) => x.id_table === idTableCourante);
          setTable((tableCourante) =>
            tablesIdentiques(tableCourante, t ?? null) ? tableCourante : t ?? null
          );
          setErreur(null);
        } catch {
          // pas bloquant : on conserve la dernière table connue pour éviter
          // de masquer le bloc timeout pendant un incident de polling.
          setErreur("Rafraîchissement de la table incomplet. Dernières données conservées.");
        }
      } catch (err) {
        setErreur((err as Error).message);
      } finally {
        if (chargementInitial) {
          setLoading(false);
        }
      }
    }

    charger(true);
    const interval = setInterval(() => charger(false), 3000);
    return () => clearInterval(interval);
  }, [joueur, tableId, navigate]);

  useEffect(() => {
    setEditionTimeoutDirty(false);
  }, [tableId]);

  useEffect(() => {
    const politique = table?.politique_timeout_partie;
    if (editionTimeoutDirty) return;
    if (!politique) return;

    const edition = delaiVersEdition(politique.delai_inactivite_secondes);
    setTimeoutActif(politique.active);
    setDelaiTimeoutValeur(edition.valeur);
    setDelaiTimeoutUnite(edition.unite);
  }, [
    editionTimeoutDirty,
    table?.politique_timeout_partie.active,
    table?.politique_timeout_partie.delai_inactivite_secondes,
  ]);

  // Quand ui-etat-joueur indique que la partie est lancée pour ce joueur,
  // on bascule automatiquement vers la page de jeu.
  useEffect(() => {
    if (!situation) return;

    // 1) Si l’ancrage indique déjà une partie, on redirige
    if (ancrage?.type === "partie" && ancrage.partie_id) {
      memoriserNomTablePourPartie(ancrage.partie_id, table?.nom_table);
      navigate(`/parties/${ancrage.partie_id}`);
      return;
    }

    // 2) Sinon on se base sur les marqueurs "en_partie"
    if (marqueurs.en_partie && ancrage?.partie_id) {
      memoriserNomTablePourPartie(ancrage.partie_id, table?.nom_table);
      navigate(`/parties/${ancrage.partie_id}`);
      return;
    }

    // 3) ui-état demande un retour au lobby (fin de partie ou dissolution)
    if (marqueurs.retour_lobby) {
      navigate("/lobby");
      return;
    }
  }, [situation, marqueurs, ancrage, navigate, table?.nom_table]);


  if (!joueur || !tableId) return null;

  const idTable = tableId;
  const idJoueur = joueur.id_joueur;

  if (!etatTable || loading) {
    return <Loading message="Chargement de la table…" />;
  }

  const moi = etatTable.joueurs.find((j) => j.id_joueur === joueur.id_joueur);
  const estHote = moi?.role === "hote";
  const configurationModifiable =
    estHote && (table?.statut === "ouverte" || table?.statut === "en_preparation");
  const politiqueTimeout = table?.politique_timeout_partie ?? null;
  const tousPrets =
    etatTable.joueurs.length > 0 &&
    etatTable.joueurs.every((j) => j.pret === true);

  async function handlePret() {
    try {
      await joueurPret({ id_table: idTable, id_joueur: idJoueur });
      const data = await listerJoueursTable(idTable);
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
        id_table: idTable,
        id_hote: idJoueur
      });
      memoriserNomTablePourPartie(resp.id_partie, table?.nom_table);
      navigate(`/parties/${resp.id_partie}`);
    } catch (err) {
      setErreur((err as Error).message);
      setLancementEnCours(false);
    }
  }

  async function handleSauvegarderTimeout() {
    if (!table || !configurationModifiable) return;

    setSauvegardeTimeoutEnCours(true);
    setMessageTimeout(null);
    setErreur(null);

    try {
      const delaiSecondes = delaiEditionVersSecondes(
        delaiTimeoutValeur,
        delaiTimeoutUnite
      );
      const tableModifiee = await modifierConfigurationTable({
        id_table: table.id_table,
        id_hote: idJoueur,
        politique_timeout_partie: {
          active: timeoutActif,
          delai_inactivite_secondes: delaiSecondes,
        },
      });
      setTable(tableModifiee);
      setEditionTimeoutDirty(false);
      setMessageTimeout("Paramètres de timeout enregistrés.");
    } catch (err) {
      const message =
        err instanceof Error ? err.message : "sauvegarde_timeout_impossible";
      setMessageTimeout(null);
      setErreur(message);
    } finally {
      setSauvegardeTimeoutEnCours(false);
    }
  }

  return (
    <div className="space-y-4">
      <h2 className="text-xl font-semibold">
        {table?.nom_table ?? `table ${idCourt(etatTable.id_table)}`}
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

      {politiqueTimeout && (
        <div className="border border-slate-800 rounded p-3 space-y-3">
          <div className="flex flex-col gap-1 sm:flex-row sm:items-start sm:justify-between">
            <div>
              <h3 className="font-semibold text-sm">Timeout d’inactivité</h3>
              <p className="text-xs opacity-75">
                S’applique au lancement de la partie. Une fois lancée, la
                configuration n’est plus modifiable.
              </p>
            </div>
            <Link
              to={`/aide?retour=${encodeURIComponent(`/tables/${idTable}`)}#timeout-partie`}
              className="text-xs text-bleuGlacier hover:underline"
            >
              aide sur le timeout
            </Link>
          </div>

          <div className="text-sm">
            <span className="font-medium">
              {politiqueTimeout.active ? "Actif" : "Désactivé"}
            </span>
            <span className="opacity-75">
              {" "}
              · délai :{" "}
              {formatterDelaiTimeout(
                politiqueTimeout.delai_inactivite_secondes
              )}
            </span>
          </div>

          {!estHote && (
            <p className="text-xs opacity-70">
              Seul l’hôte peut modifier ce réglage.
            </p>
          )}

          {estHote && !configurationModifiable && (
            <p className="text-xs opacity-70">
              La configuration est verrouillée pour cette table.
            </p>
          )}

          {estHote && (
            <fieldset
              className="space-y-3"
              disabled={!configurationModifiable || sauvegardeTimeoutEnCours}
            >
              <label className="flex items-center gap-2 text-sm">
                <input
                  type="checkbox"
                  checked={timeoutActif}
                  onChange={(e) => {
                    setEditionTimeoutDirty(true);
                    setTimeoutActif(e.target.checked);
                  }}
                />
                Timeout d’inactivité actif
              </label>

              <div className="grid gap-2 sm:grid-cols-[minmax(0,1fr)_9rem]">
                <label className="flex flex-col gap-1 text-xs">
                  Délai
                  <input
                    type="number"
                    min={1}
                    max={delaiTimeoutUnite === "heures" ? 24 : 1440}
                    className="bg-slate-900 border border-slate-700 rounded px-2 py-1 text-sm"
                    value={delaiTimeoutValeur}
                    onChange={(e) => {
                      setEditionTimeoutDirty(true);
                      setDelaiTimeoutValeur(Number(e.target.value));
                    }}
                  />
                </label>

                <label className="flex flex-col gap-1 text-xs">
                  Unité
                  <select
                    className="bg-slate-900 border border-slate-700 rounded px-2 py-1 text-sm"
                    value={delaiTimeoutUnite}
                    onChange={(e) => {
                      setEditionTimeoutDirty(true);
                      setDelaiTimeoutUnite(e.target.value as UniteDelaiTimeout);
                    }}
                  >
                    <option value="minutes">minutes</option>
                    <option value="heures">heures</option>
                  </select>
                </label>
              </div>

              <Button
                size="sm"
                variant="secondary"
                type="button"
                onClick={handleSauvegarderTimeout}
              >
                {sauvegardeTimeoutEnCours ? "Enregistrement…" : "Enregistrer"}
              </Button>
            </fieldset>
          )}

          {messageTimeout && (
            <p className="text-xs text-bleuGlacier">{messageTimeout}</p>
          )}
        </div>
      )}

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
