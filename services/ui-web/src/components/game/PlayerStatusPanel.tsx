// src/components/game/PlayerStatusPanel.tsx
import React, { useEffect, useMemo, useState } from "react";

type JoueurStatusRow = {
  id: string;
  alias: string;
  role?: string;
  pret?: boolean;
  capital_politique?: number;
  poids_vote?: number;
};

type PlayerStatusPanelProps = {
  joueurs: JoueurStatusRow[];
  tour?: number | null;
  capitalCollectif?: number | null;
  capitalOpposition?: number | null;

  // pour calculer une tendance fiable (snapshot par partie/joueur)
  partieId?: string;
  joueurId?: string;

  axes?: Record<string, number> | null;
  budget?: {
    dette?: number | null;
    recettes_total?: number | null;
    depenses_total?: number | null;
    interets?: number | null;
    taux_interet?: number | null;
    recettes?: Record<string, number> | null;
    depenses?: Record<string, number> | null;

  } | null;

};

function normaliserJoueurs(input: PlayerStatusPanelProps["joueurs"]): JoueurStatusRow[] {
  if (!input) return [];

  if (Array.isArray(input)) {
    return input.map((j, idx) => ({
      id: (j as any).id ?? String(idx),
      alias:
        (j as any).alias ??
        (j as any).nom ??
        (j as any).donnees_skin?.alias ??
        (j as any).id ??
        `Joueur ${idx + 1}`,
      role: (j as any).role ?? (j as any).donnees_skin?.role ?? undefined,
      pret: (j as any).pret ?? (j as any).donnees_skin?.pret ?? undefined,
      capital_politique:
        typeof (j as any).capital_politique === "number"
          ? (j as any).capital_politique
          : typeof (j as any).capital_politique?.valeur === "number"
          ? (j as any).capital_politique.valeur
          : undefined,
      poids_vote: (j as any).poids_vote ?? (j as any).donnees_skin?.poids_vote ?? undefined,
    }));
  }

  return Object.entries(input as any).map(([id, j]: [string, any]) => ({
    id,
    alias: j.alias ?? j.nom ?? j.donnees_skin?.alias ?? id,
    role: j.role ?? j.donnees_skin?.role,
    pret: j.pret ?? j.donnees_skin?.pret,
    capital_politique:
      typeof j.capital_politique === "number"
        ? j.capital_politique
        : typeof j.capital_politique?.valeur === "number"
        ? j.capital_politique.valeur
        : undefined,
    poids_vote: j.poids_vote ?? j.donnees_skin?.poids_vote,
  }));
}

type SnapshotVictoire = { tour: number; cabinet: number; opposition: number };

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

function signed(n: number) {
  return n > 0 ? `+${n}` : `${n}`;
}
function fmt(n: number | null | undefined) {
  if (typeof n !== "number" || Number.isNaN(n)) return "—";
  return String(n);
}

function fmtMoney(n: number | null | undefined) {
  if (typeof n !== "number" || Number.isNaN(n)) return "—";
  // politique : pas de cents → arrondi à l’unité + séparateurs
  const v = Math.round(n);
  const abs = Math.abs(v);
  const s = new Intl.NumberFormat("fr-CA", { maximumFractionDigits: 0 }).format(abs);
  return v > 0 ? `+${s}` : v < 0 ? `-${s}` : "0";
 }
 
function sumRecord(rec: Record<string, number> | null | undefined): number {
  if (!rec) return 0;
  return Object.values(rec).reduce((s, v) => s + (typeof v === "number" && Number.isFinite(v) ? v : 0), 0);
}

function clamp01(x: number) {
  if (!Number.isFinite(x)) return 0;
  if (x < 0) return 0;
  if (x > 1) return 1;
  return x;
}

function fmtPct(x: number) {
  if (!Number.isFinite(x)) return "—";
  return `${Math.round(x * 100)}%`;
}

type Slice = { label: string; value: number };

