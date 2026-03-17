---
name: ci-cd
description: Infrastructure locale et prod, CI/CD, déploiement tuls.me. Utiliser pour logs, start scripts, GitHub Actions, nginx, DNS.
triggers:
  - tuls.me
  - serveur tuls
  - nginx
  - déployer
  - ci/cd
  - github actions
  - logs
  - start.sh
  - Procfile
  - honcho
  - local dev
---

# CI/CD & Infrastructure

## Règle absolue

**NE JAMAIS démarrer ou arrêter le serveur dev**

Le serveur tourne déjà (honcho ou tmux). Tu dois SEULEMENT lire les logs.
Si l'utilisateur demande de démarrer/arrêter → lui rappeler qu'il tourne déjà.

---

## Dev local — Pattern honcho + Procfile

Chaque projet a un `Procfile` à sa racine. On lance avec `honcho start`.

```bash
# Installer (une fois)
pipx install honcho

# Lancer un projet
cd /data/projects/tuls && honcho start
```

Honcho gère : logs préfixés par process, cleanup au Ctrl+C, multi-process (db + app + worker).

### Exemple Procfile (Flask + PG Docker)
```
db: docker compose -f infra/local/docker-compose.yml up
app: PORT=5000 ./venv/bin/python -u app.py
```

### Exemple Procfile (FastAPI + PG Docker)
```
db: docker compose -f infra/local/docker-compose.yml up
app: .venv/bin/uvicorn app.backend.main:app --host 0.0.0.0 --port 8085 --reload
```

### Exemple Procfile (Next.js)
```
app: npm run dev
```

**Important :** `--reload` pour le hot reload en dev. En prod (service.conf), **jamais** de `--reload`.

---

## Config centrale

**Répertoire :** `/data/infra/local-dev/`

| Fichier | Rôle |
|---------|------|
| `ports.conf` | Registre des ports (source de vérité) |
| `local-dev.nginx` | Reverse proxy *.local → localhost:PORT |
| `start-all.sh` | Lance tous les projets en tmux |
| `check-ports.sh` | Vérifie cohérence ports/nginx |

### Architecture

```
Browser → *.local → /etc/hosts → 127.0.0.1 → nginx (port 80) → localhost:PORT
```

### Ports assignés (source de vérité : `/data/infra/local-dev/ports.conf`)

| Port | Projet | Domaine local |
|------|--------|---------------|
| 5000 | tuls | tuls.local |
| 5010 | otomata | otomata.local |
| 8000 | yaats | yaats.local |
| 3000 | landing-builder | landing.local |
| 3001 | ytmusic-manager | ytmusic.local |
| 5173 | headless-crm | hcrm.local |
| 5001 | financex | financex.local |
| 3002 | roundtable | rtx.local |
| 8080 | o-browser | browser.local |
| 8765 | stocktrotter | stocktrotter.local |
| 5174 | 4-as-agent-front | albaron.local |
| 8085 | 4-as-agent | albaron.local |
| 8086 | la-fabrique-by-ca | lfbca.local |

### Plages de ports

| Stack | Plage | Prochain dispo |
|-------|-------|----------------|
| Flask | 5000-5099 | 5002 |
| Django | 8000-8099 | 8001 |
| FastAPI | 8080-8099 | 8087 |
| Next.js | 3000-3099 | 3003 |
| Vite/React | 5173-5199 | 5175 |

### Ajouter un projet au local dev

1. Choisir port dans la plage selon la stack
2. Ajouter dans `/data/infra/local-dev/ports.conf`
3. Ajouter server block dans `/data/infra/local-dev/local-dev.nginx`
4. `echo "127.0.0.1 monprojet.local" | pkexec tee -a /etc/hosts`
5. `pkexec nginx -t && pkexec systemctl reload nginx`
6. Créer un `Procfile` à la racine du projet
7. (optionnel) Ajouter une window tmux dans `start-all.sh`

### Lancer tous les projets

```bash
/data/infra/local-dev/start-all.sh     # Lance en tmux
tmux attach -t dev                      # Voir les logs
tmux kill-session -t dev                # Arrêter tout
```

---

## Structure infra par projet

```
projet/
├── Procfile              # Processes dev (honcho)
├── infra/
│   └── prod/
│       ├── nginx.conf    # Config nginx (référence)
│       ├── service.conf  # Systemd service (référence)
│       └── setup.sh      # Script setup serveur (optionnel)
└── .github/
    └── workflows/
        └── deploy.yml    # CI/CD
```

---

## Serveur tuls.me

### Accès

```bash
ssh -i ~/.ssh/alexis root@51.15.225.121
```

### Sites hébergés

Voir `/data/infra/CLAUDE.md` pour la liste complète des services et ports.

### DNS Scaleway

```bash
scw dns record list tuls.me
scw dns record add tuls.me name=SUBDOMAIN type=A data=51.15.225.121 ttl=300
```

### SSL

```bash
cd /data/infra
./scripts/ssl-cert.sh list    # Domaines actuels
./scripts/ssl-cert.sh check   # Vérifie si domaines manquent
./scripts/ssl-cert.sh sync    # Ajoute domaines manquants
```

