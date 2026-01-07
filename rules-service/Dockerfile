# =========================
# Build stage
# =========================
FROM maven:3.9-eclipse-temurin-21 AS build
WORKDIR /workspace

# Copier d'abord les fichiers Maven pour profiter du cache
COPY pom.xml ./
# (optionnel) si tu as un .mvn/ ou mvnw, copie-les ici aussi
# COPY .mvn .mvn
# COPY mvnw ./

# Télécharger les dépendances (cache Docker)
RUN mvn -B -q -e -DskipTests dependency:go-offline

# Copier le code source
COPY src ./src
# Si tu gardes un dossier "rules/" au runtime, copie-le dans l'image (sinon tu peux omettre)
COPY rules ./rules

# Build Quarkus (fast-jar par défaut)
RUN mvn -B -q -DskipTests package

# =========================
# Runtime stage
# =========================
FROM eclipse-temurin:21-jre
WORKDIR /app

# Copier le "fast-jar" Quarkus
COPY --from=build /workspace/target/quarkus-app/ /app/

EXPOSE 8081
# Quarkus fast-jar: le jar de démarrage s'appelle quarkus-run.jar
CMD ["java", "-jar", "/app/quarkus-run.jar"]

