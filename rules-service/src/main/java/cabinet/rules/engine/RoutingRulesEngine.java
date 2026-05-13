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
        if (routeVersDebutMandatBreV1(req != null ? req.analyseSkin : null)) {
            return v1.evalSousPhase(req);
        }
        return mock.evalSousPhase(req);
    }

    @Override
    public CommandsResponse evalAttenteTerminee(EvalAttenteTermineeRequest req) {
        if (routeVersDebutMandatBreV1(req != null ? req.analyseSkin : null)) {
            return v1.evalAttenteTerminee(req);
        }
        return mock.evalAttenteTerminee(req);
    }

    @Override
    public ValidationResponse validerUsageCarte(ValiderUsageCarteRequest req) {
        if (routeVersDebutMandatBreV1(req != null ? req.analyseSkin : null)) {
            return v1.validerUsageCarte(req);
        }
        return mock.validerUsageCarte(req);
    }

    private boolean routeVersDebutMandatBreV1(AnalyseSkinDto analyseSkin) {
        return analyseSkin != null
                && "debut_mandat_bre".equals(analyseSkin.skin)
                && "v1".equals(analyseSkin.version);
    }
}
