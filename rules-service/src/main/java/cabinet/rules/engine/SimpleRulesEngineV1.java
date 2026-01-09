// source: /rules-service/src/main/java/cabinet/rules/engine/SimpleRulesEngineV1.java
package cabinet.rules.engine;

import cabinet.rules.api.dto.CommandsResponse;
import cabinet.rules.api.dto.EvalAttenteTermineeRequest;
import cabinet.rules.api.dto.EvalSousPhaseRequest;
import cabinet.rules.api.dto.ValidationResponse;
import cabinet.rules.api.dto.ValiderUsageCarteRequest;
import jakarta.enterprise.inject.Vetoed;

import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.Map;

@Vetoed
public class SimpleRulesEngineV1 implements RulesEngine {

  private final RulesEngine fallback;

  public SimpleRulesEngineV1(RulesEngine fallback) {
    this.fallback = fallback;
  }

  @Override
  public CommandsResponse evalSousPhase(EvalSousPhaseRequest req) {
    return fallback.evalSousPhase(req);
  }

  @Override
  public CommandsResponse evalAttenteTerminee(EvalAttenteTermineeRequest req) {
    return fallback.evalAttenteTerminee(req);
  }

  @Override
  public ValidationResponse validerUsageCarte(ValiderUsageCarteRequest req) {
    // Implémentation conforme au DMN 20_valider_action.dmn (valider_usage_carte)

    Map<String, Object> cmd = (req != null ? req.cmd : null);
    if (cmd == null || cmd.get("op") == null) {
      return mk(false, List.of(), List.of());
    }

    String op = String.valueOf(cmd.get("op"));
    if (!"programme.engager_carte".equals(op)) {
      return mk(true, List.of(), List.of());
    }

    String joueurId = asString(cmd.get("joueur_id"));
    String carteId  = asString(cmd.get("carte_id"));
    if (joueurId == null || carteId == null) {
      return mk(false, List.of("cmd_incomplete"), List.of());
    }

    Map<String, Object> joueurs = (req.joueurs != null ? req.joueurs : Collections.emptyMap());
    Object joueurObj = joueurs.get(joueurId);
    if (!(joueurObj instanceof Map)) {
      return mk(false, List.of(), List.of());
    }
    Map<String, Object> joueur = (Map<String, Object>) joueurObj;

    // === Contexte DMN: analyse_skin.cartes_def ===
    // Le contrat v1 n’inclut pas analyse_skin.cartes_def,
    // donc on le dérive de etat_min.cartes_def (si présent).
    Map<String, Object> etatMin = (req.etat_min != null ? req.etat_min : Collections.emptyMap());
    Map<String, Object> cartesDef = Collections.emptyMap();
    if (etatMin.get("cartes_def") instanceof Map) {
      cartesDef = (Map<String, Object>) etatMin.get("cartes_def");
    }

    Object defCarteObj = cartesDef.get(carteId);
    if (!(defCarteObj instanceof Map)) {
      return mk(false, List.of(), List.of());
    }
    Map<String, Object> defCarte = (Map<String, Object>) defCarteObj;

    int coutAtt = asInt(defCarte.get("cout_attention"), 0);
    int coutCp  = asInt(defCarte.get("cout_capital"), 0);
    int attDispo = asInt(joueur.get("attention"), 0);
    int cpDispo  = asInt(joueur.get("capital_politique"), 0);

    if (attDispo < coutAtt || cpDispo < coutCp) {
      return mk(false, List.of(), List.of());
    }

    List<Map<String, Object>> cmds = new ArrayList<>();
    if (coutAtt > 0) {
      cmds.add(Map.of("op","joueur.attention.delta","joueur_id",joueurId,"delta",-coutAtt));
    }
    if (coutCp > 0) {
      cmds.add(Map.of("op","joueur.capital.delta","joueur_id",joueurId,"delta",-coutCp));
    }

    return mk(true, List.of(), cmds);
  }

  private ValidationResponse mk(boolean ok, List<String> raisons, List<Map<String,Object>> cmdCout) {
    ValidationResponse r = new ValidationResponse();
    r.ok = ok;
    r.raisons = raisons;
    r.cmd_cout = cmdCout;
    return r;
  }

  private static String asString(Object v) {
    return v == null ? null : String.valueOf(v);
  }

  private static int asInt(Object v, int def) {
    if (v == null) return def;
    if (v instanceof Number) return ((Number) v).intValue();
    try { return Integer.parseInt(String.valueOf(v)); } catch (Exception e) { return def; }
  }

}

