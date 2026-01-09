package cabinet.rules;

import io.quarkus.test.junit.QuarkusTest;
import org.junit.jupiter.api.Test;

import java.io.InputStream;
import java.nio.charset.StandardCharsets;

import static io.restassured.RestAssured.given;
import static org.hamcrest.Matchers.*;

@QuarkusTest
public class ValiderUsageCarteV1Test {

    @Test
    void valider_usage_carte_ok() throws Exception {
        String json = readResource("/fixtures/valider_usage_carte_ok.json");

        given()
          .contentType("application/json")
          .body(json)
        .when()
          .post("/rules/eval/valider-usage-carte")
        .then()
          .statusCode(200)
          .body("ok", is(true))
          .body("raisons", hasSize(0))
          .body("cmd_cout", hasSize(2))
          .body("cmd_cout[0].op", notNullValue());
    }

    private static String readResource(String path) throws Exception {
        try (InputStream is = ValiderUsageCarteV1Test.class.getResourceAsStream(path)) {
            if (is == null) throw new IllegalStateException("Missing resource: " + path);
            return new String(is.readAllBytes(), StandardCharsets.UTF_8);
        }
    }
}

