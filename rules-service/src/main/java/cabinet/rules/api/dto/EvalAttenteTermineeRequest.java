package cabinet.rules.api.dto;

import java.util.Map;

public class EvalAttenteTermineeRequest {
    public String skin;
    public String version_regles;
    public String type_attente;
    public Map<String, Object> etat_min;
    public Map<String, Object> axes;
    public Map<String, Object> joueurs;
    public Object attente;
    public Object programme;
    public Object opposition;
    public Object analyse_skin;
    public Object etat;
}
