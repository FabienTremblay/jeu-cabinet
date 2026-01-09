package cabinet.rules.engine;

import cabinet.rules.api.dto.CommandsResponse;
import cabinet.rules.api.dto.EvalAttenteTermineeRequest;
import cabinet.rules.api.dto.EvalSousPhaseRequest;
import cabinet.rules.api.dto.TraceDto;
import cabinet.rules.api.dto.ValiderUsageCarteRequest;
import cabinet.rules.api.dto.ValidationResponse;

import java.util.List;
import java.util.Map;

public class MockRulesEngine implements RulesEngine {

    @Override
    public CommandsResponse evalSousPhase(EvalSousPhaseRequest req) {
        CommandsResponse r = new CommandsResponse();
        r.commands = List.of();
        r.trace = TraceDto.mock(1, 1, "mock", "mock", "mock");
        return r;
    }

    @Override
    public CommandsResponse evalAttenteTerminee(EvalAttenteTermineeRequest req) {
        CommandsResponse r = new CommandsResponse();
        r.commands = List.of();
        r.trace = TraceDto.mock(1, 1, "mock", "mock", "mock");
        return r;
    }

    @Override
    public ValidationResponse validerUsageCarte(ValiderUsageCarteRequest request) {
        ValidationResponse r = new ValidationResponse();
        r.ok = true;
        r.raisons = List.of();
        r.cmd_cout = List.of();
        return r;
    }
}