### Ajouter un site sur tuls.me

1. DNS: `scw dns record add tuls.me name=monsite type=A data=51.15.225.121 ttl=300`
2. Nginx: créer `/etc/nginx/sites-available/monsite`
3. Activer: `ln -s /etc/nginx/sites-available/monsite /etc/nginx/sites-enabled/`
4. SSL: `./scripts/ssl-cert.sh sync`
5. Reload: `nginx -t && systemctl reload nginx`

---

## Templates nginx (prod)

### Static
```nginx
server {
    listen 80;
    server_name monsite.tuls.me;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl http2;
    server_name monsite.tuls.me;
    ssl_certificate /etc/letsencrypt/live/tuls.me-wildcard/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/tuls.me-wildcard/privkey.pem;
    root /opt/monsite;
    index index.html;
    location / { try_files $uri $uri/ =404; }
}
```

### Proxy (API + SPA)
```nginx
server {
    listen 80;
    server_name monsite.tuls.me;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl http2;
    server_name monsite.tuls.me;
    ssl_certificate /etc/letsencrypt/live/tuls.me-wildcard/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/tuls.me-wildcard/privkey.pem;

    root /opt/monsite/frontend/dist;
    index index.html;

    location /api {
        proxy_pass http://127.0.0.1:PORT;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location / { try_files $uri $uri/ /index.html; }
}
```

### Systemd service
```ini
[Unit]
Description=Mon API
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/monsite/app/backend
Environment="PATH=/opt/monsite/venv/bin"
ExecStart=/opt/monsite/venv/bin/uvicorn main:app --host 127.0.0.1 --port PORT
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```

---

## CI/CD GitHub Actions

### Deploy key setup

1. Créer clé RSA: `ssh-keygen -t rsa -b 4096 -f /tmp/deploy -N '' -C 'projet-deploy'`
2. Ajouter pub sur serveur: `cat /tmp/deploy.pub >> ~/.ssh/authorized_keys` (via SSH)
3. Secret GitHub: `gh secret set SSH_PRIVATE_KEY < /tmp/deploy`

### Template deploy.yml

```yaml
name: Deploy

on:
  push:
    branches: [master]

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
            git pull origin master

            # Backend
            cd app/backend
            /opt/${{ github.event.repository.name }}/venv/bin/pip install -r requirements.txt -q

            # Frontend
            cd ../frontend
            npm install --silent
            npm run build

            # Restart
            systemctl restart ${{ github.event.repository.name }}-api
```

### Vercel (front-end only)

```bash
gh repo create AlexisLaporte/$REPO_NAME --private --source=. --push
vercel link
vercel git connect
```

---

## Branch Deployments (full-stack)

Pattern : **branche = déploiement** (`{slug}.projet.tuls.me`), **tag = prod** (`projet.tuls.me`).

**Outil partagé** : `/data/infra/scripts/branch-*.sh` (copié sur serveur dans `/opt/branch-deploy/`)

### Fonctionnement

- `branch-deploy.sh <project-dir> <slug> <branch>` — clone/update, alloue port, installe, génère .env, restart service, regen nginx map
- `branch-cleanup.sh <project-dir> <slug>` — stop service, rm branch dir, regen nginx map
- `branch-regen-map.sh <project-dir>` — parcourt `branches/*/.port` → `nginx-ports.conf` → nginx reload

### Config par projet

Chaque projet a dans `infra/prod/` :

| Fichier | Rôle |
|---------|------|
| `branches.conf` | REPO_URL, PORT_BASE/MAX, SERVICE_TPL, MAP_VAR, INSTALL_CMD, WORKING_SUBDIR |
| `branch.env.tpl` | Template .env avec `${SLUG}`, `${PORT}`, `${BRANCH_DIR}` |
| `*-branch@.service` | Systemd template unit (instancié par slug) |
| `*-branches.nginx` | Nginx regex server block `*.projet.tuls.me` avec map → port |

### Projets avec branch deploy actif

| Projet | Domaine branches | Plage ports | Prod |
|--------|-----------------|-------------|------|
| financex | `*.financex.tuls.me` | 5100-5199 | `financex.tuls.me` (tag) |
| 4-as-agent | `*.4-as-agent.proj.otomata.tech` | 8200-8299 | `4-as-agent.proj.otomata.tech` (tag) |

---

## Checklist nouveau projet

- [ ] Port choisi et ajouté à `ports.conf`
- [ ] `Procfile` créé à la racine du projet
- [ ] Server block ajouté dans `local-dev.nginx`
- [ ] Domaine `.local` ajouté dans `/etc/hosts`
- [ ] nginx rechargé
- [ ] DNS Scaleway configuré
- [ ] `infra/prod/nginx.conf` créé
- [ ] `infra/prod/service.conf` créé
- [ ] Nginx activé sur serveur
- [ ] SSL synchronisé (`ssl-cert.sh sync`)
- [ ] `.github/workflows/deploy.yml` créé
- [ ] Secret `SSH_PRIVATE_KEY` configuré
- [ ] Monitor ajouté dans Uptime Kuma (https://uptime.tuls.me)
- [ ] (optionnel) Branch deploy
