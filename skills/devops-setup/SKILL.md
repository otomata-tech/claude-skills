---
name: devops-setup
description: Setup dev servers, CI/CD pipelines, and deployment. Use to read logs, create start scripts, and configure GitHub Actions.
---

# DevOps Setup Skill

## Règle absolue

**NE JAMAIS démarrer ou arrêter le serveur**

Le serveur tourne déjà. Tu dois SEULEMENT lire les logs :
- `tail -f dev/dev.log`
- `grep "ERROR" dev/dev.log`
- JAMAIS lancer `npm run dev` ou `python manage.py runserver`

Si l'utilisateur demande de démarrer/arrêter → lui rappeler qu'il tourne déjà.

## Commandes logs

```bash
tail -f dev/dev.log                    # Temps réel
tail -n 100 dev/dev.log                # Dernières lignes
grep -i "error" dev/dev.log            # Recherche
```

---

## Local Dev Infrastructure

**Config centrale :** `/data/alexis/infra/local-dev/`

```
infra/local-dev/
├── README.md           # Documentation
├── local-dev.nginx     # Nginx reverse proxy (*.local → localhost:PORT)
├── setup.sh            # Installation (nginx + /etc/hosts)
└── start-all.sh        # Démarre tous les projets (tmux)
```

### Ports assignés (source de vérité)

| Projet | Port | Domaine local | Stack |
|--------|------|---------------|-------|
| tuls | 5000 | tuls.local, claude.tuls.local, growth.tuls.local | Flask |
| financex | 5002 | financex.local | Flask |
| otomata | 5010 | otomata.local | Flask |
| yaats | 8000 | yaats.local | Django |
| landing-builder | 3000 | landing.local | Next.js |
| ytmusic | 3001 | ytmusic.local | Node |
| yacrm | 5173 | yacrm.local | Vite |

### Plages de ports par stack

| Stack | Plage | Prochain dispo |
|-------|-------|----------------|
| Flask | 5000-5099 | 5003 |
| Django | 8000-8099 | 8001 |
| FastAPI | 7000-7099 | 7002 |
| Next.js | 3000-3099 | 3002 |
| Vite/React | 5173-5199 | 5174 |
| Node/Express | 3100-3199 | 3100 |

---

## Ajouter un nouveau projet

### 1. Choisir le port

Consulter le tableau ci-dessus et prendre le prochain disponible dans la plage.

### 2. Ajouter au nginx local

Éditer `/data/alexis/infra/local-dev/local-dev.nginx` :

```nginx
# monprojet.local
server {
    listen 80;
    server_name monprojet.local;

    location / {
        proxy_pass http://127.0.0.1:PORT;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Pour Vite/Next.js (HMR websocket), ajouter :
```nginx
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
```

### 3. Ajouter au /etc/hosts

```bash
echo "127.0.0.1  monprojet.local" | sudo tee -a /etc/hosts
```

### 4. Recharger nginx

```bash
sudo nginx -t && sudo systemctl reload nginx
```

### 5. Mettre à jour start-all.sh (optionnel)

Ajouter dans `/data/alexis/infra/local-dev/start-all.sh` :

```bash
# monprojet (port XXXX)
tmux new-window -t $SESSION -n "monprojet"
tmux send-keys -t $SESSION:monprojet "cd /data/alexis/monprojet && python3 app.py" Enter
```

### 6. Mettre à jour ce skill

Ajouter le projet au tableau "Ports assignés" ci-dessus.

---

## Structure dev/ pour un projet

```
projet/
├── dev/
│   ├── start.sh           # Démarre serveur avec logs
│   └── dev.log            # Logs (écrasés à chaque démarrage)
└── .github/
    └── workflows/
        └── deploy.yml     # CI/CD (optionnel)
