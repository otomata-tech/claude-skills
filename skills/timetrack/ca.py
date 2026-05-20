#!/usr/bin/env python3
"""CA analytique par période de travail.

Agrège le CA Pennylane par mois de travail (pas par date d'émission)
en liant chaque facture aux time-entries via invoiceId.

Pro-rata : si une facture couvre plusieurs mois (entrées dans plusieurs
mois), le montant HT/TTC est réparti au prorata des heures loguées.

Usage:
    python3 ca.py [--year YEAR] [--no-drafts]
"""
import argparse
import json
import re
import subprocess
from collections import Counter, defaultdict


def canonical(inv_id):
    """Normalise 'F2026-001' → 'F2026-1', garde 'PL-<id>' tel quel."""
    if not inv_id:
        return None
    s = inv_id.strip()
    if s.startswith('PL-'):
        return s
    m = re.match(r'^F(\d{4})-0*(\d+)$', s)
    return f'F{m.group(1)}-{int(m.group(2))}' if m else s


def client_from_label(label):
    """'Facture La Fabrique by CA - F2026-6 (label généré)' → 'La Fabrique by CA'."""
    m = re.match(r'^Facture (.+?)(?:\s*-\s*F\d+-\d+)?\s*\(label', label or '')
    return m.group(1).strip() if m else (label or '')[:30]


def fetch_invoices():
    r = subprocess.run(['oto', 'pennylane', 'customer-invoices'],
                       capture_output=True, text=True, check=True)
    return json.loads(r.stdout)


def fetch_entries():
    """Lit les time entries depuis le datastore (namespace `timetrack`)."""
    r = subprocess.run(['oto', 'data', 'list', 'timetrack', '--limit', '10000'],
                       capture_output=True, text=True, check=True)
    return json.loads(r.stdout)['rows']


def period_from_emission(date_str):
    """Fallback: facture émise J1-J7 = travail mois précédent."""
    if not date_str:
        return 'unknown'
    y, m, d = map(int, date_str.split('-'))
    if d <= 7:
        m -= 1
        if m == 0:
            m, y = 12, y - 1
    return f'{y:04d}-{m:02d}'


def attribute_invoice(inv, entries):
    """Renvoie [(période, part_ht, part_ttc, hours), ...].

    Règle :
    - Si les time-entries couvrent plusieurs mois → prorata par heures
    - Sinon → date d'émission de la facture (J1-J7 → mois précédent)
    """
    ht = float(inv.get('currency_amount_before_tax') or 0)
    ttc = float(inv.get('currency_amount') or 0)

    if entries:
        hours_by_month = defaultdict(float)
        for e in entries:
            hours_by_month[e['date'][:7]] += e['hours']
        if len(hours_by_month) > 1:
            total_h = sum(hours_by_month.values())
            return [(p, ht * h / total_h, ttc * h / total_h, h)
                    for p, h in hours_by_month.items()]

    # Single month of entries (or no entries) → date d'émission
    hours = sum(e['hours'] for e in entries) if entries else 0
    return [(period_from_emission(inv.get('date')), ht, ttc, hours)]


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--year', type=int, help='Filtrer sur une année')
    p.add_argument('--no-drafts', action='store_true', help='Exclure les drafts')
    args = p.parse_args()

    entries = fetch_entries()
    invoices = fetch_invoices()

    # Lookup canonique : F-number ET PL-<id> pointent vers le même objet
    inv_by_id = {}
    for inv in invoices:
        fnum = canonical(inv.get('invoice_number'))
        if fnum:
            inv_by_id[fnum] = inv
        inv_by_id[f"PL-{inv.get('id')}"] = inv

    # Grouper entrées par facture (billed=true uniquement)
    entries_by_inv = defaultdict(list)
    unbilled = []
    for e in entries:
        cid = canonical(e.get('invoiceId'))
        if e.get('billed') and cid:
            entries_by_inv[cid].append(e)
        elif 'NON FACTURABLE' not in (e.get('note') or '') and not e['project'].startswith('321-'):
            unbilled.append(e)

    # Agréger par période (en itérant sur invoices uniques)
    by_period = defaultdict(lambda: {'ht': 0, 'ttc': 0, 'hours': 0, 'lines': []})
    inv_no_entries = []
    seen_ids = set()

    for inv in invoices:
        if inv['id'] in seen_ids:
            continue
        seen_ids.add(inv['id'])
        if args.no_drafts and inv.get('draft'):
            continue

        # Chercher entrées associées (via F-number ou PL-<id>)
        fnum = canonical(inv.get('invoice_number'))
        pl_id = f"PL-{inv['id']}"
        ent = entries_by_inv.get(fnum, []) + entries_by_inv.get(pl_id, [])
        if not ent:
            inv_no_entries.append(fnum or pl_id)

        display_id = fnum or pl_id
        client = client_from_label(inv.get('label', ''))
        is_draft = bool(inv.get('draft'))

        for period, part_ht, part_ttc, h in attribute_invoice(inv, ent):
            if args.year and not period.startswith(str(args.year)):
                continue
            by_period[period]['ht'] += part_ht
            by_period[period]['ttc'] += part_ttc
            by_period[period]['hours'] += h
            by_period[period]['lines'].append((display_id, client, part_ht, is_draft))

    # Output
    print(f"\n{'Mois':<10} {'HT':>10} {'TTC':>10} {'Jours':>7}  Factures (HT part)")
    print('-' * 115)
    tot = {'ht': 0, 'ttc': 0, 'hours': 0}
    for m in sorted(by_period.keys()):
        if m == 'unknown':
            continue
        v = by_period[m]
        for k in tot:
            tot[k] += v[k]
        inv_str = ' · '.join(
            f"{cid}{'*' if dr else ''} {cl[:18]} ({h:,.0f})"
            for cid, cl, h, dr in v['lines']
        )
        days = v['hours'] / 7
        print(f"{m:<10} {v['ht']:>9,.0f}€ {v['ttc']:>9,.0f}€ {days:>6,.1f}j  {inv_str[:90]}")
    print('-' * 115)
    days_tot = tot['hours'] / 7
    print(f"{'TOTAL':<10} {tot['ht']:>9,.0f}€ {tot['ttc']:>9,.0f}€ {days_tot:>6,.1f}j")
    print("\n* = draft (proforma non finalisée) · multi-mois = prorata heures")

    if unbilled:
        print(f"\n⚠️  {len(unbilled)} entrées non facturées / non rapprochées :")
        ub = defaultdict(float)
        for e in unbilled:
            ub[e['project']] += e['hours']
        for proj, h in sorted(ub.items(), key=lambda x: -x[1]):
            print(f"   {proj:28}  {h:>6,.1f}h  ({h/7:.1f}j)")

    if inv_no_entries:
        print(f"\n⚠️  {len(inv_no_entries)} facture(s) sans entrées time-entries "
              f"(période estimée via date d'émission)")


if __name__ == '__main__':
    main()