function PieDonut({ title, slices, totalLabel }: { title: string; slices: Slice[]; totalLabel?: string }) {
  const total = slices.reduce((s, x) => s + (Number.isFinite(x.value) ? x.value : 0), 0);
  const R = 24;
  const C = 2 * Math.PI * R;
  if (!slices.length || total <= 0) return null;
  let offset = 0;
  return (
    <div className="rounded-card border border-white/10 bg-black/10 px-4 py-3">
      <div className="text-[10px] uppercase tracking-wide text-blancNordique/60">{title}</div>
      <div className="mt-2 flex items-center gap-3">
        <svg width="70" height="70" viewBox="0 0 70 70" className="shrink-0">
          <g transform="translate(35,35)">
            <circle r={R} fill="none" stroke="rgba(255,255,255,0.10)" strokeWidth="10" />
            {slices.map((sl, idx) => {
              const frac = clamp01(sl.value / total);
              const len = frac * C;
              const dasharray = `${len} ${C - len}`;
              const strokeDashoffset = -offset;
              offset += len;
              const alpha = 0.80 - (idx % 4) * 0.12;
              return (
                <circle
                  key={sl.label}
                  r={R}
                  fill="none"
                  stroke={`rgba(255,255,255,${alpha})`}
                  strokeWidth="10"
                  strokeDasharray={dasharray}
                  strokeDashoffset={strokeDashoffset}
                  transform="rotate(-90)"
                />
              );
            })}
            <circle r="15" fill="rgba(0,0,0,0.35)" />
            <text x="0" y="4" textAnchor="middle" fontSize="10" fill="rgba(255,255,255,0.85)">
              {fmtMoney(total)}
            </text>
          </g>
        </svg>

        <div className="min-w-0 flex-1">
          {totalLabel ? <div className="text-[11px] text-blancNordique/70 mb-1">{totalLabel}</div> : null}
          <ul className="space-y-1">
            {slices
              .slice()
              .sort((a, b) => Math.abs(b.value) - Math.abs(a.value))
              .slice(0, 6)
              .map((sl) => (
                <li key={sl.label} className="text-[11px] text-blancNordique/85 flex justify-between gap-2">
                  <span className="truncate">{sl.label}</span>
                  <span className="shrink-0 text-blancNordique/70">
                    {fmtMoney(sl.value)} · {fmtPct(sl.value / total)}
                  </span>
                </li>
              ))}
          </ul>
        </div>
      </div>
    </div>
  );
}


function nomAxe(id: string) {
  const map: Record<string, string> = {
    social: "social",
    economique: "économique",
    environnement: "environnement",
    institutionnel: "institutionnel",
  };
  return map[id] ?? id;
}