```

### Templates start.sh

**Flask :**
```bash
#!/bin/bash
set -e
cd "$(dirname "$0")/.."
# Secrets loaded from .env + .env.local by app.py
PORT=${PORT:-5000}
echo "Flask on port ${PORT}"
source venv/bin/activate 2>/dev/null || true
unbuffer python app.py 2>&1 | tee dev/dev.log
```

**Django :**
```bash
#!/bin/bash
set -e
cd "$(dirname "$0")/.."
PORT=${PORT:-8000}
echo "Django on port ${PORT}"
source venv/bin/activate 2>/dev/null || true
unbuffer python manage.py runserver "0.0.0.0:${PORT}" 2>&1 | tee dev/dev.log
```

**Next.js :**
```bash
#!/bin/bash
set -e
cd "$(dirname "$0")/.."
echo "Next.js dev"
unbuffer npm run dev 2>&1 | tee dev/dev.log
```

**FastAPI :**
```bash
#!/bin/bash
set -e
cd "$(dirname "$0")/.."
PORT=${PORT:-7000}
echo "FastAPI on port ${PORT}"
source venv/bin/activate 2>/dev/null || true
unbuffer uvicorn app:app --host 0.0.0.0 --port ${PORT} --reload 2>&1 | tee dev/dev.log
```

### Installation

```bash
mkdir -p dev
chmod +x dev/start.sh
# unbuffer requis pour logs temps réel
which unbuffer || sudo apt-get install -y expect
```

---

## Secrets / Variables d'environnement

Pattern `.env` multi-fichiers (référence : tuls) :

```
.env          → secrets communs (API keys, OAuth) — gitignored
.env.local    → overrides local dev (BASE_URL, DATABASE_URL) — gitignored
.env.prod     → overrides prod (SECRET_KEY, AUTH_SECRET) — serveur uniquement, gitignored
.env.example  → référence des vars — committé
```

L'app charge `.env` puis `.env.{ENV}` (`ENV=local` par défaut). Le second fichier écrase le premier.

**Loader Python (app.py) :**
```python
for env_file in ['.env', f'.env.{os.environ.get("ENV", "local")}']:
    path = Path(__file__).parent / env_file
    if path.exists():
        for line in path.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ[key.strip()] = value.strip()
```

**Systemd (prod) :**
```ini
Environment=ENV=prod
EnvironmentFile=/opt/PROJET/.env
EnvironmentFile=/opt/PROJET/.env.prod
```

**`.gitignore` :**
```
.env
.env.local
.env.prod
```

---

## CI/CD Setup

### Vérifier si CI/CD configuré

```bash
ls .github/workflows/*.yml 2>/dev/null && echo "GitHub Actions présent"
[ -f .vercel/project.json ] && echo "Vercel lié"
git remote -v
```

### Option A : Déploiement Vercel (SaaS)

Pour projets front-end (Next.js, React, etc.) :

```bash
[ -d .git ] || git init
REPO_NAME=$(basename $PWD)
gh repo create AlexisLaporte/$REPO_NAME --private --source=. --push
vercel link
vercel git connect
```

### Option B : Déploiement serveur (tuls.me)

Pour projets backend Flask/Django :

**Créer `.github/workflows/deploy.yml` :**

```yaml
name: Deploy

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to server
        uses: appleboy/ssh-action@v1.0.3
        with:
          host: 51.15.225.121
          username: root
          key: ${{ secrets.SSH_PRIVATE_KEY }}
          script: |
            cd /opt/${{ github.event.repository.name }}
            git pull origin main
            source venv/bin/activate
            pip install -r requirements.txt
            systemctl restart ${{ github.event.repository.name }}
```

**Secrets requis sur GitHub :**
```bash
gh secret set SSH_PRIVATE_KEY < ~/.ssh/deploy
```

### Option C : Déploiement 321founded

```bash
REPO_NAME=$(basename $PWD)
gh repo create 321founded/$REPO_NAME --private --source=. --push
vercel link
vercel git connect https://github.com/321founded/$REPO_NAME
```

### Option D : Preview Deployments par branche

Déploie chaque PR sur un sous-domaine unique `{slug}.{site}.tuls.me`.

Voir skill `serveur-tuls` pour setup serveur (DNS wildcard, SSL, nginx).

---

## Checklist Setup Complet

- [ ] Port défini (dans plage appropriée, ajouté au tableau)
- [ ] Nginx local configuré (`local-dev.nginx`)
- [ ] `/etc/hosts` mis à jour
- [ ] `dev/start.sh` créé avec le bon template
- [ ] `chmod +x dev/start.sh`
- [ ] `.gitignore` inclut `dev/dev.log`, `.env`, `.env.local`, `.env.prod`
- [ ] `.env` + `.env.local` créés (secrets), `.env.example` committé
- [ ] CI/CD configuré (Vercel OU GitHub Actions)
- [ ] Serveur : `.env` + `.env.prod` dans `/opt/PROJET/` (chmod 600), systemd `EnvironmentFile=`

---

## Rappels

- "Démarre le serveur" → "Le serveur tourne déjà. Lire logs : `tail -f dev/dev.log`"
- "Arrête le serveur" → "Je ne dois jamais. Fais Ctrl+C si nécessaire"
- "Logs" → Utiliser `tail -f` ou `grep`
- "Deploy" → Vérifier si CI/CD existe, sinon proposer de le setup
- "Nouveau projet" → Suivre les étapes "Ajouter un nouveau projet"
