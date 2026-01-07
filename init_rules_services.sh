#!/usr/bin/env bash
set -euo pipefail

ROOT="rules-service"
BASE_JAVA="$ROOT/src/main/java"
BASE_RES="$ROOT/src/main/resources"
PKG_DIR="$BASE_JAVA/cabinet/rules"

timestamp() { date +"%Y%m%d_%H%M%S"; }

echo "== Vérifications =="
if [[ ! -d "$ROOT" ]]; then
  echo "ERREUR: dossier '$ROOT' introuvable. Lance ce script à la racine (où se trouve rules-service/)."
  exit 1
fi

mkdir -p "$PKG_DIR/api/dto" "$PKG_DIR/engine" "$PKG_DIR/model" "$BASE_RES"

echo "== Backup fichiers existants (si présents) =="
if [[ -f "$PKG_DIR/RulesResource.java" ]]; then
  cp "$PKG_DIR/RulesResource.java" "$PKG_DIR/RulesResource.java.bak.$(timestamp)"
  echo "Backup: $PKG_DIR/RulesResource.java -> .bak.*"
fi
if [[ -f "$BASE_RES/application.properties" ]]; then
  cp "$BASE_RES/application.properties" "$BASE_RES/application.properties.bak.$(timestamp)"
  echo "Backup: $BASE_RES/application.properties -> .bak.*"
fi

echo "== Écriture application.properties (ajout non destructif) =="
touch "$BASE_RES/application.properties"

# Ajoute uniquement si absent
append_if_missing () {
  local key="$1"
  local line="$2"
  local file="$3"
  if ! grep -qE "^\s*${key}\s*=" "$file"; then
    echo "$line" >> "$file"
  fi
}

append_if_missing "quarkus.http.port" "quarkus.http.port=8081" "$BASE_RES/application.properties"
append_if_missing "quarkus.smallrye-health.root-path" "quarkus.smallrye-health.root-path=/q/health" "$BASE_RES/application.properties"
append_if_missing "quarkus.log.level" "quarkus.log.level=INFO" "$BASE_RES/application.properties"
append_if_missing "quarkus.log.category.\"cabinet.rules\".level" "quarkus.log.category.\"cabinet.rules\".level=DEBUG" "$BASE_RES/application.properties"
append_if_missing "cab.rules.engine" "cab.rules.engine=mock" "$BASE_RES/application.properties"
append_if_missing "cab.rules.default-version" "cab.rules.default-version=debut_mandat.v1" "$BASE_RES/application.properties"

echo "== DTOs =="
cat > "$PKG_DIR/api/dto/TraceDto.java" <<'EOF'
package cabinet.rules.api.dto;

import java.util.List;
import java.util.Map;

public class TraceDto {
    public String mode;                 // "mock" / "drools"
    public String versionRegles;        // ex: "debut_mandat.v1"
    public List<String> fired;          // règles déclenchées (drools), vide en mock
    public Map<String, Object> meta;    // info additionnelle

    public static TraceDto mock(String versionRegles) {
        TraceDto t = new TraceDto();
        t.mode = "mock";
        t.versionRegles = versionRegles;
        t.fired = List.of();
        t.meta = Map.of();
        return t;
    }
}
EOF

cat > "$PKG_DIR/api/dto/CommandsResponse.java" <<'EOF'
package cabinet.rules.api.dto;

import java.util.List;
import java.util.Map;

public class CommandsResponse {
    // On reste volontairement souple: une "command" est un objet JSON libre (Map)
    public List<Map<String, Object>> commands;
    public TraceDto trace;

    public static CommandsResponse of(List<Map<String, Object>> commands, TraceDto trace) {
        CommandsResponse r = new CommandsResponse();
        r.commands = commands;
        r.trace = trace;
        return r;
    }
}
EOF

cat > "$PKG_DIR/api/dto/ValidationResponse.java" <<'EOF'
package cabinet.rules.api.dto;

import java.util.List;
import java.util.Map;

public class ValidationResponse {
    public boolean ok;
    public List<Map<String, Object>> commandes_cout;
    public TraceDto trace;

    public static ValidationResponse ok(List<Map<String, Object>> commandesCout, TraceDto trace) {
        ValidationResponse r = new ValidationResponse();
        r.ok = true;
        r.commandes_cout = commandesCout;
        r.trace = trace;
        return r;
    }

    public static ValidationResponse refuse(List<Map<String, Object>> commandesCout, TraceDto trace) {
        ValidationResponse r = new ValidationResponse();
        r.ok = false;
        r.commandes_cout = commandesCout;
        r.trace = trace;
        return r;
    }
}
EOF

cat > "$PKG_DIR/api/dto/EvalSousPhaseRequest.java" <<'EOF'
package cabinet.rules.api.dto;

import java.util.Map;

public class EvalSousPhaseRequest {
    public String skin;
    public String version_regles; // conforme à ta payload Python
    public String signal;
    public Map<String, Object> etat_min;
    public Map<String, Object> axes;
    public Map<String, Object> joueurs;
    public Object attente;
    public Object programme;
    public Object opposition;
    public Object analyse_skin;

    // Snapshot complet (au début): utile pour itérations
    public Object etat;
}
EOF

