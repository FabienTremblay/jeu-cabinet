# =========================
# Build stage
# =========================
FROM maven:3.9-eclipse-temurin-21 AS build
WORKDIR /workspace

# Cache deps
COPY pom.xml ./
RUN mvn -B -q -e -DskipTests dependency:go-offline

# Copier les sources (inclut src/main/resources/rules)
COPY src ./src

# Compiler / packager Quarkus (fast-jar par défaut)
RUN mvn -B -q -e -DskipTests package

# =========================
# Runtime stage
# =========================
FROM eclipse-temurin:21-jre
WORKDIR /app

# Quarkus fast-jar layout
COPY --from=build /workspace/target/quarkus-app/ /app/

EXPOSE 8081
CMD ["java", "-jar", "/app/quarkus-run.jar"]

