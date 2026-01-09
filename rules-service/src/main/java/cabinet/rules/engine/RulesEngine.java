// source_fichier: rules-service/src/main/java/cabinet/rules/engine/RulesEngine.java
package cabinet.rules.engine;


import cabinet.rules.api.dto.CommandsResponse;
import cabinet.rules.api.dto.EvalAttenteTermineeRequest;
import cabinet.rules.api.dto.EvalSousPhaseRequest;
import cabinet.rules.api.dto.ValiderUsageCarteRequest;
import cabinet.rules.api.dto.ValidationResponse;

public interface RulesEngine {
    CommandsResponse evalSousPhase(EvalSousPhaseRequest req);
    CommandsResponse evalAttenteTerminee(EvalAttenteTermineeRequest req);
    ValidationResponse validerUsageCarte(ValiderUsageCarteRequest request);
}
