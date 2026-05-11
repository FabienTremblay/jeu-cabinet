docs/atelierIA/codex-gardien-issues.md.

Objectif :
Documenter le rôle permanent de Codex comme gardien des issues GitHub du projet.

Contenu attendu :

# Codex — Gardien des issues GitHub

## Mission

Codex agit comme secrétaire technique des issues GitHub du projet jeu-cabinet. Il maintient la cohérence entre l’état du dépôt, la documentation, les commits récents et les tickets GitHub.

## Source officielle

GitHub Issues est le registre officiel des tickets.
La documentation dans docs/atelierIA sert de mémoire de travail et de contexte pour les assistants IA.

## Responsabilités

Codex peut :
- lister les issues existantes ;
- créer les issues manquantes ;
- proposer des labels ;
- commenter une issue avec un bilan technique ;
- relier une issue à un commit ;
- proposer la fermeture d’une issue ;
- créer des tickets de dette technique ;
- créer des tickets de tests ou documentation ;
- produire un bilan des tickets ouverts.

## Limites

Codex ne doit pas :
- fermer une issue importante sans validation explicite ;
- supprimer une issue ;
- modifier du code pendant une tâche de maintenance des issues ;
- changer l’architecture du projet ;
- créer des doublons ;
- renommer les conventions du projet ;
- utiliser les issues comme journal bavard.

## Commandes autorisées

Utiliser principalement :

gh issue list --repo FabienTremblay/jeu-cabinet
gh issue view <numero> --repo FabienTremblay/jeu-cabinet
gh issue create --repo FabienTremblay/jeu-cabinet --title ... --body ...
gh issue comment <numero> --repo FabienTremblay/jeu-cabinet --body ...
gh issue edit <numero> --repo FabienTremblay/jeu-cabinet --add-label ...
gh issue close <numero> --repo FabienTremblay/jeu-cabinet --comment ...

La fermeture doit être proposée avant exécution, sauf instruction explicite.

## Convention de titre

Format préféré :

TXX — Verbe à l’infinitif + objet

Exemples :
T13 — Introduire une mécanique de migration SQL
T14 — Automatiser les tests de présence joueur et reprise de session
T15 — Afficher l’état de présence des joueurs à la table

## Structure d’une issue

Chaque issue doit contenir :

- Objectif
- Contexte
- Travaux attendus
- Critères d’acceptation
- Contraintes
- Notes techniques si nécessaire

## Labels recommandés

architecture
backend
frontend
sql
tests
documentation
dette-technique
codex
aider
à-valider

Si un label n’existe pas, Codex peut proposer sa création, mais ne doit pas échouer inutilement.

## Règles de fermeture

Une issue peut être proposée comme terminée si :
- le code ou la documentation correspondant existe ;
- un commit est identifié ;
- les critères d’acceptation sont satisfaits ou explicitement reportés ;
- les limites restantes sont documentées.

Codex doit commenter l’issue avant fermeture avec :
- résumé de la réalisation ;
- commit ou fichier concerné ;
- validation effectuée ;
- reste à faire le cas échéant.

## Rapport attendu lors d’une passe de maintenance

Codex doit produire :
- issues créées ;
- issues existantes non modifiées ;
- issues possiblement terminées ;
- doublons potentiels ;
- prochaines actions recommandées.
