// /rules-service/src/main/java/cabinet/rules/engine/RoutingRulesEngine.java
package cabinet.rules.engine;

import cabinet.rules.api.dto.*;
import jakarta.enterprise.inject.Vetoed;

@Vetoed
public class RoutingRulesEngine implements RulesEngine {


    private final RulesEngine mock;
    private final RulesEngine v1;

    public RoutingRulesEngine(RulesEngine mock, RulesEngine v1) {
        this.mock = mock;
        this.v1 = v1;
    }

    @Override
    public CommandsResponse evalSousPhase(EvalSousPhaseRequest req) {
        // choix par skin via version_regles (issu de config.py côté moteur)
        if (req != null && req.version_regles != null && req.version_regles.endsWith(".v1")) {
            return v1.evalSousPhase(req);
        }
        return mock.evalSousPhase(req);
    }

    @Override
    public CommandsResponse evalAttenteTerminee(EvalAttenteTermineeRequest req) {
        if (req != null && req.version_regles != null && req.version_regles.endsWith(".v1")) {
            return v1.evalAttenteTerminee(req);
        }
        return mock.evalAttenteTerminee(req);
    }

    @Override
    public ValidationResponse validerUsageCarte(ValiderUsageCarteRequest req) {
        if (req != null && req.analyseSkin != null
                && "debut_mandat".equals(req.analyseSkin.skin)
                && "v1".equals(req.analyseSkin.version)) {
            return v1.validerUsageCarte(req);
        }
        return mock.validerUsageCarte(req);
    }
}

