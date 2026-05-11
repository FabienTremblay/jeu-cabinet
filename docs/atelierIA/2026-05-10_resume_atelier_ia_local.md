# Atelier IA local — résumé des commandes et décisions

Date : 2026-05-10

## Objectif

Construire un atelier IA local isolé sous Linux pour expérimenter :

- Aider
- LM Studio
- modèles locaux
- Codex CLI
- discipline Git sécurisée

Le tout dans un utilisateur Linux dédié (`atelierdev`) et une branche Git d’expérimentation (`essai-codex`).

---

# 1. Création de l’utilisateur Linux dédié

## Création du compte

```bash
sudo adduser atelierdev
```

## Ajout aux groupes utiles

```bash
sudo usermod -aG docker,video,render atelierdev
```

## Vérification

```bash
id atelierdev
```

---

# 2. Préparation de l’environnement atelierdev

## Vérifications

```bash
whoami
pwd
groups
python3 --version
pipx --version
```

---

# 3. Préparation GitHub SSH

## Génération de clé SSH

```bash
ssh-keygen -t ed25519 -C "atelierdev@MaisonNeuve - atelier IA" -f ~/.ssh/id_ed25519_atelierdev
```

## Activation de l’agent SSH

```bash
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_ed25519_atelierdev
```

## Affichage de la clé publique

```bash
cat ~/.ssh/id_ed25519_atelierdev.pub
```

## Test GitHub

```bash
ssh -T git@github.com
```

---

# 4. Clonage du dépôt

```bash
mkdir -p ~/workspace
cd ~/workspace

git clone git@github.com:FabienTremblay/jeu-cabinet.git
cd jeu-cabinet
```

## Vérifications

```bash
git status
git remote -v
```

---

# 5. Installation de pipx

## Installation Ubuntu

```bash
sudo apt install pipx python3-venv
```

---

# 6. Installation d’Aider

## Installation

```bash
pipx install aider-install
```

## Chargement du PATH

```bash
source ~/.bashrc
```

## Vérification

```bash
which aider
aider --version
```

---

# 7. LM Studio — tests API

## Vérification des modèles

```bash
curl -sS http://localhost:1234/v1/models | python3 -m json.tool
```

## Test direct d’un modèle

```bash
curl -sS http://localhost:1234/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "NOM_MODELE",
    "messages": [
      {
        "role": "user",
        "content": "Réponds seulement: OK"
      }
    ],
    "temperature": 0.1,
    "max_tokens": 50
  }' | python3 -m json.tool
```

---

# 8. Modèles testés

## Résultats observés

| Modèle | Résultat |
|---|---|
| nvidia/nemotron-3-nano-4b | fonctionne mais beaucoup de reasoning |
| qwen2.5-coder-7b-instruct | instable avec Aider |
| deepseek-r1-qwen3-8b | problèmes de contexte et reasoning |
| qwen2.5-coder-3b-instruct | meilleur résultat avec Aider |

## Verdict provisoire

Le meilleur modèle local pour Aider sur cette machine :

```text
qwen2.5-coder-3b-instruct
```

---

# 9. Scripts utilitaires créés

## Répertoire local d’outils

```bash
mkdir -p ~/bin
```

---

## Script lmtest

### Objectif

Tester rapidement un modèle LM Studio.

### Usage

```bash
lmtest "NOM_MODELE"
```

---

## Script aider-lm

### Objectif

Lancer Aider avec LM Studio.

### Paramètres importants

```bash
--edit-format diff
--no-auto-commits
```

### Usage

```bash
aider-lm "qwen2.5-coder-3b-instruct"
```

---

# 10. Installation de Codex CLI

## Préparation npm local

```bash
mkdir -p ~/.npm-global

npm config set prefix "$HOME/.npm-global"
```

## PATH

```bash
export PATH="$HOME/.npm-global/bin:$PATH"
```

---

## Installation Codex

```bash
npm i -g @openai/codex
```

## Vérification

```bash
which codex
codex --version
```

---

# 11. Discipline Git mise en place

## Règles retenues

- ne jamais travailler directement sur `main`
- utiliser `essai-codex`
- inspecter les `git diff`
- ne jamais pousser automatiquement
- validation humaine obligatoire
- Aider réservé aux micro-modifications

---

# 12. Gestion des branches

## Création locale

```bash
git checkout -b essai-codex
```

## Alignement avec la branche distante

```bash
git fetch origin

git branch --set-upstream-to=origin/essai-codex essai-codex

git reset --hard origin/essai-codex
```

## Reprise du commit .gitignore

```bash
git cherry-pick 54042e5
```

---

# 13. Fichiers .aider ignorés

Ajout dans `.gitignore` :

```gitignore
.aider*
```

---

# 14. Doctrine retenue

## Rôles

### Toi

- architecte
- arbitre
- validation finale
- gardien du sens

### Codex

- agent principal
- analyse
- planification
- modifications structurées
- tests

### Aider

- assistant local secondaire
- micro-diffs
- modifications ciblées
- jamais sans validation humaine

---

# 15. Conclusion

L’atelier local est maintenant opérationnel :

- utilisateur Linux dédié
- Git isolé
- LM Studio fonctionnel
- Aider fonctionnel
- Codex CLI installé
- branche d’expérimentation sécurisée
- workflow IA clarifié
