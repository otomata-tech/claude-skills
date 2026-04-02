---
name: dev-init
description: "Initialiser un projet web fullstack (Fastify + Vue 3 + Vite + shadcn-vue + Tailwind + PG + Drizzle + Auth0) et configurer l'environnement local (Caddy, ports, honcho)."
triggers:
  - init web
  - nouveau projet web
  - bootstrap projet
  - créer un projet
  - web init
  - dev init
  - local dev
  - Procfile
  - honcho
argument-hint: "[nom du projet]"
---

# Dev Init — Nouveau projet web fullstack

## Règle absolue

**NE JAMAIS démarrer ou arrêter le serveur dev.**

Le serveur tourne déjà (honcho ou tmux). Tu dois SEULEMENT lire les logs.

---

## Stack standard

| Couche | Choix | Pourquoi |
|--------|-------|----------|
| **Backend** | Fastify + TypeScript | API REST propre, OpenAPI native, mainstream |
| **Validation** | Zod + fastify-type-provider-zod | Schemas typés → validation + OpenAPI auto |
| **API Docs** | @fastify/swagger + @fastify/swagger-ui | Swagger UI sur /api/docs, spec sur /api/doc |
| **DB** | PostgreSQL + Drizzle ORM | Type-safe, migrations, pas d'ORM magique |
| **Frontend** | Vue 3 + Vite | Simple, DX excellente, moins de boilerplate que React |
| **UI** | shadcn-vue + Tailwind CSS v4 | Composants éditables, dark theme, cohérent |
| **Auth** | Auth0 (PKCE + RS256 JWT) | Tenant otomata.us.auth0.com, CLI dispo |
| **Dev** | Procfile + honcho | Un `honcho start` lance tout |
| **Prod** | Caddy + systemd + GitHub Actions | Deploy sur tuls.me (voir `/prod-init`) |

Ne pas substituer de framework sans discussion explicite.

## Structure cible

```
project/
├── server/
│   ├── src/
│   │   ├── index.ts          # Fastify app, plugins, routes
│   │   ├── db.ts             # Drizzle schema + connection
│   │   ├── schemas.ts        # Zod schemas (validation + OpenAPI)
│   │   └── routes/
│   │       └── auth.ts       # JWT preHandler (Auth0 JWKS via jose)
│   ├── package.json
│   └── tsconfig.json
├── frontend/
│   ├── src/
│   │   ├── main.ts
│   │   ├── App.vue
│   │   ├── router.ts
│   │   ├── api.ts            # Client API + auth token
│   │   ├── assets/index.css  # Tailwind + @theme
│   │   ├── composables/useAuth.ts  # Auth0 SPA SDK
│   │   ├── components/ui/    # shadcn-vue
│   │   ├── components/       # App components
│   │   ├── views/            # Pages
│   │   └── lib/utils.ts      # cn() utility
│   ├── components.json       # shadcn-vue config
│   ├── package.json
│   ├── vite.config.ts
│   └── tsconfig.json
├── infra/
│   └── prod/
│       └── service.conf      # Systemd unit
├── Procfile
└── .github/workflows/deploy.yml
```

---

## Initialisation du projet

### 1. Structure de base

Créer les dossiers `server/` et `frontend/`. Initialiser les `package.json` avec `"type": "module"`.

### 2. Backend (server/)

```bash
cd server
npm init -y
npm install fastify @fastify/cors @fastify/swagger @fastify/swagger-ui @fastify/static @fastify/multipart fastify-type-provider-zod zod jose postgres drizzle-orm dotenv
npm install -D @types/node tsx typescript drizzle-kit
```

**index.ts pattern :**
```typescript
import Fastify from "fastify";
import { serializerCompiler, validatorCompiler, jsonSchemaTransform } from "fastify-type-provider-zod";

const app = Fastify({ logger: { level: "error" } });
app.setValidatorCompiler(validatorCompiler);
app.setSerializerCompiler(serializerCompiler);

// Register plugins: cors, multipart, swagger, swagger-ui, static
// Register route plugins with prefix
// Listen on PORT env var
```

**Auth middleware pattern :**

Le middleware tente dans l'ordre : cookie session → JWT Auth0 → API token DB.

```typescript
import { createRemoteJWKSet, jwtVerify } from "jose";

const JWKS = createRemoteJWKSet(new URL(`https://${AUTH0_DOMAIN}/.well-known/jwks.json`));

