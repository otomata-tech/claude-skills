---
name: issue-triage
description: "Présente une issue GitHub à Alexis avant disposition (traiter/parquer/fermer/router), dans un format fixe : titre, labels, contexte, analyse, solution, risques. Utiliser à chaque fois qu'une issue oto est proposée pour validation."
disable-model-invocation: false
argument-hint: "[repo#numéro ...]"
---

# Triage d'issue oto

Fixe le format de présentation d'une issue GitHub avant que l'utilisateur ne tranche
sa disposition (traiter / parquer / fermer / router à un autre chantier). Ne remplace
pas l'analyse — cadre comment elle est rendue lisible.

## Pourquoi ce skill existe

Une présentation trop compacte (juste un numéro et une phrase) oblige l'utilisateur à
redemander le détail à chaque fois. Le gabarit ci-dessous porte tout ce qu'il faut pour
décider sans aller-retour : ce que dit l'issue, ce que ça vaut techniquement, ce que je
ferais, et ce qui pourrait coincer.

## Étape 1 — Récupérer l'issue

```
gh issue view <numéro> --repo otomata-tech/<repo> --json number,title,body,labels,createdAt,url
```

Lire le corps en entier — jamais tronqué à quelques centaines de caractères. Si l'issue
référence du code, l'ouvrir et vérifier l'état ACTUEL (le bug ou le gap peut déjà avoir
été corrigé par une autre session : `git log -S`, grep du symbole).

## Étape 2 — Gabarit de présentation

Pour chaque issue, produire ce bloc (en français, markdown) :

```
## #<numéro> — <titre> (<repo>)
<url>
**Labels** : <liste, ou "aucun">
**Créée** : <date ISO>

**Contexte**
<résumé fidèle du corps de l'issue — ce qui est observé/demandé, 3-5 lignes.
Ne pas interpréter ici, juste rapporter.>

**Analyse**
<mon diagnostic technique : où est le problème dans le code (fichier:ligne si
pertinent), pourquoi il existe, ce qu'il touche (autres fichiers, tests, ADR
concernée, surface servie). Si l'état a déjà changé depuis l'ouverture de
l'issue, le dire ici.>

**Solution proposée**
<ce que je ferais concrètement — taille du lot (petit correctif borné /
chantier à part), fichiers touchés.>

**Risques / dépendances**
<préavis nécessaire avant un tag ? dépend d'un autre chantier ou d'une
décision produit ? touche une surface servie à une campagne live ? aucun
risque identifié → le dire explicitement plutôt que d'omettre la rubrique.>
```

## Étape 3 — Soumettre la disposition via AskUserQuestion

Ne jamais enchaîner sur un texte qui se termine par "dis-moi" — la décision passe par
un appel à `AskUserQuestion`, une question par issue (ou groupées si elles partagent la
même option recommandée), avec des options du type :

- **Traiter** — correctif borné, je le fais maintenant
- **Parquer** — laissé OUVERT et en attente (jamais fermé ni ignoré ; cf. définition
  d'Alexis : parquer ≠ fermer)
- **Fermer** — plus pertinent / déjà résolu / décision produit tranchée sans code
- **Router à <chantier/session>** — hors de mon périmètre (ex. blueprint pour l'ADR-0070,
  oto cd pour un risque de déploiement)

Marquer l'option recommandée avec "(Recommandé)" quand une ressort clairement de
l'analyse, mais laisser toujours les alternatives réelles.

## Étape 4 — Après la décision

Exécuter la disposition choisie (fix + PR, label `parked` + commentaire de contexte,
fermeture avec commentaire, ou message à la session concernée) et ne jamais reformuler
la question déjà tranchée dans le même lot.
