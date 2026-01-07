// src/components/game/ProgrammeView.tsx
import React, { useMemo, useState } from "react";
import { soumettreAction } from "../../api/moteurApi";

import type { AttenteUiAction, Carte, CarteEngagee, RequeteAction } from "../../types/game";

interface Props {
  programme?: CarteEngagee[];
  main?: Carte[];
  partieId: string;
  acteurId: string;
  aliasParJoueur?: Record<string, string>;
  attenteType?: string | null;
  uiActions?: AttenteUiAction[];
  programmeVotes?: Record<string, number>;
  programmeVerdict?: boolean | null;
  /** Ouvre l'onglet Actions sur la carte choisie (détails) */
  onVoirCarteDetails?: (carteId: string) => void;
  onActionSent?: (op: string) => void;
}

function isChoiceDomain(domain: any): domain is { kind: string; values: any[] } {
  return domain && typeof domain === "object" && domain.kind === "choice" && Array.isArray(domain.values);
}

function buildDonnees(
  action: AttenteUiAction,
  opts: { acteurId: string; selectedCardId?: string | null; choiceValue?: unknown; attenteType?: string | null }
): Record<string, unknown> {
  const donnees: Record<string, unknown> = {};
  const fields = action.fields ?? [];

  for (const f of fields) {
    const name = f.name;
    const required = !!f.required;
    const domain = f.domain;

    if (domain === "joueur_id") {
      donnees[name] = opts.acteurId;
      continue;
    }

    if (domain === "carte_main") {
      if (!opts.selectedCardId) {
        if (required) throw new Error("Veuillez choisir une carte.");
      } else {
        donnees[name] = opts.selectedCardId;
      }
      continue;
    }

    if (isChoiceDomain(domain)) {
      if (opts.choiceValue == null) {
        if (required) throw new Error("Veuillez faire un choix.");
      } else {
        donnees[name] = opts.choiceValue;
      }
      continue;
    }
    if (domain === "attente_type") {
      if (opts.attenteType) {
        donnees[name] = opts.attenteType;
      } else if (required) {
        throw new Error("Action invalide : attente_type requis mais attenteType manquant.");
      }
      continue;
    }

    // autres domaines : ignorés ici (CTA mobile minimal)
  }

  return donnees;
}


function buildDonneesRetirer(
  action: AttenteUiAction,
  opts: { acteurId: string; uidEntree: string; attenteType?: string | null }
): Record<string, unknown> {
  const donnees: Record<string, unknown> = {};
  const fields = action.fields ?? [];

  // on remplit uniquement ce qu'on sait garantir
  // - joueur_id => acteurId
  // - uid / uid_entree => uid de l'entrée au programme
  // - attente_type si requis
  for (const f of fields) {
    const name = f.name;
    const required = !!f.required;
    const domain = f.domain;

    if (domain === "joueur_id") {
      donnees[name] = opts.acteurId;
      continue;
    }

    // contrat recommandé côté moteur: { uid: "EP-2" }
    // côté UI, le field peut s'appeler uid ou uid_entree (ou autre),
    // donc on l'alimente par heuristique sur le nom.
    const n = (name ?? "").toLowerCase();
    if (n === "uid" || n === "uid_entree" || n.includes("uid")) {
      donnees[name] = opts.uidEntree;
      continue;
    }

    if (domain === "attente_type") {
      if (opts.attenteType) donnees[name] = opts.attenteType;
      else if (required) throw new Error("Action invalide : attente_type requis mais manquant.");
      continue;
    }
  }

  // fallback: si aucun field n’a capté le uid (config UI incomplète),
  // on envoie quand même "uid" pour rester compatible avec la commande moteur proposée.
  if (donnees.uid == null) {
    donnees.uid = opts.uidEntree;
  }
  return donnees;
}


async function envoyerAction(
  partieId: string,
  acteurId: string,
  attenteType: string | null | undefined,
  action: AttenteUiAction,
  donnees: Record<string, unknown>,
  onActionSent?: (op: string) => void
) {
  const req: RequeteAction = {
    acteur: acteurId,
    type_action: action.op,
    donnees,
  };

  await soumettreAction(partieId, req, {
    acteurId,
    attenteType: attenteType ?? null,
    selectedCardId: (donnees as any)?.carte_id ?? null,
  });

  onActionSent?.(action.op);
}

