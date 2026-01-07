package cabinet.rules.api.dto;

import java.util.List;
import java.util.Map;

public class CommandsResponse {
    // On reste volontairement souple: une "command" est un objet JSON libre (Map)
    public List<Map<String, Object>> commands;
    public TraceDto trace;

    public static CommandsResponse of(List<Map<String, Object>> commands, TraceDto trace) {
        CommandsResponse r = new CommandsResponse();
        r.commands = commands;
        r.trace = trace;
        return r;
    }
}
