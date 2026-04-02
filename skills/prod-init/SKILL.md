---
name: prod-init
description: "Déployer sur tuls.me (Caddy + systemd + DNS), configurer CI/CD GitHub Actions, staging optionnel."
triggers:
  - tuls.me
  - serveur tuls
  - déployer
  - deploy
  - ci/cd
  - github actions
  - staging
  - prod
  - caddy prod
argument-hint: "[nom du projet]"
---

# Prod Init — Déploiement tuls.me & CI/CD

## Serveur tuls.me

### Accès

```bash
ssh -i ~/.ssh/alexis root@51.15.225.121
```

### Caddyfile

**Source de vérité locale :** `/data/infra/Caddyfile`
**Sur le serveur :** `/etc/caddy/Caddyfile`
**Caddy binary custom :** `/usr/local/bin/caddy-custom`

SSL automatique via Caddy (ACME). Pas de gestion manuelle de certificats.

### Ports

**Source de vérité serveur :** `/opt/ports.conf`
**Source de vérité locale :** `/data/infra/PORTS.md`

Voir `/data/infra/CLAUDE.md` pour la liste complète des services et ports.

### DNS Scaleway

Wildcard `*.tuls.me` → `51.15.225.121` déjà en place.

Pour un domaine hors `*.tuls.me` :
```bash
scw dns record add tuls.me name=SUBDOMAIN type=A data=51.15.225.121 ttl=300
scw dns record list tuls.me
```

---

## Déployer un nouveau service

### 1. Choisir un port

```bash
ssh -i ~/.ssh/alexis root@51.15.225.121 "/opt/check-port.sh PORT PROJECT"
```

Mettre à jour `/data/infra/PORTS.md` localement.

### 2. Créer le service systemd

```ini
# /etc/systemd/system/<project>.service
[Unit]
Description=<Project Name>
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/<project>
ExecStartPre=/opt/check-port-systemd.sh PORT <project>
ExecStart=/opt/<project>/venv/bin/uvicorn app:app --host 127.0.0.1 --port PORT
Restart=always
RestartSec=5
SyslogIdentifier=<project>

[Install]
WantedBy=multi-user.target
```

Variante Node.js :
```ini
ExecStart=/usr/bin/node /opt/<project>/server/dist/index.js
Environment="PORT=PORT"
Environment="NODE_ENV=production"
```

Activer :
```bash
ssh -i ~/.ssh/alexis root@51.15.225.121 "systemctl daemon-reload && systemctl enable <project> && systemctl start <project>"
```

### 3. Ajouter le bloc Caddy

Éditer `/data/infra/Caddyfile` (source de vérité locale) :

**Backend seul :**
```
# --- <project> ---

<subdomain>.tuls.me {
    reverse_proxy localhost:PORT
}
```

**API + SPA :**
```
# --- <project> ---

<subdomain>.tuls.me {
    handle /api/* {
        reverse_proxy localhost:PORT
    }
    handle {
        root * /opt/<project>/frontend/dist
        try_files {path} /index.html
        file_server
    }
}
```

Déployer le Caddyfile :
```bash
scp -i ~/.ssh/alexis /data/infra/Caddyfile root@51.15.225.121:/etc/caddy/Caddyfile
ssh -i ~/.ssh/alexis root@51.15.225.121 "caddy-custom reload --config /etc/caddy/Caddyfile"
```

### 4. Déployer le code

```bash
# Copier le projet
rsync -avz --exclude venv --exclude node_modules --exclude __pycache__ --exclude .git \
  -e "ssh -i ~/.ssh/alexis" \
  /data/projects/<project>/ root@51.15.225.121:/opt/<project>/

# Installer les dépendances (Python)
ssh -i ~/.ssh/alexis root@51.15.225.121 "cd /opt/<project> && python3 -m venv venv && ./venv/bin/pip install -r requirements.txt"

# Installer les dépendances (Node.js)
ssh -i ~/.ssh/alexis root@51.15.225.121 "cd /opt/<project>/server && npm ci && cd ../frontend && npm ci && npm run build"

# Démarrer
ssh -i ~/.ssh/alexis root@51.15.225.121 "systemctl restart <project>"
```

### 5. Enregistrer le port