async function authPreHandler(request: FastifyRequest, reply: FastifyReply) {
  // 1. Cookie session (SSO .tuls.me)
  const cookie = request.cookies["auth-token"];
  if (cookie) {
    const payload = verifyInternalJwt(cookie); // HS256 via AUTH_SECRET
    if (payload) { request.user = payload; return; }
  }

  // 2. Bearer JWT (Auth0)
  const auth = request.headers.authorization;
  if (auth?.startsWith("Bearer ")) {
    const token = auth.slice(7);
    try {
      const { payload } = await jwtVerify(token, JWKS, { audience: AUTH0_AUDIENCE });
      request.user = { sub: payload.sub, email: payload.email, roles: payload["https://<project>/roles"] || [] };
      return;
    } catch {}

    // 3. API token (prefixed, hashed in DB)
    if (token.startsWith("<project>_")) {
      const hash = sha256(token);
      const apiToken = await db.select().from(apiTokens).where(eq(apiTokens.tokenHash, hash)).limit(1);
      if (apiToken[0]) { request.user = { sub: apiToken[0].userId }; return; }
    }
  }

  reply.code(401).send({ error: "Unauthorized" });
}
```

**API tokens :**
- Préfixe projet (`<project>_`) + `crypto.randomUUID()`
- Stocké en DB : SHA-256 du token (jamais le token brut)
- Endpoints : `POST /api/auth/tokens` (create), `GET /api/auth/tokens` (list), `DELETE /api/auth/tokens/:id` (revoke)

**RBAC Auth0 :**
- Rôles configurés dans Auth0 Dashboard (ex: `admin`, `member`)
- Roles injectés dans le JWT via Auth0 Rule/Action : `https://<project>/roles`
- Check côté route : `if (!request.user.roles.includes("admin")) reply.code(403).send(...)`

**Route pattern :**
```typescript
import type { FastifyPluginAsync } from "fastify";
import type { ZodTypeProvider } from "fastify-type-provider-zod";

const routes: FastifyPluginAsync = async (fastify) => {
  const app = fastify.withTypeProvider<ZodTypeProvider>();
  app.get("/", { schema: { response: { 200: MyZodSchema } } }, async (request) => { ... });
};
```

### 3. Frontend (frontend/)

```bash
cd frontend
npm create vue@latest . -- --typescript --router --no-pinia --no-vitest --no-e2e --no-eslint --no-prettier
npm install @auth0/auth0-spa-js
npm install -D tailwindcss @tailwindcss/vite
```

**vite.config.ts** : ajouter `tailwindcss()` plugin + proxy `/api` et `/data` vers le backend.

**shadcn-vue :**
```bash
npx shadcn-vue@latest init -y -b slate
npx shadcn-vue@latest add button card badge dialog input textarea select separator
```

**Thème dark** dans `src/assets/index.css` : CSS variables dans `:root` (pas de light/dark toggle sauf demandé).

**Auth0** : composable `useAuth.ts` avec Auth0Client, initAuth(), login(), logout(), getAccessToken(). PKCE flow avec redirect vers `/callback`.

### 4. Procfile + .env

**Procfile :**
```
server: cd server && PORT=<port> npx tsx watch src/index.ts
frontend: cd frontend && npx vite --host
```

**Convention .env :**
- `server/.env` — secrets backend (jamais commité)
- `server/.env.example` — template commité (valeurs vides ou fake)
- `frontend/.env` — config publique frontend

**Variables standard backend :**
```env
PORT=<port>
DATABASE_URL=postgres://user:pass@localhost:5434/<project>
AUTH0_DOMAIN=otomata.us.auth0.com
AUTH0_AUDIENCE=https://api.<project>.proj.otomata.tech
AUTH_SECRET=<random-string>  # Pour JWT internes / SSO cookie
```

**Variables standard frontend :**
```env
VITE_AUTH0_DOMAIN=otomata.us.auth0.com
VITE_AUTH0_CLIENT_ID=<client-id>
VITE_AUTH0_AUDIENCE=https://api.<project>.proj.otomata.tech
```

### 5. Auth0

Créer une app SPA dans le tenant `otomata.us.auth0.com` :
```bash
auth0 apps create --name "<Project>" --type spa --callbacks "https://<project>.dev/callback" --logout-urls "https://<project>.dev" --web-origins "https://<project>.dev"
```

Créer une API si besoin :
```bash
auth0 apis create --name "<Project> API" --identifier "https://api.<project>.proj.otomata.tech"
```

### 6. Tests

```bash
cd server
npm install -D vitest
```

**package.json :**
```json
{ "scripts": { "test": "vitest run", "test:watch": "vitest" } }
```

**Structure :** tests co-localisés dans `server/src/` (ex: `routes/items.test.ts` à côté de `routes/items.ts`).

**Pattern test API :**
```typescript
import { describe, it, expect } from "vitest";
import { buildApp } from "../index.js";  // Export app factory

describe("GET /api/items", () => {
  it("returns items", async () => {
    const app = await buildApp();
    const res = await app.inject({ method: "GET", url: "/api/items" });
    expect(res.statusCode).toBe(200);
  });
});
```

Utiliser `app.inject()` de Fastify (pas besoin de supertest). DB de test via `DATABASE_URL` dans `.env.test`.

---

## Environnement local

### Architecture

```
Browser → https://<project>.dev → /etc/hosts → Caddy (HTTPS local) → localhost:PORT
```

Caddy gère le HTTPS local avec sa CA intégrée. Les domaines `.dev` nécessitent HTTPS (HSTS préchargé par les navigateurs).

