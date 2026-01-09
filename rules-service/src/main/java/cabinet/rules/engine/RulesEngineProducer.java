// source_fichier: rules-service/src/main/java/cabinet/rules/engine/RulesEngineProducer.java
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
        RulesEngine mock = new MockRulesEngine();
        RulesEngine v1   = new SimpleRulesEngineV1(mock);

        // Stratégie recommandée :
        // - "routing" : choix par skin via req.version_regles / req.analyseSkin
        // - "v1"      : force v1 (utile pour tests d’intégration en environnement)
        // - "mock"    : fallback total
        return switch (engine) {
            case "mock"    -> mock;
            case "v1"      -> v1;
            case "routing" -> new RoutingRulesEngine(mock, v1);
            default        -> new RoutingRulesEngine(mock, v1);
        };
     }
}
