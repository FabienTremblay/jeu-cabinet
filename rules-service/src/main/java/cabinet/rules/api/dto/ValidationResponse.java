// source_fichier: rules-service/src/main/java/cabinet/rules/api/dto/ValidationResponse.java
package cabinet.rules.api.dto;

import java.util.List;
import java.util.Map;

public class ValidationResponse {
    public boolean ok;
    public List<String> raisons;
    /** DMN output: cmd_cout */
    public List<Map<String, Object>> cmd_cout;
}