cat > "$PKG_DIR/api/dto/EvalAttenteTermineeRequest.java" <<'EOF'
package cabinet.rules.api.dto;

import java.util.Map;

public class EvalAttenteTermineeRequest {
    public String skin;
    public String version_regles;
    public String type_attente;
    public Map<String, Object> etat_min;
    public Map<String, Object> axes;
    public Map<String, Object> joueurs;
    public Object attente;
    public Object programme;
    public Object opposition;
    public Object analyse_skin;
    public Object etat;
}
EOF

cat > "$PKG_DIR/api/dto/ValiderUsageCarteRequest.java" <<'EOF'
package cabinet.rules.api.dto;

import java.util.Map;

public class ValiderUsageCarteRequest {
    public String skin;
    public String version_regles;
    public Map<String, Object> etat_min;
    public Map<String, Object> axes;
    public Map<String, Object> joueurs;
    public Object attente;
    public Object programme;
    public Object opposition;
    public Object analyse_skin;

    public Object etat;

    // Commande reçue (libre)
    public Map<String, Object> cmd;
}
EOF

echo "== Engine (mock + sélection) =="
cat > "$PKG_DIR/engine/RulesEngine.java" <<'EOF'
package cabinet.rules.engine;

import cabinet.rules.api.dto.*;

public interface RulesEngine {
    CommandsResponse evalSousPhase(EvalSousPhaseRequest req);
    CommandsResponse evalAttenteTerminee(EvalAttenteTermineeRequest req);
    ValidationResponse validerUsageCarte(ValiderUsageCarteRequest req);
}
EOF

cat > "$PKG_DIR/engine/MockRulesEngine.java" <<'EOF'
package cabinet.rules.engine;

import cabinet.rules.api.dto.*;

import java.util.List;
import java.util.Map;

public class MockRulesEngine implements RulesEngine {

    @Override
    public CommandsResponse evalSousPhase(EvalSousPhaseRequest req) {
        String version = (req != null && req.version_regles != null) ? req.version_regles : "dev";
        // Pour l'instant: aucune commande (mock)
        return CommandsResponse.of(List.of(), TraceDto.mock(version));
    }

    @Override
    public CommandsResponse evalAttenteTerminee(EvalAttenteTermineeRequest req) {
        String version = (req != null && req.version_regles != null) ? req.version_regles : "dev";
        // Pour l'instant: aucune commande (mock)
        return CommandsResponse.of(List.of(), TraceDto.mock(version));
    }

    @Override
    public ValidationResponse validerUsageCarte(ValiderUsageCarteRequest req) {
        String version = (req != null && req.version_regles != null) ? req.version_regles : "dev";
        // Par défaut: valide, aucun coût
        return ValidationResponse.ok(List.of(), TraceDto.mock(version));
    }
}
EOF

cat > "$PKG_DIR/engine/RulesEngineProducer.java" <<'EOF'
package cabinet.rules.engine;

import jakarta.enterprise.context.ApplicationScoped;
import jakarta.enterprise.inject.Produces;
import org.eclipse.microprofile.config.inject.ConfigProperty;

@ApplicationScoped
public class RulesEngineProducer {

    @ConfigProperty(name = "cab.rules.engine", defaultValue = "mock")
    String engine;

    @Produces
    @ApplicationScoped
    public RulesEngine rulesEngine() {
        // Pour l'instant, uniquement mock.
        // Plus tard: if ("drools".equals(engine)) return new DroolsRulesEngine(...);
        return new MockRulesEngine();
    }
}
EOF

echo "== API Resource =="
cat > "$PKG_DIR/RulesResource.java" <<'EOF'
package cabinet.rules;

import cabinet.rules.api.dto.*;
import cabinet.rules.engine.RulesEngine;
import jakarta.inject.Inject;
import jakarta.ws.rs.*;
import jakarta.ws.rs.core.MediaType;

@Path("/rules")
@Consumes(MediaType.APPLICATION_JSON)
@Produces(MediaType.APPLICATION_JSON)
public class RulesResource {

    @Inject
    RulesEngine engine;

    @POST
    @Path("/eval/sous-phase")
    public CommandsResponse evalSousPhase(EvalSousPhaseRequest req) {
        return engine.evalSousPhase(req);
    }

    @POST
    @Path("/eval/attente-terminee")
    public CommandsResponse evalAttenteTerminee(EvalAttenteTermineeRequest req) {
        return engine.evalAttenteTerminee(req);
    }

    @POST
    @Path("/eval/valider-usage-carte")
    public ValidationResponse validerUsageCarte(ValiderUsageCarteRequest req) {
        return engine.validerUsageCarte(req);
    }
}
EOF

echo "== Terminé =="
echo "Fichiers générés/modifiés dans: $ROOT"
echo
echo "Prochaines vérifications:"
echo "  1) (dans rules-service) mvn -q test"
echo "  2) mvn -q quarkus:dev  (ou via Docker) et tester:"
echo "     curl -s -X POST http://localhost:8081/rules/eval/sous-phase -H 'Content-Type: application/json' -d '{\"skin\":\"debut_mandat\",\"version_regles\":\"debut_mandat.v1\",\"signal\":\"init_tour\"}' | jq"
echo
echo "NOTE: si compilation échoue, c'est probablement des dépendances Jakarta/REST non présentes dans ton pom.xml."