### Caddy local

**Config :** `/data/infra/local-dev/Caddyfile`

**Installation (une fois) :**
```bash
# Installer Caddy
pkexec apt install caddy

# Installer la CA locale (certificats auto-signés trusted)
caddy trust
```

**Template pour un projet fullstack :**
```
<project>.dev {
    handle /api/* {
        reverse_proxy localhost:<backend-port>
    }
    handle /data/* {
        reverse_proxy localhost:<backend-port>
    }
    handle {
        reverse_proxy localhost:5173
    }
}
```

**Template pour un backend seul :**
```
<project>.dev {
    reverse_proxy localhost:<port>
}
```

**Recharger après modif :**
```bash
pkexec caddy reload --config /data/infra/local-dev/Caddyfile
```

### Honcho + Procfile

Chaque projet a un `Procfile` à sa racine. On lance avec `honcho start`.

```bash
# Installer (une fois)
pipx install honcho

# Lancer un projet
cd /data/projects/<project> && honcho start
```

Honcho gère : logs préfixés par process, cleanup au Ctrl+C, multi-process (db + app + worker).

**Exemples Procfile :**

Flask + PG Docker :
```
db: docker compose -f infra/local/docker-compose.yml up
app: PORT=5000 ./venv/bin/python -u app.py
```

FastAPI + PG Docker :
```
db: docker compose -f infra/local/docker-compose.yml up
app: .venv/bin/uvicorn app.backend.main:app --host 0.0.0.0 --port 8085 --reload
```

Next.js :
```
app: npm run dev
```

**Important :** `--reload` pour le hot reload en dev. En prod, **jamais** de `--reload`.

### Config centrale

**Répertoire :** `/data/infra/local-dev/`

| Fichier | Rôle |
|---------|------|
| `ports.conf` | Registre des ports (source de vérité) |
| `Caddyfile` | Reverse proxy *.dev → localhost:PORT |
| `start-all.sh` | Lance tous les projets en tmux |
| `check-ports.sh` | Vérifie cohérence ports/Caddy |

### Ports

**Source de vérité :** `/data/infra/local-dev/ports.conf`

| Port | Projet | Domaine |
|------|--------|---------|
| 5000 | tuls | tuls.dev |
| 5010 | otomata | otomata.dev |
| 8000 | yaats | yaats.dev |
| 3000 | landing-builder | landing.dev |
| 3001 | ytmusic-manager | ytmusic.dev |
| 5173 | headless-crm | hcrm.dev |
| 5001 | financex | financex.dev |
| 3002 | roundtable | rtx.dev |
| 8080 | o-browser | browser.dev |
| 8765 | stocktrotter | stocktrotter.dev |
| 5174 | 4-as-agent-front | albaron.dev |
| 8085 | 4-as-agent | albaron.dev |
| 8086 | la-fabrique-by-ca | lfbca.dev |

**Plages de ports :**

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
3. Ajouter bloc dans `/data/infra/local-dev/Caddyfile`
4. `echo "127.0.0.1 <project>.dev" | pkexec tee -a /etc/hosts`
5. `pkexec caddy reload --config /data/infra/local-dev/Caddyfile`
6. Créer un `Procfile` à la racine du projet
7. (optionnel) Ajouter une window tmux dans `start-all.sh`

### Lancer tous les projets

```bash
/data/infra/local-dev/start-all.sh     # Lance en tmux
tmux attach -t dev                      # Voir les logs
tmux kill-session -t dev                # Arrêter tout
```

---

## API Documentation

Swagger UI automatique via les Zod schemas. Rien à maintenir manuellement.

```typescript
// Dans index.ts
await app.register(swagger, {
  openapi: { info: { title: "<Project> API", version: "1.0.0" } },
  transform: jsonSchemaTransform,
});
await app.register(swaggerUi, { routePrefix: "/api/docs" });
```

- **Swagger UI** : `/api/docs` (interactif, testable)
- **Spec OpenAPI JSON** : `/api/doc` (pour clients auto-générés)
- Chaque route avec `schema: { body, querystring, params, response }` en Zod est auto-documentée

## Gestion de projet

Issues GitHub comme backlog. Voir `/projects` pour la gestion cross-repo.

```bash
# Créer une issue
gh issue create --title "Feature X" --body "Description" --label "enhancement"

# Lister les issues
gh issue list

# Fermer
gh issue close 42
```

Labels standard : `bug`, `enhancement`, `infra`, `design`.

## Conventions

- API RESTful sous `/api/*`
- OpenAPI auto-générée depuis les Zod schemas
- Swagger UI sur `/api/docs`
- Routes protégées par `authPreHandler` (Fastify preHandler hook)
- Frontend : composants dans `components/`, pages dans `views/`
- Fichiers runtime servis par Fastify via @fastify/static sur `/data/*`
- DB : PostgreSQL Docker local (port 5434), natif en prod
- Pas de fichier > 500 lignes
- Pas de code legacy, pas de fallbacks (lever une erreur)
