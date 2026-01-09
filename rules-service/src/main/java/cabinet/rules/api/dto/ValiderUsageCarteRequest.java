package cabinet.rules.api.dto;

import com.fasterxml.jackson.annotation.JsonInclude;
import com.fasterxml.jackson.annotation.JsonProperty;

import java.util.Map;

public class ValiderUsageCarteRequest {

    @JsonProperty("source_fichier")
    @JsonInclude(JsonInclude.Include.NON_NULL)
    public String sourceFichier;

    /** Requis par facts_envelope.schema.json */
    @JsonProperty("analyse_skin")
    public AnalyseSkin analyseSkin;

    /** Requis par facts_envelope.schema.json */
    public Map<String, Object> cmd;

    /** Requis par facts_envelope.schema.json */
    public Map<String, Object> joueurs;

    /** Optionnels mais utilisés partout dans ton modèle */
    @JsonProperty("etat_min")
    @JsonInclude(JsonInclude.Include.NON_NULL)
    public Map<String, Object> etat_min;

    @JsonInclude(JsonInclude.Include.NON_NULL)
    public Map<String, Object> axes;

    @JsonInclude(JsonInclude.Include.NON_NULL)
    public Map<String, Object> trace;

    @JsonInclude(JsonInclude.Include.NON_NULL)
    public Map<String, Object> domains;

    @JsonInclude(JsonInclude.Include.NON_NULL)
    public Map<String, Object> meta;

    public static class AnalyseSkin {
        public String skin;
        public String version;
    }
}

