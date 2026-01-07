// src/components/game/ActionsPanel.tsx
import React, { useMemo, useState } from "react";
import { soumettreAction } from "../../api/moteurApi";

import type { Carte, RequeteAction } from "../../types/game";

const CarteChoiceItem: React.FC<{
  carte: Carte;
  selected: boolean;
  onSelect: () => void;
}> = ({ carte, selected, onSelect }) => {
  return (
    <button
      type="button"
      onClick={onSelect}
      className={`w-full text-left rounded-lg border px-3 py-2 text-xs mb-1 ${
        selected
          ? "border-bleu-glacier bg-slate-800"
          : "border-slate-700 bg-slate-900 hover:bg-slate-800"
      }`}
    >
      <div className="text-[10px] text-slate-300">{carte.id}</div>
      <div className="font-semibold text-sm text-slate-50">{carte.nom}</div>
      <div className="text-[11px] text-slate-200/80 mt-1">
        <span className="capitalize">{carte.type}</span>
        {typeof carte.cout_attention === "number" &&
          carte.cout_attention > 0 && (
            <> · coût attention : {carte.cout_attention}</>
          )}
        {typeof carte.cout_cp === "number" && carte.cout_cp > 0 && (
          <> · coût capital : {carte.cout_cp}</>
        )}
      </div>
      {carte.resume && (
        <div className="text-[11px] text-slate-100 mt-1">{carte.resume}</div>
      )}
    </button>
  );
};

// -----------------------------------------------------------------------------
// Contrat actions UI (etat.attente.meta.ui.actions)
// -----------------------------------------------------------------------------

export interface AttenteUiField {
  name: string;
  label: string;
  required?: boolean;
  // Peut être une string ("joueur_id", "carte_main", "effort_attention", ...)
  // ou un objet { kind: "choice", values: [...] }
  domain?: any;
}

export interface AttenteUiAction {
  op: string;
  label: string;
  fields?: AttenteUiField[];
}

function isChoiceDomain(domain: any): domain is { kind: string; values: any[] } {
  return domain && typeof domain === "object" && domain.kind === "choice";
}

function fieldNeedsCard(field: AttenteUiField): boolean {
  return field.domain === "carte_main";
}

function fieldNeedsChoice(field: AttenteUiField): boolean {
  return isChoiceDomain(field.domain);
}

function fieldNeedsEffortAttention(field: AttenteUiField): boolean {
  return field.domain === "effort_attention";
}

function fieldNeedsEffortCp(field: AttenteUiField): boolean {
  return field.domain === "effort_cp";
}

// -----------------------------------------------------------------------------
// Props & contexte de build
// -----------------------------------------------------------------------------

export interface ActionsPanelProps {
  partieId: string;
  acteurId: string;
  phase?: string | null;
  sousPhase?: string | null;
  attenteType?: string | null;
  uiActions: AttenteUiAction[];
  main: Carte[];
  onActionSent?: (op: string) => void;
}

// Contexte pour construire le payload côté UI
interface BuildContext {
  acteurId: string;
  attenteType?: string | null;
  selectedCardId?: string | null;
  choiceValue?: unknown;

  // Efforts optionnels (attention / capital politique)
  effortAttention?: number | null;
  effortCp?: number | null;

  // Pour plus tard : cibles, autres paramètres
  cibleId?: string | null;
}

// Joker : on refuse de laisser passer _auto / _cible / _effort vers le moteur
function detecterJoker(donnees: Record<string, unknown>): string | null {
  for (const value of Object.values(donnees)) {
    if (value === "_auto" || value === "_cible" || value === "_effort") {
      return String(value);
    }
  }
  return null;
}

