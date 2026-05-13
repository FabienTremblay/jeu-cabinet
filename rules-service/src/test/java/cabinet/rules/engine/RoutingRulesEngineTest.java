package cabinet.rules.engine;

import cabinet.rules.api.dto.AnalyseSkinDto;
import cabinet.rules.api.dto.CommandsResponse;
import cabinet.rules.api.dto.EvalAttenteTermineeRequest;
import cabinet.rules.api.dto.EvalSousPhaseRequest;
import cabinet.rules.api.dto.ValidationResponse;
import cabinet.rules.api.dto.ValiderUsageCarteRequest;
import org.junit.jupiter.api.Test;

import java.util.List;
import java.util.Map;

import static org.junit.jupiter.api.Assertions.assertEquals;

class RoutingRulesEngineTest {

    @Test
    void debut_mandat_bre_v1_route_vers_le_moteur_v1() {
        RecordingRulesEngine mock = new RecordingRulesEngine("mock");
        RecordingRulesEngine v1 = new RecordingRulesEngine("v1");
        RoutingRulesEngine routing = new RoutingRulesEngine(mock, v1);

        ValidationResponse response = routing.validerUsageCarte(reqValidation("debut_mandat_bre", "v1"));

        assertEquals("v1", response.raisons.get(0));
        assertEquals(0, mock.appels);
        assertEquals(1, v1.appels);
    }

    @Test
    void skin_inconnue_route_explicitement_vers_le_mock() {
        RecordingRulesEngine mock = new RecordingRulesEngine("mock");
        RecordingRulesEngine v1 = new RecordingRulesEngine("v1");
        RoutingRulesEngine routing = new RoutingRulesEngine(mock, v1);

        CommandsResponse response = routing.evalSousPhase(reqSousPhase("skin_inconnue", "v1"));

        assertEquals("mock", response.trace.meta.get("moteur"));
        assertEquals(1, mock.appels);
        assertEquals(0, v1.appels);
    }

    @Test
    void version_inconnue_route_explicitement_vers_le_mock() {
        RecordingRulesEngine mock = new RecordingRulesEngine("mock");
        RecordingRulesEngine v1 = new RecordingRulesEngine("v1");
        RoutingRulesEngine routing = new RoutingRulesEngine(mock, v1);

        CommandsResponse response = routing.evalAttenteTerminee(reqAttente("debut_mandat_bre", "v2"));

        assertEquals("mock", response.trace.meta.get("moteur"));
        assertEquals(1, mock.appels);
        assertEquals(0, v1.appels);
    }

    @Test
    void version_regles_ne_route_pas_si_analyse_skin_est_absent() {
        RecordingRulesEngine mock = new RecordingRulesEngine("mock");
        RecordingRulesEngine v1 = new RecordingRulesEngine("v1");
        RoutingRulesEngine routing = new RoutingRulesEngine(mock, v1);
        EvalSousPhaseRequest req = new EvalSousPhaseRequest();
        req.version_regles = "debut_mandat_bre.v1";

        CommandsResponse response = routing.evalSousPhase(req);

        assertEquals("mock", response.trace.meta.get("moteur"));
        assertEquals(1, mock.appels);
        assertEquals(0, v1.appels);
    }

    private static EvalSousPhaseRequest reqSousPhase(String skin, String version) {
        EvalSousPhaseRequest req = new EvalSousPhaseRequest();
        req.analyseSkin = analyseSkin(skin, version);
        return req;
    }

    private static EvalAttenteTermineeRequest reqAttente(String skin, String version) {
        EvalAttenteTermineeRequest req = new EvalAttenteTermineeRequest();
        req.analyseSkin = analyseSkin(skin, version);
        return req;
    }

    private static ValiderUsageCarteRequest reqValidation(String skin, String version) {
        ValiderUsageCarteRequest req = new ValiderUsageCarteRequest();
        req.analyseSkin = analyseSkin(skin, version);
        return req;
    }

    private static AnalyseSkinDto analyseSkin(String skin, String version) {
        AnalyseSkinDto analyseSkin = new AnalyseSkinDto();
        analyseSkin.skin = skin;
        analyseSkin.version = version;
        return analyseSkin;
    }

    private static final class RecordingRulesEngine implements RulesEngine {
        private final String nom;
        private int appels;

        private RecordingRulesEngine(String nom) {
            this.nom = nom;
        }

        @Override
        public CommandsResponse evalSousPhase(EvalSousPhaseRequest req) {
            appels += 1;
            return commandsResponse();
        }

        @Override
        public CommandsResponse evalAttenteTerminee(EvalAttenteTermineeRequest req) {
            appels += 1;
            return commandsResponse();
        }

        @Override
        public ValidationResponse validerUsageCarte(ValiderUsageCarteRequest request) {
            appels += 1;
            ValidationResponse response = new ValidationResponse();
            response.ok = true;
            response.raisons = List.of(nom);
            response.cmd_cout = List.of();
            return response;
        }

        private CommandsResponse commandsResponse() {
            CommandsResponse response = new CommandsResponse();
            response.commands = List.of();
            response.trace = cabinet.rules.api.dto.TraceDto.mock(1, 1, "test", "test", "test");
            response.trace.meta = Map.of("moteur", nom);
            return response;
        }
    }
}
