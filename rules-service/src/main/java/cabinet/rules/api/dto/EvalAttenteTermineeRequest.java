// source_fichier: rules-service/src/main/java/cabinet/rules/api/dto/EvalAttenteTermineeRequest.java
package cabinet.rules.api.dto;

import com.fasterxml.jackson.annotation.JsonInclude;
import com.fasterxml.jackson.annotation.JsonProperty;

import java.util.Map;

public class EvalAttenteTermineeRequest {
    @JsonInclude(JsonInclude.Include.NON_NULL)
    public String skin;

    @JsonInclude(JsonInclude.Include.NON_NULL)
    public String version_regles;

    public String type_attente;
    public Map<String, Object> etat_min;
    public Map<String, Object> axes;
    public Map<String, Object> joueurs;
    public Object attente;
    public Object programme;
    public Object opposition;

    @JsonProperty("analyse_skin")
    public AnalyseSkinDto analyseSkin;

    public Object etat;
}