export const ProgrammeView: React.FC<Props> = ({
  programme,
  main,
  partieId,
  acteurId,
  aliasParJoueur,
  attenteType,
  uiActions,
  programmeVotes,
  programmeVerdict,
  onVoirCarteDetails,
  onActionSent,
}) => {
  const liste = programme ?? [];
  const cartesMain = main ?? [];
  const actions = uiActions ?? [];

  const nomJoueur = (jid?: string | null) => {
    if (!jid) return "?";
    return aliasParJoueur?.[jid] ?? jid;
  };

  const estPhaseVote = useMemo(() => {
    const t = String(attenteType ?? "").toLowerCase();
    return t.includes("vote");
  }, [attenteType]);

  const libelleTypeFamille = (type?: string | null) => {
    const t = String(type ?? "").trim().toLowerCase();
    if (t.includes("mesure")) return "Mesure gouvernementale";
    if (t.includes("relation")) return "Manœuvre stratégique";
    if (t.includes("influence")) return "Action politique";
    return "Action politique";
  };

  const nomActeur = useMemo(() => nomJoueur(acteurId), [acteurId, aliasParJoueur]);
    const opLower = (a: AttenteUiAction) => (a.op ?? "").toLowerCase();
    const labelLower = (a: AttenteUiAction) => (a.label ?? "").toLowerCase();
    const fields = (a: AttenteUiAction) => a.fields ?? [];
    const hasDomain = (a: AttenteUiAction, d: string) => fields(a).some((f) => f.domain === d);
    const hasChoice = (a: AttenteUiAction) => fields(a).some((f) => isChoiceDomain(f.domain));

    const actionEngager = useMemo(() => {
      // le plus fiable : nécessite une carte_main
      return (
        actions.find((a) => hasDomain(a, "carte_main") && (opLower(a).includes("engager") || labelLower(a).includes("engager"))) ??
        actions.find((a) => hasDomain(a, "carte_main")) ??
        null
      );
    }, [actions]);

    const actionTerminer = useMemo(() => {
      return (
        actions.find((a) => labelLower(a).includes("terminer") && labelLower(a).includes("engagement")) ??
        actions.find((a) => opLower(a).includes("terminer") && opLower(a).includes("engagement")) ??
        null
      );
    }, [actions]);

    const actionVote = useMemo(() => {
      // fiable : action avec choix (choice) + label/op qui ressemble à vote
      return (
        actions.find((a) => hasChoice(a) && (labelLower(a).includes("vote") || opLower(a).includes("vote") || opLower(a).includes("voter"))) ??
        actions.find((a) => opLower(a).includes("vote") || opLower(a).includes("voter")) ??
        null
      );
    }, [actions]);

    const actionConfirmer = useMemo(() => {
      return (
        actions.find((a) => labelLower(a).includes("enregistrer") || labelLower(a).includes("confirmer")) ??
        actions.find((a) => opLower(a).includes("confirmer") || opLower(a).includes("confirmation")) ??
        null
      );
    }, [actions]);


    const actionRetirer = useMemo(() => {
      return (
        actions.find((a) => opLower(a).includes("programme.retirer_carte")) ??
        actions.find((a) => opLower(a).includes("retirer") && opLower(a).includes("programme")) ??
        actions.find((a) => labelLower(a).includes("retirer") && labelLower(a).includes("programme")) ??
        null
      );
    }, [actions]);

  const voteChoiceField = useMemo(() => {
    if (!actionVote) return null;
    return (actionVote.fields ?? []).find((f: any) => isChoiceDomain(f.domain)) ?? null;
  }, [actionVote]);

  const voteChoices = useMemo(() => {
    if (!voteChoiceField) return [];
    const domain = (voteChoiceField as any).domain;
    if (!isChoiceDomain(domain)) return [];
    return domain.values ?? [];
  }, [voteChoiceField]);

  const [voteSelection, setVoteSelection] = useState<unknown>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const enregistrerVote = async () => {
    if (!actionVote) return;
    if (voteSelection === null || voteSelection === undefined) return;

    // 1) envoyer le vote (avec choiceValue)
    await envoyerAction(
      partieId,
      acteurId,
      attenteType,
      actionVote,
      buildDonnees(actionVote, { acteurId, choiceValue: voteSelection, attenteType }),
      onActionSent
    );

    // 2) si une confirmation existe, l’envoyer ensuite
    if (actionConfirmer) {
      await envoyerAction(
        partieId,
        acteurId,
        attenteType,
        actionConfirmer,
        buildDonnees(actionConfirmer, { acteurId, attenteType }),
        onActionSent
      );
    }
  };
  const cardClass =
    "rounded-card border border-slate-800 bg-slate-950 shadow-carte p-3";

  return (
    <div className={cardClass}>
      <div className="flex items-start justify-between gap-3 mb-2">
        <div>
          {/* Titre retiré car redondant avec l’onglet */}
          <div className="text-xs text-slate-200">
            Les décisions que le cabinet prépare ensemble pour renforcer ses chances de réélection.
          </div>
        </div>
      </div>

      {/* État du vote */}
      {estPhaseVote && (programmeVotes || programmeVerdict !== undefined) && (
        <div className="mb-3 p-2 rounded-lg border border-slate-800 bg-slate-950/60">
          <div className="text-xs font-semibold text-slate-100">Vote des ministres</div>
          <div className="text-[11px] text-slate-300 mt-1">
            <div className="text-[11px] text-slate-400">
              Chaque ministre se prononce sur les mesures à l’agenda.
            </div>
            {programmeVotes && Object.keys(programmeVotes).length > 0 ? (
              <div className="flex flex-col gap-1">
                <div>
                  Votes reçus :{" "}
                  <span className="text-slate-100">
                    {Object.keys(programmeVotes).length}
                  </span>
                </div>
                <div className="text-[11px] text-slate-400">
                  {Object.entries(programmeVotes)
                    .map(([jid, v]) => `${nomJoueur(jid)}:${v}`)
                    .join(" · ")}
                </div>
              </div>
            ) : (
              <div>Les votes n’ont pas encore commencé.</div>
            )}
            {typeof programmeVerdict === "boolean" && (
              <div className="mt-1">
                Verdict :{" "}
                <span className={programmeVerdict ? "text-emerald-300" : "text-rose-300"}>
                  {programmeVerdict ? "accepté" : "rejeté"}
                </span>
              </div>
            )}
          </div>

          {/* CTA vote / confirmation (mobile-first) */}
          <div className="mt-2 flex flex-col gap-2">
            {error && (
              <div className="text-[11px] text-rose-300 border border-rose-900/50 bg-rose-950/40 rounded-lg px-2 py-1">
                {error}
              </div>
            )}

            {actionVote && (
              <div className="flex flex-col gap-2">
                {voteChoices.length > 0 && (
                  <div className="flex flex-wrap gap-2">
                    {voteChoices.map((c: any, idx: number) => {
                      const label = c.label ?? String(c.value ?? c);
                      const value = c.value ?? c;
                      const selected = voteSelection === value;
                      return (
                        <button
                          key={idx}
                          type="button"
                          onClick={() => setVoteSelection(value)}
                          className={`px-3 py-2 rounded-lg text-xs border ${
                            selected
                              ? "border-slate-200 bg-slate-200 text-slate-900"
                              : "border-slate-700 bg-slate-900 text-slate-100 hover:bg-slate-800"
                          }`}
                        >
                          {label}
                        </button>
                      );
                    })}
                  </div>
                )}
              </div>
            )}

            {actionConfirmer && (
              <button
                onClick={enregistrerVote}
                disabled={voteSelection === null || voteSelection === undefined}
              >
                Enregistrer mon vote
              </button>
            )}
          </div>
        </div>
      )}

      {/* Cartes engagées */}
      {liste.length === 0 && (
        <div className="text-sm text-slate-200">
          <div className="italic">Aucune mesure n’est encore à l’agenda.</div>
          <div className="mt-1 text-[11px] text-slate-400">
            👉 Proposez une carte ci-dessous pour lancer l’action du gouvernement.
          </div>
        </div>
      )}

      {liste.length > 0 && (
        <div className="space-y-2">
          {liste.map((c, idx) => (
            <div
              key={c.uid ?? `${c.id}-${idx}`}
              className="p-2 border rounded-card border-slate-700 bg-slate-900/80 flex justify-between gap-3"
            >
              <div className="min-w-0">
                <div className="font-semibold text-xs text-slate-100">
                  {c.id}
                </div>
                {c.nom && (
                  <div className="text-[11px] text-slate-300 mt-1 leading-snug line-clamp-2">
                    {c.nom}
                  </div>
                )}
                <div className="text-[11px] text-slate-400 mt-1">
                  {c.auteur_id ? <>Proposé par <span className="text-slate-200">{nomJoueur(c.auteur_id)}</span></> : "Proposé par : ?"}
                  {typeof c.attention_engagee === "number" && (
                    <> · actions engagées : <span className="text-slate-200">{c.attention_engagee}</span></>
                  )}
                </div>

                {Array.isArray(c.details) && c.details.length > 0 && (
                  <ul className="mt-2 list-disc pl-4 text-[11px] text-slate-300 space-y-1">
                    {c.details.map((d, i) => (
                      <li key={i} className="leading-snug">{d}</li>
                    ))}
                  </ul>
                )}
              </div>


              {/* CTA "Retirer" : uniquement l'auteur de l'entrée */}
              <div className="shrink-0 flex flex-col gap-2 min-w-[160px]">
                {actionRetirer && c.uid && c.auteur_id === acteurId ? (
                  <button
                    type="button"
                    disabled={loading}
                    className="px-3 py-2 rounded-lg text-xs font-semibold border border-rougeErable/50 bg-rougeErable/10 text-blancNordique hover:bg-rougeErable/20 disabled:opacity-60"
                    onClick={async () => {
                      setError(null);
                      setLoading(true);
                      try {
                        const donnees = buildDonneesRetirer(actionRetirer, {
                          acteurId,
                          uidEntree: String(c.uid),
                          attenteType,
                        });
                        await envoyerAction(
                          partieId,
                          acteurId,
                          attenteType,
                          actionRetirer,
                          donnees,
                          onActionSent
                        );
                      } catch (e) {
                        setError((e as Error).message);
                      } finally {
                        setLoading(false);
                      }
                    }}
                    title="Retirer cette carte du programme (avant le vote)"
                  >
                    Retirer
                  </button>
                ) : null}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Mobile : duplication des cartes en main + CTA engager / terminer */}
      <div className="mt-3 flex flex-col gap-2">
        {actionEngager && (
          <div className="p-2 rounded-lg border border-slate-800 bg-slate-950/60">
            <div className="text-xs font-semibold text-slate-100">
              Les cartes de {nomActeur}
            </div>
            <div className="text-[11px] text-slate-400 mt-1">
              Voici ce que vous pouvez proposer au gouvernement ce tour-ci.
            </div>

            <div className="mt-2 space-y-2">
              {cartesMain.length === 0 && (
                <div className="text-[11px] text-slate-300 italic">
                  Vous n'avez plus aucune carte en main.
                </div>
              )}

              {cartesMain.map((carte) => (
                <div
                  key={carte.id}
                  className="p-2 rounded-lg border border-slate-700 bg-slate-900/70 flex items-center justify-between gap-2"
                >
                  <div className="min-w-0">
                    <div className="text-[10px] text-slate-300">{carte.id}</div>
                    <div className="text-sm font-semibold text-slate-50 line-clamp-1">
                      {carte.nom}
                    </div>
                    <div className="text-[11px] text-slate-300/80 mt-1">
                      <span className="text-slate-200">{libelleTypeFamille((carte as any).type)}</span>
                      {typeof carte.cout_attention === "number" && carte.cout_attention > 0 && (
                        <> · 🕒 coûte {carte.cout_attention} action(s) ce tour</>
                      )}
                      {typeof carte.cout_cp === "number" && carte.cout_cp > 0 && (
                        <> · ⭐ demande du soutien politique</>
                      )}
                    </div>
                  </div>


                  <div className="shrink-0 flex flex-col items-end gap-2">
                    <button
                      type="button"
                      disabled={loading}
                      className="w-full px-3 py-2 rounded-lg text-xs font-semibold border border-slate-700 bg-slate-900 text-slate-100 hover:bg-slate-800 disabled:opacity-60"
                      onClick={async () => {
                        if (!actionEngager) return;
                        setError(null);
                        setLoading(true);
                        try {
                          const donnees = buildDonnees(actionEngager, { acteurId, selectedCardId: carte.id, attenteType });

                          await envoyerAction(
                            partieId,
                            acteurId,
                            attenteType,
                            actionEngager,
                            donnees,
                            onActionSent
                          );
                        } catch (e) {
                          setError((e as Error).message);
                        } finally {
                          setLoading(false);
                        }
                      }}
                      title="Ajouter cette carte à l’agenda du gouvernement"
                    >
                      Mettre à l’agenda
                    </button>

                    {onVoirCarteDetails ? (
                      <button
                        type="button"
                        disabled={loading}
                        className="w-full px-3 py-2 rounded-lg text-xs border border-slate-700 bg-slate-950/40 text-slate-200 hover:bg-slate-900 disabled:opacity-60"
                        onClick={() => onVoirCarteDetails(carte.id)}
                        title="Voir la carte en détail (onglet Actions)"
                      >
                        Voir la carte
                      </button>
                    ) : null}
                  </div>
                </div>
              ))}
            </div>

            {actionTerminer && (
              <button
                type="button"
                disabled={loading}
                className="mt-3 w-full px-3 py-2 rounded-lg text-sm font-semibold border border-slate-700 bg-slate-900 text-slate-100 hover:bg-slate-800 disabled:opacity-60"
                onClick={async () => {
                  if (!actionTerminer) return;
                  setError(null);
                  setLoading(true);
                  try {
                    const donnees = buildDonnees(actionTerminer, { acteurId, attenteType });
                    await envoyerAction(
                      partieId,
                      acteurId,
                      attenteType,
                      actionTerminer,
                      donnees,
                      onActionSent
                    );
                  } catch (e) {
                    setError((e as Error).message);
                  } finally {
                    setLoading(false);
                  }
                }}
              >
                J’ai fini pour ce tour
              </button>
            )}
            <div className="mt-1 text-[11px] text-slate-400">
              Vos propositions sont faites. Vous laissez la place aux autres ministres.
            </div>
          </div>
        )}
      </div>
    </div>
  );
};


export default ProgrammeView;
