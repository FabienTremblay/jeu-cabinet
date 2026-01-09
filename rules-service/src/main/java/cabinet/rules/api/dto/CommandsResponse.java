// source_fichier: rules-service/src/main/java/cabinet/rules/api/dto/CommandsResponse.java
package cabinet.rules.api.dto;

import java.util.List;
import java.util.Map;

public class CommandsResponse {
    /** Schema common: commands */
    public List<Map<String, Object>> commands;

    /** Schema common: trace (objet) */
    public TraceDto trace;
}