// Construction du payload de base à partir de uiActions + contexte
function buildPayloadForAction(
  action: AttenteUiAction,
  ctx: BuildContext
): Record<string, unknown> {
  const payload: Record<string, unknown> = {};

  for (const field of action.fields ?? []) {
    const { name, required, domain } = field;

    // joueur_id : toujours acteurId côté UI
    if (domain === "joueur_id") {
      payload[name] = ctx.acteurId;
      continue;
    }

    // type d’attente (ENGAGER_CARTE, VOTE_PROGRAMME, PERTURBATION_VOTE, …)
    if (domain === "attente_type") {
      if (ctx.attenteType) {
        payload[name] = ctx.attenteType;
      } else if (required) {
        throw new Error(
          `Champ ${name} (attente_type) requis mais attenteType manquant.`
        );
      }
      continue;
    }

    // carte à choisir dans la main
    if (domain === "carte_main") {
      if (!ctx.selectedCardId) {
        if (required) {
          throw new Error(
            `Une carte doit être sélectionnée pour l’action ${action.op}.`
          );
        }
      } else {
        payload[name] = ctx.selectedCardId;
      }
      continue;
    }

    // Effort d’attention explicite : si le domaine le demande,
    // l’UI DOIT fournir la valeur (sinon erreur).
    if (domain === "effort_attention") {
      if (
        ctx.effortAttention === null ||
        ctx.effortAttention === undefined ||
        Number.isNaN(ctx.effortAttention)
      ) {
        if (required) {
          throw new Error(
            `Un effort d’attention doit être fourni pour le champ ${name}.`
          );
        }
      } else {
        payload[name] = ctx.effortAttention;
      }
      continue;
    }

    // Effort de capital politique explicite
    if (domain === "effort_cp") {
      if (
        ctx.effortCp === null ||
        ctx.effortCp === undefined ||
        Number.isNaN(ctx.effortCp)
      ) {
        if (required) {
          throw new Error(
            `Un effort de capital politique doit être fourni pour le champ ${name}.`
          );
        }
      } else {
        payload[name] = ctx.effortCp;
      }
      continue;
    }

    // domaine à choix (vote, etc.)
    if (isChoiceDomain(domain)) {
      if (ctx.choiceValue == null) {
        if (required) {
          throw new Error(
            `Une valeur doit être choisie pour le champ ${name}.`
          );
        }
      } else {
        payload[name] = ctx.choiceValue;
      }
      continue;
    }

    // domaines non gérés explicitement : laissés vides côté UI
    // (pourront être complétés plus tard si besoin).
  }

  return payload;
}

// -----------------------------------------------------------------------------
// Composant principal
// -----------------------------------------------------------------------------

