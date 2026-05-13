# Tests Java Du Rules-Service

## Objectif

Les tests Java du `rules-service` couvrent notamment :

- le routage BRE par `analyse_skin.skin` et `analyse_skin.version` ;
- la validation minimale de `programme.engager_carte` par le moteur v1.

## Prérequis

- JDK 21 accessible via `JAVA_HOME`.
- `javac` disponible dans le `PATH`.
- Accès réseau au premier lancement du wrapper Maven, pour télécharger Maven
  Wrapper 3.3.2 et Apache Maven 3.9.9.

Un JRE seul ne suffit pas : le service doit compiler du Java, donc il faut un
JDK complet. Maven global n'est pas requis, car le dépôt fournit `./mvnw`.

Le `pom.xml` cible explicitement Java 21 :

```xml
<maven.compiler.release>21</maven.compiler.release>
```

## Vérifier L'environnement

```bash
java -version
javac -version
echo "$JAVA_HOME"
```

Résultat attendu :

- `java -version` indique une version 21 ;
- `javac -version` indique une version 21 ;
- `JAVA_HOME` pointe vers un JDK 21, pas vers un JRE.

## Installation Indicative Ubuntu/Debian

```bash
sudo apt update
sudo apt install openjdk-21-jdk
```

Après installation, vérifier que `JAVA_HOME` pointe vers le JDK 21 si plusieurs
versions de Java coexistent.

## Commande

Depuis la racine du dépôt :

```bash
cd rules-service
./mvnw test
```

Sur Windows :

```bat
cd rules-service
mvnw.cmd test
```

## Wrapper Maven

Le wrapper est local au dossier `rules-service/`.

Fichiers suivis :

- `rules-service/mvnw`
- `rules-service/mvnw.cmd`
- `rules-service/.mvn/wrapper/maven-wrapper.properties`

Le fichier `maven-wrapper.jar` n'est pas versionné. Il est téléchargé au
premier lancement depuis l'URL `wrapperUrl`.

## Limites Connues

L'environnement courant de développement ne fournit que Java 8 et ne fournit
pas `javac`. Les tests Java ne peuvent donc pas y être exécutés tant qu'un JDK
21 n'est pas installé ou exposé via `JAVA_HOME`.

Résultat observé localement :

```text
./mvnw test
...
[ERROR] No compiler is provided in this environment.
Perhaps you are running on a JRE rather than a JDK?
```
