package cabinet.rules.engine;

import cabinet.rules.api.dto.*;

import java.util.List;
import java.util.Map;

public class MockRulesEngine implements RulesEngine {

    @Override
    public CommandsResponse evalSousPhase(EvalSousPhaseRequest req) {
        String version = (req != null && req.version_regles != null) ? req.version_regles : "dev";
        String skin = (req != null ? req.skin : null);
        String signal = (req != null ? req.signal : null);

        TraceDto trace = TraceDto.mock(version);
        // meta est immutable dans TraceDto.mock(), donc on remplace au complet:
        trace.meta = Map.of(
                "skin", skin,
                "signal", signal
        );

        // Preuve de vie: quand le moteur dit "init_tour", on renvoie une commande triviale.
        if ("signal.init_tour".equals(signal)) {
            Map<String, Object> cmd = Map.of(
                    "op", "journal",
                    "payload", Map.of(
                            "message", "BRE mock: signal.init_tour (skin=" + skin + ", version=" + version + ")"
                    )
            );
            return CommandsResponse.of(List.of(cmd), trace);
        }

        // Sinon: aucune commande (mock)
        return CommandsResponse.of(List.of(), trace);
    }

    @Override
    public CommandsResponse evalAttenteTerminee(EvalAttenteTermineeRequest req) {
        String version = (req != null && req.version_regles != null) ? req.version_regles : "dev";
        String skin = (req != null) ? req.skin : null;
        String typeAttente = (req != null) ? req.type_attente : null;

        TraceDto trace = TraceDto.mock(version);
        trace.meta = Map.of(
                "skin", skin,
                "type_attente", typeAttente
        );

        // Preuve de vie BRE : attente terminée
        if (typeAttente != null && !typeAttente.isBlank()) {
            Map<String, Object> cmd = Map.of(
                    "op", "journal",
                    "payload", Map.of(
                            "message",
                            "BRE mock: attente-terminee (type=" + typeAttente +
                            ", skin=" + skin +
                            ", version=" + version + ")"
                    )
            );
            return CommandsResponse.of(List.of(cmd), trace);
        }

        return CommandsResponse.of(List.of(), trace);
    }

    @Override
    public ValidationResponse validerUsageCarte(ValiderUsageCarteRequest req) {
        String version = (req != null && req.version_regles != null) ? req.version_regles : "dev";
        // Par défaut: valide, aucun coût
        return ValidationResponse.ok(List.of(), TraceDto.mock(version));
    }
}
