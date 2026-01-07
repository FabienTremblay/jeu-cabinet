package cabinet.rules.api.dto;

import java.util.List;
import java.util.Map;

public class ValidationResponse {
    public boolean ok;
    public List<Map<String, Object>> commandes_cout;
    public TraceDto trace;

    public static ValidationResponse ok(List<Map<String, Object>> commandesCout, TraceDto trace) {
        ValidationResponse r = new ValidationResponse();
        r.ok = true;
        r.commandes_cout = commandesCout;
        r.trace = trace;
        return r;
    }

    public static ValidationResponse refuse(List<Map<String, Object>> commandesCout, TraceDto trace) {
        ValidationResponse r = new ValidationResponse();
        r.ok = false;
        r.commandes_cout = commandesCout;
        r.trace = trace;
        return r;
    }
}
