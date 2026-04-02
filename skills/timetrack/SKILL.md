---
name: timetrack
description: "Time tracking for freelance missions. Log hours, list entries, show summaries by project/period. Data in /data/pro/time-entries.json, missions in /data/pro/missions.yaml."
argument-hint: "[log|list|summary|missions] [args]"
---

# Time Tracking

Track billable hours for freelance missions.

## Sources de données

| Fichier | Rôle |
|---------|------|
| `/data/pro/missions.yaml` | **Référentiel missions** (source de vérité) : clients, TJM, contacts, Pennylane IDs |
| `/data/pro/time-entries.json` | **Entrées de temps** : heures loguées par jour/mission |

Les missions sont définies dans `missions.yaml` (sections `active` et `progress`). Ne jamais dupliquer les infos mission dans `time-entries.json`.

## Commands

| Command | Description |
|---------|-------------|
| `/timetrack log <slug> <hours> [note]` | Log hours for today |
| `/timetrack log <slug> <hours> <date> [note]` | Log hours for a specific date (YYYY-MM-DD) |
| `/timetrack list [slug] [--month YYYY-MM]` | List entries, optionally filtered |
| `/timetrack summary [slug] [--month YYYY-MM]` | Summary: total hours, amount, billed/unbilled |
| `/timetrack missions` | List active missions with client et TJM |

Default (no subcommand): `summary` for current month.

## Storage

**time-entries.json** — entrées uniquement, pas de définition de missions :
```json
{
  "entries": [
    {
      "id": "2026-03-15-001",
      "date": "2026-03-15",
      "project": "roundtable",
      "hours": 7,
      "billed": false,
      "invoiceId": null,
      "note": "Jour 1"
    }
  ]
}
```

## log

1. Lire `missions.yaml` → vérifier que le slug existe dans `active`. Sinon, erreur.
2. Generate ID: `<date>-<NNN>` (next sequence for that date).
3. Append entry to `entries` array in `time-entries.json`.
4. Show confirmation: `Logged Xh on <slug> (<date>) — "<note>"`

## list

1. Read entries, filter by slug and/or month.
2. Display as table:
   ```
   Date        Mission       Hours  Note
   2026-03-15  roundtable    7.0    Jour 1
   ```
3. Total hours at bottom.

## summary

1. Lire `missions.yaml` pour les TJM et infos client.
2. Filter entries by slug/month.
3. Show:
   - Total hours (billed / unbilled)
   - Total amount (hours × TJM/7 from missions.yaml)
   - Breakdown by mission if no slug filter

## missions

Lire `missions.yaml` et afficher les missions actives :
```
Slug                Client                TJM    Contact
roundtable          Roundtable            700    Simon Ternoir
la-fabrique-ca      La Fabrique by CA     —      Charlotte Guyard
stephanie-le-beuze  Stéphanie Le Beuze    800    Stéphanie Le Beuze
```

## Règles

- Le slug doit matcher une mission `active` dans `missions.yaml`
- TJM et infos client viennent exclusivement de `missions.yaml`
- `time-entries.json` ne contient que les entrées de temps (plus de section `projects`)
- Heures loguées en heures (7h = 1 jour). Le calcul montant utilise TJM/7.
