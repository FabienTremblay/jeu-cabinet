# Relance complète du projet — atelier IA local

Date : 2026-05-10

Ce document résume les commandes essentielles pour relancer rapidement :

- l’atelier Linux `atelierdev`
- LM Studio
- les modèles locaux
- Aider
- Codex
- le projet `jeu-cabinet`

---

# 1. Ouvrir une session atelierdev

```bash
su - atelierdev
```

---

# 2. Aller dans le dépôt du projet

```bash
cd ~/workspace/jeu-cabinet
```

---

# 3. Vérifier la branche Git

```bash
git branch --show-current
```

Branche attendue :

```text
essai-codex
```

---

# 4. Vérifier l’état Git

```bash
git status
```

---

# 5. Démarrer LM Studio

```bash
lmstudio
```

---

# 6. Charger le modèle recommandé

```text
qwen2.5-coder-3b-instruct
```

---

# 7. Vérifier les modèles disponibles

```bash
curl -sS http://localhost:1234/v1/models | python3 -m json.tool
```

---

# 8. Tester rapidement le modèle

```bash
lmtest "qwen2.5-coder-3b-instruct"
```

Résultat attendu :

```json
"content": "OK"
```

---

# 9. Variables utilisées par Aider

```bash
export OPENAI_API_BASE=http://localhost:1234/v1
export OPENAI_API_KEY=dummy-api-key
```

---

# 10. Lancer Aider

```bash
aider-lm "qwen2.5-coder-3b-instruct"
```

Ou ciblé :

```bash
aider-lm "qwen2.5-coder-3b-instruct" docs/fichier.md
```

---

# 11. Discipline Aider

- micro-modifications seulement ;
- un seul fichier idéalement ;
- validation humaine obligatoire ;
- inspecter `git diff` avant commit.

---

# 12. Lancer Codex

```bash
cd ~/workspace/jeu-cabinet

codex
```

---

# 13. Vérifier les derniers commits

```bash
git log --oneline -5
```

---

# 14. Voir les modifications

```bash
git diff
```

Ou :

```bash
git diff -- NOM_FICHIER
```

---

# 15. Voir les fichiers modifiés

```bash
git status --short
```

---

# 16. Prévisualiser un nouveau fichier

```bash
git add -N docs/nouveau-fichier.md
git diff -- docs/nouveau-fichier.md
```

---

# 17. Commit manuel

```bash
git add NOM_FICHIER
git commit -m "Description du changement"
```

---

# 18. Push volontaire uniquement

```bash
git push origin essai-codex
```

---

# 19. Restaurer un fichier

```bash
git restore NOM_FICHIER
```

---

# 20. Workflow retenu

```text
Toi
  ↓
Codex
  ↓
(Aider si micro-tâche ciblée)
  ↓
Validation humaine
  ↓
Commit
  ↓
Push volontaire
```

---

# 21. Rappel important

Ne jamais travailler directement sur :

```text
main
```

Toujours utiliser :

```text
essai-codex
```
