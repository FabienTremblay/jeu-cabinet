package cabinet.rules;

import cabinet.rules.api.dto.*;
import cabinet.rules.engine.RulesEngine;
import jakarta.inject.Inject;
import jakarta.ws.rs.*;
import jakarta.ws.rs.core.MediaType;
import org.jboss.logging.Logger;

@Path("/rules")
@Consumes(MediaType.APPLICATION_JSON)
@Produces(MediaType.APPLICATION_JSON)
public class RulesResource {

    private static final Logger LOG = Logger.getLogger(RulesResource.class);


    @Inject
    RulesEngine engine;

    @POST
    @Path("/eval/sous-phase")
    public CommandsResponse evalSousPhase(EvalSousPhaseRequest req) {
        LOG.infof("evalSousPhase skin=%s version=%s signal=%s",
                (req != null ? req.skin : null),
                (req != null ? req.version_regles : null),
                (req != null ? req.signal : null));
        return engine.evalSousPhase(req);
    }

    @POST
    @Path("/eval/attente-terminee")
    public CommandsResponse evalAttenteTerminee(EvalAttenteTermineeRequest req) {
        LOG.infof("evalAttenteTerminee skin=%s version=%s type_attente=%s",
                (req != null ? req.skin : null),
                (req != null ? req.version_regles : null),
                (req != null ? req.type_attente : null));
        return engine.evalAttenteTerminee(req);
    }

    @POST
    @Path("/eval/valider-usage-carte")
    public ValidationResponse validerUsageCarte(ValiderUsageCarteRequest req) {
        LOG.infof("validerUsageCarte skin=%s version=%s cmd.op=%s",
                (req != null ? req.skin : null),
                (req != null ? req.version_regles : null),
                (req != null && req.cmd != null ? req.cmd.get("op") : null));
        return engine.validerUsageCarte(req);
    }
}
