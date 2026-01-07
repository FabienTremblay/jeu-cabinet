package cabinet.rules.api.dto;

import java.util.List;
import java.util.Map;

public class TraceDto {
    public String mode;                 // "mock" / "drools"
    public String versionRegles;        // ex: "debut_mandat.v1"
    public List<String> fired;          // règles déclenchées (drools), vide en mock
    public Map<String, Object> meta;    // info additionnelle

    public static TraceDto mock(String versionRegles) {
        TraceDto t = new TraceDto();
        t.mode = "mock";
        t.versionRegles = versionRegles;
        t.fired = List.of();
        t.meta = Map.of();
        return t;
    }
}
