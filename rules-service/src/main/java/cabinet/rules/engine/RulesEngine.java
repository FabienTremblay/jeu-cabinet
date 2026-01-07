package cabinet.rules.engine;

import cabinet.rules.api.dto.*;

public interface RulesEngine {
    CommandsResponse evalSousPhase(EvalSousPhaseRequest req);
    CommandsResponse evalAttenteTerminee(EvalAttenteTermineeRequest req);
    ValidationResponse validerUsageCarte(ValiderUsageCarteRequest req);
}