export const ActionsPanel: React.FC<ActionsPanelProps> = ({
  partieId,
  acteurId,
  phase,
  sousPhase,
  attenteType,
  uiActions,
  main,
  onActionSent,
}) => {
  const [selectedActionOp, setSelectedActionOp] = useState<string | null>(null);
  const [selectedCardId, setSelectedCardId] = useState<string | null>(null);
  const [choiceValue, setChoiceValue] = useState<unknown>(null);
  const [effortAttention, setEffortAttention] = useState<number | null>(null);
  const [effortCp, setEffortCp] = useState<number | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [opsEnvoyees, setOpsEnvoyees] = useState<Set<string>>(() => new Set());
  const [feedbackSucces, setFeedbackSucces] = useState<string | null>(null);
  const [opEnCours, setOpEnCours] = useState<string | null>(null);

  const estPerturbationVote = useMemo(() => {
    const p = String(phase ?? "").toUpperCase();
    const sp = String(sousPhase ?? "").toUpperCase();
    return p.includes("PHASE_PERTURBATION_VOTE") || sp.includes("PHASE_PERTURBATION_VOTE");
  }, [phase, sousPhase]);

  function estActionAucuneCarte(action: AttenteUiAction): boolean {
    const op = String(action?.op ?? "").toLowerCase();
    const label = String(action?.label ?? "").toLowerCase();
    return (
      label.includes("aucune carte") ||
      label.includes("ne joue") ||
      op.includes("aucune") ||
      op.includes("sans_carte") ||
      op.includes("no_card")
    );
  }

  // ------------------------------------------------------------
  // Anti-doublon : on filtre les actions prises en charge par ProgrammeView
  // (programme/vote/engagement + actions nécessitant carte_main ou choice)
  // ------------------------------------------------------------
  const availableActions = useMemo(() => {
    const actions = uiActions ?? [];

    return actions.filter((a) => {
      const op = String(a?.op ?? "").toLowerCase();
      const label = String(a?.label ?? "").toLowerCase();

      const fields = Array.isArray(a?.fields) ? a.fields : [];
      const hasCarteMain = fields.some((f: any) => f?.domain === "carte_main");
      const hasChoice = fields.some(
        (f: any) =>
          typeof f?.domain === "object" &&
          f.domain &&
          (f.domain as any).kind === "choice"
      );

      const estProgramme =
        hasCarteMain ||
        hasChoice ||
        op.includes("programme") ||
        op.includes("vote") ||
        label.includes("vote") ||
        label.includes("engagement") ||
        label.includes("engager") ||
        label.includes("terminer") ||
        label.includes("enregistrer") ||
        label.includes("confirmer");

      return !estProgramme;
    });
  }, [uiActions]);

  // Optimistic UI : dès qu’une action est envoyée avec succès, on la retire localement
  // (et on attend que le polling reflète la nouvelle situation).
  // Dès que uiActions change (nouvelle photo serveur), on réinitialise notre retrait local.
  React.useEffect(() => {
    if (opsEnvoyees.size > 0) {
      setOpsEnvoyees(new Set());
    }
    // on ne force pas le feedback à disparaître : il s’efface via timeout ci-dessous
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [uiActions]);

  React.useEffect(() => {
    if (!feedbackSucces) return;
    const t = window.setTimeout(() => setFeedbackSucces(null), 2500);
    return () => window.clearTimeout(t);
  }, [feedbackSucces]);

  const availableActionsAffichees = useMemo(() => {
    if (!opsEnvoyees.size) return availableActions;
    return availableActions.filter((a) => !opsEnvoyees.has(a.op));
  }, [availableActions, opsEnvoyees]);


  const currentAction = useMemo(
    () => availableActionsAffichees.find((a) => a.op === selectedActionOp) ?? null,
    [availableActionsAffichees, selectedActionOp]
  );

  const currentNeedsCard = useMemo(() => {
    if (!currentAction) return false;
    return (currentAction.fields ?? []).some(fieldNeedsCard);
  }, [currentAction]);

  const currentChoiceField = useMemo(() => {
    if (!currentAction) return null;
    return (
      (currentAction.fields ?? []).find((f) => fieldNeedsChoice(f)) ?? null
    );
  }, [currentAction]);

  const currentChoiceOptions = useMemo(() => {
    if (!currentChoiceField || !isChoiceDomain(currentChoiceField.domain)) {
      return [];
    }
    return currentChoiceField.domain.values ?? [];
  }, [currentChoiceField]);

  const currentNeedsEffortAttention = useMemo(() => {
    if (!currentAction) return false;
    return (currentAction.fields ?? []).some(fieldNeedsEffortAttention);
  }, [currentAction]);

  const currentNeedsEffortCp = useMemo(() => {
    if (!currentAction) return false;
    return (currentAction.fields ?? []).some(fieldNeedsEffortCp);
  }, [currentAction]);

  const resetLocalState = () => {
    setSelectedCardId(null);
    setChoiceValue(null);
    setEffortAttention(null);
    setEffortCp(null);
    setSelectedActionOp(null);
    setError(null);
  };

  async function handleDirectAction(action: AttenteUiAction) {
    setError(null);
    setLoading(true);
    setOpEnCours(action.op);
    try {
      const ctxBuild: BuildContext = {
        acteurId,
        attenteType,
        selectedCardId: null,
        choiceValue: null,
        effortAttention: null,
        effortCp: null,
      };

      const donnees = buildPayloadForAction(action, ctxBuild);

      const joker = detecterJoker(donnees);
      if (joker) {
        console.error("Joker non résolu dans donnees :", donnees);
        throw new Error(
          `L’action ${action.op} contient encore un joker interne (${joker}). ` +
            "L’interface doit le résoudre avant l’envoi."
        );
      }

      const req: RequeteAction = {
        acteur: acteurId,
        type_action: action.op,
        donnees,
      };

      await soumettreAction(partieId, req, {
        acteurId,
        attenteType,
      });

      // Retrait immédiat : feedback visuel (succès) + disparition de l’action
      setOpsEnvoyees((prev) => {
        const next = new Set(prev);
        next.add(action.op);
        return next;
      });
      setFeedbackSucces(`Action envoyée : ${action.label}`);

      onActionSent?.(action.op);
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setLoading(false);
      setOpEnCours(null);
    }
  }

  const handleSelectAction = (action: AttenteUiAction) => {
    const fields = action.fields ?? [];
    const needsCard = fields.some(fieldNeedsCard);
    const needsChoice = fields.some(fieldNeedsChoice);
    const needsEffAtt = fields.some(fieldNeedsEffortAttention);
    const needsEffCp = fields.some(fieldNeedsEffortCp);

    // si aucun input requis → action immédiate
    if (!needsCard && !needsChoice && !needsEffAtt && !needsEffCp) {
      void handleDirectAction(action);
      return;
    }

    setError(null);
    setSelectedActionOp(action.op);
    setSelectedCardId(null);
    setChoiceValue(null);
    setEffortAttention(null);
    setEffortCp(null);
  };

  const handleConfirmCurrentAction = async () => {
    if (!currentAction) return;

    setLoading(true);
    setError(null);
    setOpEnCours(currentAction.op);

    try {
      const ctxBuild: BuildContext = {
        acteurId,
        attenteType,
        selectedCardId,
        choiceValue,
        effortAttention,
        effortCp,
      };

      const donnees = buildPayloadForAction(currentAction, ctxBuild);

      const joker = detecterJoker(donnees);
      if (joker) {
        console.error("Joker non résolu dans donnees :", donnees);
        throw new Error(
          `L’action ${currentAction.op} contient encore un joker interne (${joker}). ` +
            "L’interface doit le résoudre avant l’envoi."
        );
      }

      const req: RequeteAction = {
        acteur: acteurId,
        type_action: currentAction.op,
        donnees,
      };

      await soumettreAction(partieId, req, {
        acteurId,
        attenteType,
        selectedCardId,
      });

      setOpsEnvoyees((prev) => {
        const next = new Set(prev);
        next.add(currentAction.op);
        return next;
      });
      setFeedbackSucces(`Action envoyée : ${currentAction.label}`);
      onActionSent?.(currentAction.op);
      resetLocalState();
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setLoading(false);
      setOpEnCours(null);
    }
  };

  if (!partieId || !acteurId) {
    return null;
  }

  const actionAucuneCarte = estPerturbationVote
    ? availableActionsAffichees.find(estActionAucuneCarte) ?? null
    : null;
  const actionsNormales = actionAucuneCarte
    ? availableActionsAffichees.filter((a) => a.op !== actionAucuneCarte.op)
    : availableActionsAffichees;

  return (
    <div className="border border-slate-800 rounded-lg p-3">
      <h3 className="text-sm font-semibold mb-2">Actions disponibles</h3>

      {phase && (
        <p className="text-[11px] mb-2 text-slate-300">
          Phase : {phase}
          {sousPhase ? ` / ${sousPhase}` : ""}
        </p>
      )}

      {estPerturbationVote && (
        <div className="mb-3 rounded-lg border border-bleu-glacier/60 bg-slate-900 px-3 py-2">
          <div className="text-xs font-semibold text-slate-50">
            perturbations : à toi d’agir
          </div>
          <div className="text-[11px] text-slate-200/80 mt-0.5">
            S'il te reste des points d'attention, joue une carte si tu en as une… sinon confirme explicitement que tu n’en joues aucune.
          </div>
        </div>
      )}

      {feedbackSucces ? (
        <div className="mb-2 rounded-lg border border-bleuGlacier/50 bg-bleuBoreal/30 px-3 py-2">
          <div className="text-[12px] font-semibold text-blancNordique/90">
            ✅ {feedbackSucces}
          </div>
          <div className="text-[11px] text-blancNordique/70 mt-0.5">
            Mise à jour en cours… les actions vont se rafraîchir automatiquement.
          </div>
        </div>
      ) : null}

      {availableActions.length === 0 && (
        <p className="text-[11px] text-slate-400">
          Aucune action particulière pour ce tour.
        </p>
      )}

      <div className="space-y-1 mb-2">
        {actionsNormales.map((action) => {
          const isCurrent = currentAction?.op === action.op;
          const fields = action.fields ?? [];
          const needsCard = fields.some(fieldNeedsCard);
          const needsChoice = fields.some(fieldNeedsChoice);
          const needsEffAtt = fields.some(fieldNeedsEffortAttention);
          const needsEffCp = fields.some(fieldNeedsEffortCp);

          return (
            <button
              key={action.op}
              type="button"
              className={`w-full text-left text-[11px] px-2 py-1 rounded border ${
                isCurrent
                  ? "border-bleu-glacier bg-slate-800"
                  : "border-slate-700 bg-slate-900 hover:bg-slate-800"
              }`}
              disabled={loading}
              onClick={() => handleSelectAction(action)}
            >
              <div className="font-semibold text-xs">
                {opEnCours === action.op ? "Envoi…" : action.label}
              </div>
              {(needsCard || needsChoice || needsEffAtt || needsEffCp) && (
                <div className="text-[10px] text-slate-300 mt-0.5">
                  {needsCard && "Nécessite une carte de ta main. "}
                  {needsChoice && "Nécessite un choix. "}
                  {needsEffAtt &&
                    "Nécessite un effort d’attention (peut être supérieur au coût par défaut). "}
                  {needsEffCp &&
                    "Nécessite un effort de capital politique (peut être supérieur au coût par défaut)."}
                </div>
              )}
            </button>
          );
        })}
      </div>

      {/* Action primaire “aucune carte” pendant PHASE_PERTURBATION_VOTE */}
      {actionAucuneCarte && (
        <div className="mt-3 pt-3 border-t border-slate-700">
          <div className="text-[11px] text-slate-300 mb-2">
            si tu ne joues aucune carte de perturbation :
          </div>
          <button
            type="button"
            className="w-full rounded-lg border border-bleu-glacier bg-bleu-glacier text-slate-950 font-semibold px-4 py-3 text-sm hover:brightness-110 disabled:opacity-60"
            disabled={loading}
            onClick={() => handleSelectAction(actionAucuneCarte)}
          >
            {opEnCours === actionAucuneCarte.op ? "Envoi…" : actionAucuneCarte.label}
          </button>
          <div className="text-[11px] text-slate-200/70 mt-2">
            tu confirmes officiellement que tu ne joues aucune carte.
          </div>
        </div>
      )}

      {/* panneau détaillé si l'action courante a besoin d'inputs */}
      {currentAction &&
        (currentNeedsCard ||
          currentChoiceField ||
          currentNeedsEffortAttention ||
          currentNeedsEffortCp) && (
          <div className="mt-2 border-t border-slate-700 pt-2 space-y-2">
            <div className="text-[11px] font-semibold">
              Action : {currentAction.label}
            </div>

            {currentNeedsCard && (
              <div>
                <div className="text-[11px] mb-1">
                  Choisis une carte de ta main :
                </div>
                {main.length === 0 ? (
                  <p className="text-[11px] text-slate-400">
                    Ta main est vide, tu ne peux pas engager de carte.
                  </p>
                ) : (
                  <div>
                    {main.map((c) => (
                      <CarteChoiceItem
                        key={c.id}
                        carte={c}
                        selected={selectedCardId === c.id}
                        onSelect={() => setSelectedCardId(c.id)}
                      />
                    ))}
                  </div>
                )}
              </div>
            )}

            {currentChoiceField && currentChoiceOptions.length > 0 && (
              <div>
                <label className="text-[11px] mb-1 block">
                  {currentChoiceField.label}
                  <select
                    className="mt-1 w-full bg-slate-900 border border-slate-700 rounded px-2 py-1 text-[11px]"
                    value={choiceValue != null ? String(choiceValue) : ""}
                    onChange={(e) => setChoiceValue(e.target.value)}
                  >
                    <option value="">-- Choisir --</option>
                    {currentChoiceOptions.map((opt: any) => (
                      <option
                        key={String(opt.value ?? opt)}
                        value={String(opt.value ?? opt)}
                      >
                        {String(opt.label ?? opt)}
                      </option>
                    ))}
                  </select>
                </label>
              </div>
            )}

            {currentNeedsEffortAttention && (
              <div>
                <label className="text-[11px] mb-1 block">
                  Effort d’attention
                  <input
                    type="number"
                    min={0}
                    className="mt-1 w-full bg-slate-900 border border-slate-700 rounded px-2 py-1 text-[11px]"
                    value={effortAttention ?? ""}
                    onChange={(e) => {
                      const v = e.target.value;
                      setEffortAttention(v === "" ? null : Number(v));
                    }}
                    placeholder="Laisse vide pour utiliser le coût par défaut de la carte"
                  />
                </label>
              </div>
            )}

            {currentNeedsEffortCp && (
              <div>
                <label className="text-[11px] mb-1 block">
                  Effort de capital politique
                  <input
                    type="number"
                    min={0}
                    className="mt-1 w-full bg-slate-900 border border-slate-700 rounded px-2 py-1 text-[11px]"
                    value={effortCp ?? ""}
                    onChange={(e) => {
                      const v = e.target.value;
                      setEffortCp(v === "" ? null : Number(v));
                    }}
                    placeholder="Laisse vide pour utiliser le coût par défaut de la carte"
                  />
                </label>
              </div>
            )}

            <div className="flex justify-end gap-2 pt-1">
              <button
                type="button"
                className="text-[11px] px-2 py-1 rounded border border-slate-600 text-slate-200 hover:bg-slate-800"
                onClick={resetLocalState}
                disabled={loading}
              >
                Annuler
              </button>
              <button
                type="button"
                className="text-[11px] px-3 py-1 rounded bg-bleu-glacier text-slate-900 font-semibold disabled:opacity-60"
                disabled={loading}
                onClick={handleConfirmCurrentAction}
              >
                Confirmer
              </button>
            </div>
          </div>
        )}

      {error && (
        <p className="mt-1 text-[11px] text-rouge-erable">
          {error}
        </p>
      )}
    </div>
  );
};

export default ActionsPanel;

