// source_fichier: rules-service/src/main/java/cabinet/rules/api/dto/EvalSousPhaseRequest.java
package cabinet.rules.api.dto;

import java.util.Map;

public class EvalSousPhaseRequest {
    public String skin;
    public String version_regles; // conforme à ta payload Python
    public String signal;
    public Map<String, Object> etat_min;
    public Map<String, Object> axes;
    public Map<String, Object> joueurs;
    public Object attente;
    public Object programme;
    public Object opposition;
    public Object analyse_skin;

    // Snapshot complet (au début): utile pour itérations
    public Object etat;
}
