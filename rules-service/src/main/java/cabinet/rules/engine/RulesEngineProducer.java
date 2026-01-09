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
        if ("mock".equals(engine)) return new MockRulesEngine();
        // Plus tard: if ("drools".equals(engine)) return new DroolsRulesEngine(...);
        throw new IllegalArgumentException("cab.rules.engine invalide: " + engine);
    }
}
