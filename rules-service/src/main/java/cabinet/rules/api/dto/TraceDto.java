package cabinet.rules.api.dto;

import com.fasterxml.jackson.annotation.JsonInclude;

import java.util.Map;

public class TraceDto {
    public int journee;
    public int tour;
    public String phase;
    public String sous_phase;
    public String pivot;

    @JsonInclude(JsonInclude.Include.NON_NULL)
    public Map<String, Object> meta;

    public static TraceDto mock(int journee, int tour, String phase, String sousPhase, String pivot) {
        TraceDto t = new TraceDto();
        t.journee = journee;
        t.tour = tour;
        t.phase = phase;
        t.sous_phase = sousPhase;
        t.pivot = pivot;
        t.meta = Map.of("mode", "mock");
        return t;
    }
}

