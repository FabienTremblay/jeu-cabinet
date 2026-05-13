# Tests Java Du Rules-Service

## Objectif

Les tests Java du `rules-service` couvrent notamment :

- le routage BRE par `analyse_skin.skin` et `analyse_skin.version` ;
- la validation minimale de `programme.engager_carte` par le moteur v1.

## Prérequis

- JDK 21 accessible via `JAVA_HOME`.
- Accès réseau au premier lancement du wrapper Maven, pour télécharger Maven
  Wrapper 3.3.2 et Apache Maven 3.9.9.

Le `pom.xml` cible explicitement Java 21 :

```xml
<maven.compiler.release>21</maven.compiler.release>
```

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
