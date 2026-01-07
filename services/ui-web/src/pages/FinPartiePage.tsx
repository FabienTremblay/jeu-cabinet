import React, { useState } from "react";
import { useParams } from "react-router-dom";
import type { EntreePalmares } from "../types/game";
import { useSession } from "../context/SessionContext";
import { soumettreAction } from "../api/moteurApi";
import { idCourt } from "../utils/idCourt";
type FinPartiePageProps = {
  palmares?: EntreePalmares[] | null;
  raison?: string | null;
  // pour réutiliser la section "Victoire" (clan + PM potentiel) déjà prévue au status panel
  tour?: number | null;
  capitalCollectif?: number | null;
  capitalOpposition?: number | null;
  joueurs?: Array<{
    id: string;
    alias?: string;
    capital_politique?: number;
    poids_vote?: number;
  }> | null;
  joueurId?: string | null;
  // bouton quitter géré par GamePage (flow actuel)
  onQuitterPartie?: () => void;
  quitterEnCours?: boolean;
  erreurQuitter?: string | null;
};

function classStatut(statut: "ok" | "warning" | "bad") {
  if (statut === "ok") return "border-emerald-500/40 bg-emerald-500/10";
  if (statut === "warning") return "border-amber-400/40 bg-amber-400/10";
  return "border-rougeErable/50 bg-rougeErable/10";
}
function labelStatut(statut: "ok" | "warning" | "bad") {
  if (statut === "ok") return "✔ victoire en bonne voie";
  if (statut === "warning") return "⚠ victoire non assurée";
  return "✖ victoire en péril";
}