```bash
ssh -i ~/.ssh/alexis root@51.15.225.121 "echo 'PORT <project>' >> /opt/ports.conf"
```

### 6. Vérifier

```bash
# Logs
ssh -i ~/.ssh/alexis root@51.15.225.121 "journalctl -u <project> -n 20"

# HTTP
curl -s https://<subdomain>.tuls.me/
```

---

## CI/CD — GitHub Actions

### Deploy key (1 clé par projet)

Chaque projet a sa propre clé SSH. Pas de clé partagée.

```bash
# Générer la clé
ssh-keygen -t ed25519 -f /tmp/deploy-<project> -N '' -C '<project>-deploy'

# Ajouter la clé publique sur le serveur
ssh -i ~/.ssh/alexis root@51.15.225.121 "echo '$(cat /tmp/deploy-<project>.pub)' >> ~/.ssh/authorized_keys"

# Stocker la clé privée dans GitHub Secrets
gh secret set SSH_PRIVATE_KEY < /tmp/deploy-<project>

# Nettoyer
rm /tmp/deploy-<project> /tmp/deploy-<project>.pub
```

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

            # Backend (Python)
            cd app/backend
            /opt/${{ github.event.repository.name }}/venv/bin/pip install -r requirements.txt -q

            # Frontend
            cd ../frontend
            npm install --silent
            npm run build

            # Restart
            systemctl restart ${{ github.event.repository.name }}-api
```

Adapter le script selon la stack (Python/Node.js, avec/sans frontend).

---

## Staging (optionnel)

Environnement staging à la demande : `staging.<project>.tuls.me`.

### Setup

1. **Port** : choisir un port distinct de la prod
2. **Service** : `<project>-staging.service` (même template, port et WorkingDirectory différents)
3. **Code** : `/opt/<project>-staging/` (clone séparé sur la branche `staging` ou `develop`)
4. **Caddy** : ajouter un bloc dans le Caddyfile
   ```
   staging.<subdomain>.tuls.me {
       reverse_proxy localhost:STAGING_PORT
   }
   ```
5. **GitHub Actions** : workflow séparé ou job conditionnel sur la branche

### Déployer sur staging

```bash
ssh -i ~/.ssh/alexis root@51.15.225.121 "cd /opt/<project>-staging && git pull origin staging && systemctl restart <project>-staging"
```

---

## Vercel (frontend only)

Pour les projets frontend sans backend custom :

```bash
gh repo create AlexisLaporte/$REPO_NAME --private --source=. --push
vercel link
vercel git connect
```

---

## Structure infra par projet

```
projet/
├── Procfile              # Processes dev (honcho)
├── infra/
│   └── prod/
│       └── service.conf  # Systemd service (référence)
└── .github/
    └── workflows/
        └── deploy.yml    # CI/CD
```

La config Caddy est centralisée dans `/data/infra/Caddyfile`, pas dans le projet.

---

## Conventions

- Code dans `/opt/<project>/` sur le serveur
- Source dans `/data/projects/<project>/` en local
- Pas de DB sauf si nécessaire (voir `/data/infra/CLAUDE.md` pour les bases existantes)
- Logs via journalctl (`journalctl -u <project> -f`)
- SSL automatique via Caddy (ACME)
- Monitoring : Uptime Kuma (https://uptime.tuls.me)

---

## Checklist nouveau projet

### Local
- [ ] Port choisi et ajouté à `ports.conf`
- [ ] `Procfile` créé
- [ ] Bloc ajouté dans `/data/infra/local-dev/Caddyfile`
- [ ] Domaine `.dev` ajouté dans `/etc/hosts`
- [ ] Caddy local rechargé

### Prod
- [ ] Port choisi et vérifié sur serveur
- [ ] `infra/prod/service.conf` créé
- [ ] Service systemd activé sur serveur
- [ ] Bloc ajouté dans `/data/infra/Caddyfile` et déployé
- [ ] `.github/workflows/deploy.yml` créé
- [ ] Secret `SSH_PRIVATE_KEY` configuré (clé dédiée)
- [ ] PORTS.md mis à jour
- [ ] Monitor ajouté dans Uptime Kuma
- [ ] (optionnel) Staging configuré
