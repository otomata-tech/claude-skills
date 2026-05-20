---
name: timetrack
description: "Time tracking for freelance missions. Log hours, list entries, show summaries by project/period. Entries in oto datastore namespace `timetrack` (Google Sheets via mcp.oto.ninja), missions in Attio Deals (oto attio deals)."
argument-hint: "[log|list|summary|missions] [args]"
---

# Time Tracking

Track billable hours for freelance missions.

## Sources de données

| Source | Rôle |
|--------|------|
| **Attio Deals** (`oto attio deals`) | **Référentiel missions** (source de vérité) : client, TJM, contacts, pennylane_* — via le slug |
| **oto datastore namespace `timetrack`** | **Entrées de temps** : heures loguées par jour/mission (clé = slug du Deal) |

Les missions actives sont les Deals avec `stage=Active`. Ne jamais dupliquer les infos mission dans le datastore.

Historique pré-2026-05-20 : `/mnt/otomata/time-entries.json` (archive read-only, migré dans le datastore).

## Commands

| Command | Description |
|---------|-------------|
| `/timetrack log <slug> <hours> [note]` | Log hours for today |
| `/timetrack log <slug> <hours> <date> [note]` | Log hours for a specific date (YYYY-MM-DD) |
| `/timetrack list [slug] [--month YYYY-MM]` | List entries, optionally filtered |
| `/timetrack summary [slug] [--month YYYY-MM]` | Summary: total hours, amount, billed/unbilled |
| `/timetrack missions` | List active missions with client et TJM |
| `/timetrack ca [--year YYYY] [--no-drafts]` | CA par période de travail (Pennylane × entries) |

Default (no subcommand): `summary` for current month.

## Storage

Datastore namespace `timetrack` — un Google Sheet per-user dans le Drive Alexis, schéma libre. Colonnes utilisateur : `date` (YYYY-MM-DD), `project` (slug Attio), `hours` (number), `billed` (bool), `invoiceId` (`F2026-N` ou `PL-<pennylane_id>` ou null), `note`. Colonnes auto : `_id` UUID, `_created_at`, `_updated_at`.

Lire/écrire :
```bash
oto data list timetrack [--filter project=<slug>] [--limit N]
oto data append timetrack '{"date":"...","project":"...","hours":N,"billed":bool,"invoiceId":"...","note":"..."}'
oto data update timetrack <_id> '{"billed":true,"invoiceId":"F2026-X"}'
oto data rm-row timetrack <_id>
oto data url timetrack                       # ouvre le Sheet dans le navigateur
```

## log

1. Vérifier que le Deal existe : `oto attio deal <slug>` → si pas trouvé, erreur. Accepter aussi les missions terminées (stage `Won 🎉`) pour facturation tardive.
2. `oto data append timetrack '{"date":"<date>","project":"<slug>","hours":<n>,"billed":false,"invoiceId":null,"note":"<note>"}'`
3. Show confirmation: `Logged Xh on <slug> (<date>) — "<note>"` + le `_id` retourné (pour update/delete éventuels).

## list

1. `oto data list timetrack --filter project=<slug> --limit 1000` (ou sans filter)
2. Parser JSON, filtrer par mois côté client si `--month` (le datastore ne fait que des filtres exacts).
3. Display as table:
   ```
   Date        Mission       Hours  Note
   2026-03-15  roundtable    7.0    Jour 1
   ```
4. Total hours at bottom.

## summary

1. `oto attio deal <slug>` → extraire `tjm.currency_value` et nom client.
2. `oto data list timetrack --filter project=<slug>` → filtrer par mois côté client.
3. Show:
   - Total hours (billed / unbilled)
   - Total amount (hours × TJM/7)
   - Breakdown by mission if no slug filter

## ca

Vue analytique du CA par **période de travail**, ventilée au prorata des heures quand une facture couvre plusieurs mois.

Exécuter : `python3 ~/.claude/skills/timetrack/ca.py [--year YYYY] [--no-drafts]`

Le script :
1. Lit entries via `oto data list timetrack` + factures Pennylane (`oto pennylane customer-invoices`)
2. Lie chaque facture aux entrées via `invoiceId` (F-number ou `PL-<pennylane_id>`)
3. Attribue la période selon cette règle :
   - **Si les entrées couvrent plusieurs mois** → prorata par heures (ex. Movinmotion 0,5j mars + 2j avril)
   - **Sinon** → date d'émission de la facture (J1-J7 = mois précédent, sinon mois d'émission)
4. Affiche HT/TTC par mois + factures (marquées `*` si draft) + entrées non facturées + factures sans entrées

## missions

`oto attio deals --stage Active` → parser la sortie JSON et afficher :
```
Slug                Client                TJM    Contact
roundtable          Roundtable            700    Simon Ternoir
la-fabrique-ca      La Fabrique by CA     725    Charlotte Guyard
stephanie-le-beuze  Stéphanie Le Beuze    800    Stéphanie Le Beuze
```

Le contact vient de `associated_people[0]` sur le Deal (besoin d'un `oto attio deal <slug>` pour chaque, ou parser directement depuis `oto attio deals`).

## Règles

- Le slug doit matcher un Deal Attio existant (tous stages acceptés pour logging ; `missions` ne liste que stage=Active)
- TJM et infos client viennent exclusivement du Deal Attio
- Le datastore ne contient que les entrées de temps
- Heures loguées en heures (7h = 1 jour). Le calcul montant utilise TJM/7.
- Pour update/delete une entrée : besoin de son `_id` (UUID), récupéré via `oto data list timetrack`.

## API Attio — formats retournés

`oto attio deals --stage Active` retourne :
```json
{"count": N, "deals": [{"id": "...", "slug": "...", "name": "...", "stage": "Active", "tjm": 700}, ...]}
```

`oto attio deal <slug>` retourne le record complet (valeurs sous `values.<attr>[0]`) :
- Client : `values.associated_company[0].target_record.values.name[0].value`
- Contact : `values.associated_people[0].target_record.values.name[0].full_name`
- TJM : `values.tjm[0].currency_value`
- Pennylane customer : `values.pennylane_customer_id[0].value`