const FinPartiePage: React.FC<FinPartiePageProps> = ({
  palmares,
  raison,
  tour,
  capitalCollectif,
  capitalOpposition,
  joueurs,
  joueurId,
  onQuitterPartie,
  quitterEnCours: quitterEnCoursProp,
  erreurQuitter: erreurQuitterProp,
}) => {
  const { partieId } = useParams<{ partieId: string }>();
  const { joueur } = useSession();

  const [quitterEnCoursLocal, setQuitterEnCoursLocal] = useState(false);
  const [erreurQuitterLocal, setErreurQuitterLocal] = useState<string | null>(null);
  const quitterEnCoursEffectif =
    typeof quitterEnCoursProp === "boolean" ? quitterEnCoursProp : quitterEnCoursLocal;
  const erreurQuitterEffectif =
    typeof erreurQuitterProp === "string" ? erreurQuitterProp : erreurQuitterLocal;

  const palmaresAffiche = Array.isArray(palmares) ? palmares : [];

  const handleQuitterPartie = async () => {
    // si on n’a pas l’info, on ne peut pas envoyer l’op; la navigation se fera via l’ancrage quand disponible.
    if (!partieId || !joueur) {
      return;
    }

    setQuitterEnCoursLocal(true);
    setErreurQuitterLocal(null);

    try {
      await soumettreAction(partieId, {
        acteur: joueur.id_joueur,
        type_action: "partie.joueur_quitte_definitivement",
        // donnees facultatives : le backend sait déjà qui est l’acteur
        donnees: {
          joueur_id: joueur.id_joueur,
        },
      });
    } catch (err) {
      console.error(
        "Erreur lors de la demande de quitter la partie :",
        err
      );
      setErreurQuitterLocal(
        "Impossible de quitter la partie pour le moment. Veuillez réessayer."
      );
    } finally {
      setQuitterEnCoursLocal(false);
    }
  };
  const t = typeof tour === "number" ? tour : null;

  // Bloc Victoire (clan + PM potentiel) — cohérent avec PlayerStatusPanel
  const cab = typeof capitalCollectif === "number" ? capitalCollectif : 0;
  const opp = typeof capitalOpposition === "number" ? capitalOpposition : 0;
  // règle: égalité => cabinet gagne
  const cabinetGagne = cab > 0 && cab >= opp;
  const oppositionGagne = !cabinetGagne;

  // (optionnel) garder un statut "serré" quand égalité ou écart 1
  const victoireNonAssuree = cabinetGagne && (cab === opp || opp === cab - 1);

  const pm = (() => {
    if (!Array.isArray(joueurs) || !joueurId || joueurs.length === 0) return null;
    const scored = joueurs
      .map((r) => ({
        id: r.id,
        alias: r.alias ?? r.id,
        cap: typeof r.capital_politique === "number" ? r.capital_politique : -999999,
        pv: typeof r.poids_vote === "number" ? r.poids_vote : 0,
      }))
      .sort((a, b) => (b.cap - a.cap) || (b.pv - a.pv));
    const idx = scored.findIndex((x) => x.id === joueurId);
    if (idx < 0) return null;
    const leader = scored[0];
    const me = scored[idx];
    return { rang: idx + 1, total: scored.length, cap: me.cap, leaderAlias: leader.alias, ecart: me.cap - leader.cap };
  })();

  const onQuitter = async () => {
    // si GamePage fournit le handler, on l’utilise, mais on conserve l’acquis:
    // on revient au lobby une fois l’intention de quitter envoyée.
    if (onQuitterPartie) {
      await onQuitterPartie();
      return;
    }
    await handleQuitterPartie();
  };

  // --- Classement final des prétendants au poste de PM ---
  const classementPM = Array.isArray(joueurs)
    ? [...joueurs]
        .map((j) => ({
          id: j.id,
          alias: j.alias ?? j.id,
          capital: typeof j.capital_politique === "number" ? j.capital_politique : 0,
          poids: typeof j.poids_vote === "number" ? j.poids_vote : 0,
        }))
        .sort((a, b) => (b.capital - a.capital) || (b.poids - a.poids))
    : [];

  const premierMinistre = classementPM.length > 0 ? classementPM[0] : null;

  return (
    <div className="p-4 space-y-4">
      <div>
        <h1 className="text-2xl font-bold mb-2">Partie terminée</h1>
        {raison && <p className="text-sm text-slate-200">{raison}</p>}
        {!raison && (
          <p className="text-sm text-slate-200">
            La partie est terminée. Vous pouvez consulter les résultats
            pendant quelques instants.
          </p>
        )}
      </div>

      {/* Bloc Victoire (clan + PM potentiel) */}
      <div className="rounded-card border border-white/10 bg-black/10 px-4 py-3">
        <div className="text-[10px] uppercase tracking-wide text-blancNordique/60">
          victoire (résultat final)
        </div>

      {/* Classement final – Premier ministre (seulement si le cabinet gagne) */}
      {cabinetGagne && classementPM.length > 0 && (
        <div className="rounded-card border border-white/10 bg-black/10 px-4 py-3">
          <div className="text-[10px] uppercase tracking-wide text-blancNordique/60">
            prochain premier ministre
          </div>

          <ol className="mt-2 space-y-1 text-sm text-blancNordique/85">
            {classementPM.map((j, idx) => (
              <li key={j.id} className={idx === 0 ? "font-semibold" : ""}>
                {idx + 1}. {j.alias} — capital politique {j.capital}
              </li>
            ))}
          </ol>

          {premierMinistre && (
            <div className="mt-2 text-sm text-blancNordique/80">
              → <span className="font-semibold">{premierMinistre.alias}</span>{" "}
              formerait le prochain gouvernement
            </div>
          )}
        </div>
      )}

        <div className="mt-1 text-sm text-blancNordique/85">
          Tour {typeof tour === "number" ? tour : "?"} · cabinet {cab} · opposition {opp}
        </div>
        <div className="mt-1 text-sm font-semibold">
          {oppositionGagne
            ? "✖ opposition victorieuse (tout le monde a perdu)"
            : victoireNonAssuree
              ? "⚠ cabinet victorieux (issue indécidable)"
              : "✔ cabinet victorieux"}
        </div>
      </div>


      {palmaresAffiche.length > 0 && (
        <div>
          <h2 className="font-semibold mb-1">Résultats</h2>
          <ol className="list-decimal list-inside space-y-1">
            {palmaresAffiche.map((p) => (
              <li key={p.joueur_id}>
                {p.rang}. {p.alias ?? idCourt(p.joueur_id)} — {p.score_total} points
              </li>
            ))}
          </ol>
        </div>
      )}

      {erreurQuitterEffectif && (
        <p className="text-sm text-red-400">{erreurQuitterEffectif}</p>
      )}

      <button
        className="border px-3 py-2 rounded mt-4 disabled:opacity-60 disabled:cursor-not-allowed"
        onClick={onQuitter}
        disabled={quitterEnCoursEffectif}
      >
        {quitterEnCoursEffectif ? "Quitter la partie…" : "Quitter la partie"}
      </button>
    </div>
  );
};

export default FinPartiePage;