const PlayerStatusPanel: React.FC<PlayerStatusPanelProps> = ({
  joueurs,
  tour,
  capitalCollectif,
  capitalOpposition,
  partieId,
  joueurId,
  axes,
  budget,
}) => {
  const rows = normaliserJoueurs(joueurs);

  const t = typeof tour === "number" ? tour : null;
  const cab = typeof capitalCollectif === "number" ? capitalCollectif : 0;
  const opp = typeof capitalOpposition === "number" ? capitalOpposition : 0;

  // Heuristique (simple, stable) : on raffinera plus tard avec des seuils du skin
  const victoireEnPeril = cab <= 0 || opp >= cab;
  const victoireNonAssuree = !victoireEnPeril && (cab <= 1 || opp === cab - 1);

  const statutGlobal: "ok" | "warning" | "bad" = victoireEnPeril
    ? "bad"
    : victoireNonAssuree
    ? "warning"
    : "ok";

  // --- Tendance : delta vs snapshot du tour précédent (localStorage) ---
  const storageKey = useMemo(() => {
    if (!partieId || !joueurId) return null;
    return `cab.victoire.snapshot:${joueurId}:${partieId}`;
  }, [joueurId, partieId]);

  const [delta, setDelta] = useState<{ dCab: number; dOpp: number } | null>(null);

  useEffect(() => {
    if (!storageKey) return;
    if (t == null) return;

    const raw = localStorage.getItem(storageKey);
    let prev: SnapshotVictoire | null = null;
    try {
      prev = raw ? (JSON.parse(raw) as SnapshotVictoire) : null;
    } catch {
      prev = null;
    }

    // delta uniquement si on a vraiment changé de tour
    if (prev && typeof prev.tour === "number" && prev.tour !== t) {
      setDelta({ dCab: cab - prev.cabinet, dOpp: opp - prev.opposition });
    } else {
      setDelta(null);
    }

    const snap: SnapshotVictoire = { tour: t, cabinet: cab, opposition: opp };
    localStorage.setItem(storageKey, JSON.stringify(snap));
  }, [storageKey, t, cab, opp]);

  const lignesConditions = useMemo(() => {
    // Ces “conditions” sont volontairement génériques (priorité 1)
    // On pourra les rendre paramétrables par skin plus tard.
    const conditions = [
      {
        id: "cabinet",
        label: "capital collectif du cabinet",
        statut: cab >= 2 ? "ok" : cab >= 1 ? "warning" : "bad",
        detail: `valeur ${cab}`,
      },
      {
        id: "opposition",
        label: "pression de l’opposition",
        statut: opp <= cab - 2 ? "ok" : opp <= cab - 1 ? "warning" : "bad",
        detail: `valeur ${opp}`,
      },
    ] as Array<{ id: string; label: string; statut: "ok" | "warning" | "bad"; detail: string }>;

    const reunies = conditions.filter((c) => c.statut === "ok");
    const fragiles = conditions.filter((c) => c.statut === "warning");
    const derives = conditions.filter((c) => c.statut === "bad");

    return { reunies, fragiles, derives };
  }, [cab, opp]);

  const resumeTendance = useMemo(() => {
    if (!delta) return null;
    const parts: string[] = [];
    if (delta.dCab !== 0) parts.push(`cabinet ${signed(delta.dCab)}`);
    if (delta.dOpp !== 0) parts.push(`opposition ${signed(delta.dOpp)}`);
    return parts.length ? `ce tour-ci : ${parts.join(" · ")}` : "ce tour-ci : stable";
  }, [delta]);

  // victoire personnelle : rang PM potentiel
  const pm = useMemo(() => {
    if (!joueurId || rows.length === 0) return null;
    const scored = rows
      .map((r) => ({
        id: r.id,
        alias: r.alias,
        cap: typeof r.capital_politique === "number" ? r.capital_politique : -999999,
        pv: typeof r.poids_vote === "number" ? r.poids_vote : 0,
      }))
      .sort((a, b) => (b.cap - a.cap) || (b.pv - a.pv));

    const idx = scored.findIndex((x) => x.id === joueurId);
    if (idx < 0) return null;
    const leader = scored[0];
    const me = scored[idx];
    return {
      rang: idx + 1,
      total: scored.length,
      cap: me.cap,
      leaderAlias: leader?.alias ?? "—",
      ecart: (leader ? me.cap - leader.cap : 0),
    };
  }, [rows, joueurId]);


  return (
    <div className="space-y-4 md:space-y-5">
      {/* Bloc Victoire (lecture interprétée) */}
      <div className={"rounded-card border px-4 py-4 md:px-5 md:py-5 " + classStatut(statutGlobal)}>
        <div className="flex flex-col md:flex-row md:items-start md:justify-between gap-3 md:gap-6">
          <div className="min-w-0">
            <div className="text-[11px] uppercase tracking-wide text-blancNordique/70">
              Victoire
            </div>

            <div className="text-base md:text-lg font-semibold text-blancNordique mt-1">
              {labelStatut(statutGlobal)}
            </div>

            <div className="text-sm text-blancNordique/75 mt-1">
              Tour {t ?? "?"} · cabinet <span className="font-semibold">{cab}</span> · opposition{" "}
              <span className="font-semibold">{opp}</span>
              {resumeTendance ? <span className="ml-2">— {resumeTendance}</span> : null}
            </div>
          </div>

            {pm ? (
              <div className="mt-2 text-sm text-blancNordique/80">
                PM potentiel : <span className="font-semibold">#{pm.rang}</span>/{pm.total} · capital{" "}
                <span className="font-semibold">{pm.cap}</span>
                {pm.rang === 1 ? (
                  <span className="ml-2 text-blancNordique/70">— tu mènes la course</span>
                ) : (
                  <span className="ml-2 text-blancNordique/70">
                    — écart vs #1 ({pm.leaderAlias}) : <span className="font-semibold">{pm.ecart > 0 ? `+${pm.ecart}` : `${pm.ecart}`}</span>
                  </span>
                )}
              </div>
            ) : null}

          <div className="md:text-right">
            <div className="text-[10px] uppercase tracking-wide text-blancNordique/60">
              recommandation
            </div>
            <div className="text-sm text-blancNordique/85 mt-1">
              {statutGlobal === "bad"
                ? "reprendre l’initiative rapidement"
                : statutGlobal === "warning"
                ? "consolider le cabinet"
                : "maintenir la dynamique"}
            </div>
          </div>
        </div>

        {/* Conditions */}
        <div className="mt-4 grid grid-cols-1 lg:grid-cols-2 gap-3">
          <div className="rounded-card border border-white/10 bg-black/15 px-4 py-3">
            <div className="text-[10px] uppercase tracking-wide text-blancNordique/60">
              conditions réunies
            </div>
            {lignesConditions.reunies.length === 0 ? (
              <div className="text-sm text-blancNordique/70 mt-2">aucune</div>
            ) : (
              <ul className="mt-2 space-y-1.5">
                {lignesConditions.reunies.map((c) => (
                  <li key={c.id} className="text-sm text-blancNordique/85">
                    ✔ {c.label} <span className="text-blancNordique/60">({c.detail})</span>
                  </li>
                ))}
              </ul>
            )}
          </div>

          <div className="rounded-card border border-white/10 bg-black/15 px-4 py-3">
            <div className="text-[10px] uppercase tracking-wide text-blancNordique/60">
              conditions qui dérivent
            </div>
            {lignesConditions.derives.length === 0 && lignesConditions.fragiles.length === 0 ? (
              <div className="text-sm text-blancNordique/70 mt-2">aucune</div>
            ) : (
              <ul className="mt-2 space-y-1.5">
                {lignesConditions.derives.map((c) => (
                  <li key={c.id} className="text-sm text-blancNordique/85">
                    ✖ {c.label} <span className="text-blancNordique/60">({c.detail})</span>
                  </li>
                ))}
                {lignesConditions.fragiles.map((c) => (
                  <li key={c.id} className="text-sm text-blancNordique/85">
                    ⚠ {c.label} <span className="text-blancNordique/60">({c.detail})</span>
                  </li>
                ))}
              </ul>
            )}
          </div>
        </div>

        {/* Indicateurs saillants : axes + budget */}
        <VictoireSaillants axes={axes} budget={budget} />
      </div>

      {/* Panneau joueurs (inchangé, mais on retire le mini-palmarès redondant) */}
      <div className="flex justify-between items-baseline">
        <h2 className="font-semibold text-sm">Joueurs</h2>
        <span className="text-xs opacity-70">Tour {t ?? "?"}</span>
      </div>

      {rows.length === 0 ? (
        <p className="text-xs opacity-60">Aucun joueur pour l’instant.</p>
      ) : (
        <ul className="space-y-2 text-sm">
          {rows.map((j) => (
            <li
              key={j.id}
              className="flex items-center justify-between border rounded border-slate-700 px-2 py-1"
            >
              <div>
                <div className="font-medium">
                  {j.alias} {j.role ? `(${j.role})` : null}
                </div>
                <div className="text-xs opacity-70">
                  Capital politique{" "}
                  <span className="font-semibold">{j.capital_politique ?? "?"}</span>
                  {typeof j.poids_vote === "number" && (
                    <>
                      {" "}
                      · poids de vote <span className="font-semibold">{j.poids_vote}</span>
                    </>
                  )}
                </div>
              </div>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
};

function VictoireSaillants({
  axes,
  budget,
}: {
  axes?: Record<string, number> | null;
  budget?: {
    dette?: number | null;
    recettes_total?: number | null;
    depenses_total?: number | null;
    interets?: number | null;
    taux_interet?: number | null;
    recettes?: Record<string, number> | null;
    depenses?: Record<string, number> | null;
  } | null;
}) {
  const axesEntries = useMemo(() => {
    if (!axes) return [];
    return Object.entries(axes)
      .filter(([, v]) => typeof v === "number" && !Number.isNaN(v))
      .sort((a, b) => b[1] - a[1]);
  }, [axes]);

  const best = axesEntries[0] ?? null;
  const worst = axesEntries[axesEntries.length - 1] ?? null;

  const showAxes = !!(best && worst && axesEntries.length > 0);
  const showBudget =
    budget &&
    (typeof budget.dette === "number" ||
      typeof budget.recettes_total === "number" ||
      typeof budget.depenses_total === "number" ||
      (budget.recettes && Object.keys(budget.recettes).length > 0) ||
      (budget.depenses && Object.keys(budget.depenses).length > 0) ||
      typeof budget.interets === "number");

  if (!showAxes && !showBudget) return null;

  return (
    <div className="mt-4 grid grid-cols-1 lg:grid-cols-2 gap-3">
      {showAxes ? (
        <div className="rounded-card border border-white/10 bg-black/10 px-4 py-3">
          <div className="text-[10px] uppercase tracking-wide text-blancNordique/60">
            axes saillants
          </div>
          <div className="mt-2 space-y-1.5 text-sm text-blancNordique/85">
            <div>
              ▲ {nomAxe(best![0])} <span className="text-blancNordique/60">({fmt(best![1])})</span>
            </div>
            <div>
              ▼ {nomAxe(worst![0])} <span className="text-blancNordique/60">({fmt(worst![1])})</span>
            </div>
          </div>
        </div>
      ) : null}

      {showBudget ? (
        <>
          {(() => {
            const joliPoste = (k: string) => {
              const KNOWN: Record<string, string> = {
                impot_part: "impôts (particuliers)",
                impot_ent: "impôts (entreprises)",
                tps: "tps",
                tvq: "tvq",
                droits: "droits et permis",
                transferts: "transferts",
              };
              return KNOWN[k] ?? k.replace(/_/g, " ");
            };

            const recTot =
              typeof budget?.recettes_total === "number" ? budget!.recettes_total! : sumRecord(budget?.recettes);
            const depTot =
              typeof budget?.depenses_total === "number" ? budget!.depenses_total! : sumRecord(budget?.depenses);
            const interets = typeof budget?.interets === "number" ? budget!.interets! : 0;
            const dette = typeof budget?.dette === "number" ? budget!.dette! : null;

            // Résultat budgétaire du tour (hors tarte) : déficit si positif, surplus si négatif
            const resultat = (depTot + interets) - recTot;

            // Tarte dépenses : dépenses effectives (programmes + intérêts). PAS de déficit ici.
            const depProgrammes = Math.max(depTot, 0);
            const depSlices: Slice[] = [
              { label: "dépenses programmes", value: depProgrammes },
              { label: "service de la dette (intérêts)", value: Math.max(interets, 0) },
            ].filter((x) => x.value > 0);

            // Tarte recettes : breakdown si présent, sinon total
            const recObj = budget?.recettes ?? null;
            const recSlices: Slice[] =
              recObj && Object.keys(recObj).length
                ? Object.entries(recObj)
                    .filter(([, v]) => typeof v === "number" && Number.isFinite(v) && v !== 0)
                    .map(([k, v]) => ({ label: joliPoste(k), value: v }))
                : [{ label: "recettes", value: recTot }].filter((x) => x.value > 0);

            return (
              <>
                <div className="rounded-card border border-white/10 bg-black/10 px-4 py-3">
                  <div className="text-[10px] uppercase tracking-wide text-blancNordique/60">
                    budget saillant
                  </div>
                  <div className="mt-2 grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-2 text-sm text-blancNordique/85">
                    <div>
                      <div className="text-[10px] uppercase tracking-wide text-blancNordique/60">recettes</div>
                      <div className="mt-1 font-semibold">{fmtMoney(recTot)}</div>
                    </div>
                    <div>
                      <div className="text-[10px] uppercase tracking-wide text-blancNordique/60">dépenses (programmes)</div>
                      <div className="mt-1 font-semibold">{fmtMoney(depTot)}</div>
                    </div>
                    <div>
                      <div className="text-[10px] uppercase tracking-wide text-blancNordique/60">intérêts</div>
                      <div className="mt-1 font-semibold">{fmtMoney(interets)}</div>
                    </div>
                    <div>
                      <div className="text-[10px] uppercase tracking-wide text-blancNordique/60">résultat</div>
                      <div className="mt-1 font-semibold">
                        {resultat > 0 ? `déficit ${fmtMoney(resultat)}` : resultat < 0 ? `surplus ${fmtMoney(-resultat)}` : "équilibre"}
                      </div>
                    </div>
                    <div>
                      <div className="text-[10px] uppercase tracking-wide text-blancNordique/60">dette</div>
                      <div className="mt-1 font-semibold">{fmtMoney(dette)}</div>
                    </div>
                  </div>
                </div>

                <PieDonut title="budget — dépenses effectives" slices={depSlices} totalLabel="programmes + intérêts" />
                <PieDonut title="budget — recettes" slices={recSlices} totalLabel="répartition des recettes" />
              </>
            );
          })()}
        </>
      ) : null}
    </div>
  );
}

export default PlayerStatusPanel;

