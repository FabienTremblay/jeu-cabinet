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
        // Pour l'instant, uniquement mock.
        // Plus tard: if ("drools".equals(engine)) return new DroolsRulesEngine(...);
        return new MockRulesEngine();
    }
}
