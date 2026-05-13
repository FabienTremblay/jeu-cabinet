package cabinet.rules.engine;

import cabinet.rules.api.dto.ValidationResponse;
import cabinet.rules.api.dto.ValiderUsageCarteRequest;
import org.junit.jupiter.api.Test;

import java.util.List;
import java.util.Map;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;

class SimpleRulesEngineV1Test {

    private final SimpleRulesEngineV1 moteur = new SimpleRulesEngineV1(new MockRulesEngine());

    @Test
    void carte_valide_retourne_les_couts() {
        ValidationResponse response = moteur.validerUsageCarte(req(2, 3, List.of("C1"), carte("C1", 1, 1)));

        assertTrue(response.ok);
        assertEquals(2, response.cmd_cout.size());
        assertEquals("joueur.attention.delta", response.cmd_cout.get(0).get("op"));
        assertEquals("joueur.capital.delta", response.cmd_cout.get(1).get("op"));
    }

    @Test
    void carte_inexistante_est_refusee() {
        ValidationResponse response = moteur.validerUsageCarte(req(2, 3, List.of("C1"), null));

        assertFalse(response.ok);
        assertEquals(List.of("carte_introuvable"), response.raisons);
    }

    @Test
    void carte_absente_de_la_main_est_refusee() {
        ValidationResponse response = moteur.validerUsageCarte(req(2, 3, List.of("C2"), carte("C1", 1, 1)));

        assertFalse(response.ok);
        assertEquals(List.of("carte_absente_main"), response.raisons);
    }

    @Test
    void attention_insuffisante_est_refusee() {
        ValidationResponse response = moteur.validerUsageCarte(req(0, 3, List.of("C1"), carte("C1", 1, 1)));

        assertFalse(response.ok);
        assertEquals(List.of("attention_insuffisante"), response.raisons);
    }

    @Test
    void capital_politique_insuffisant_est_refuse() {
        ValidationResponse response = moteur.validerUsageCarte(req(2, 0, List.of("C1"), carte("C1", 1, 1)));

        assertFalse(response.ok);
        assertEquals(List.of("capital_politique_insuffisant"), response.raisons);
    }

    private static ValiderUsageCarteRequest req(
            int attentionDispo,
            int capitalPolitique,
            List<String> main,
            Map<String, Object> carte
    ) {
        ValiderUsageCarteRequest req = new ValiderUsageCarteRequest();
        req.cmd = Map.of("op", "programme.engager_carte", "joueur_id", "J1", "carte_id", "C1");
        req.joueurs = Map.of();
        req.etat_min = Map.of(
                "joueurs", Map.of(
                        "J1", Map.of(
                                "id", "J1",
                                "attention_dispo", attentionDispo,
                                "capital_politique", capitalPolitique,
                                "main", main
                        )
                ),
                "cartes_def", carte == null ? Map.of() : Map.of("C1", carte)
        );
        return req;
    }

    private static Map<String, Object> carte(String id, int coutAttention, int coutCp) {
        return Map.of(
                "id", id,
                "type", "mesure",
                "cout_attention", coutAttention,
                "cout_cp", coutCp
        );
    }
}
