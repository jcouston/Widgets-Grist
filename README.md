# Widgets Grist

Collection de widgets personnalisés pour [Grist](https://www.getgrist.com/).

## Widgets disponibles

### TaskFlow
Suite de gestion de projet avec 3 widgets interconnectés :
- **Kanban** — Tableau de tâches avec drag & drop
- **Gantt** — Diagramme de planification
- **Calendar** — Vue calendrier interactif

### Artefactory
IDE no-code pour composer des applications Grist :
- **Admin** — Configurateur d'applications
- **Runtime** — Exécuteur d'applications

## Installation

### Pour Grist self-hosted

Ajoutez cette variable d'environnement :

```bash
GRIST_WIDGET_LIST_URL=https://nicO1asFr.github.io/Widgets-Grist/manifest.json
```

Les widgets apparaîtront dans le menu "Custom Widget".

### Utilisation directe

Copiez l'URL d'un widget publié :
```
https://nicO1asFr.github.io/Widgets-Grist/taskflow/kanban/
https://nicO1asFr.github.io/Widgets-Grist/artefactory/runtime/
```

Dans Grist : Add Widget → Custom → Enter Custom URL

## Pour les développeurs

Voir [CLAUDE.md](CLAUDE.md) pour la documentation technique complète.

### Structure rapide

```
projects/          ← Développement (non publié)
published/         ← Production (déployé sur GitHub Pages)
packages/          ← Widgets avec build (React, etc.)
scripts/           ← Outils de gestion
```

### Commandes

```bash
npm run manifest   # Générer le catalogue
npm run promote    # Promouvoir un widget vers production
npm run serve      # Serveur local de test
```

## Licence

MIT
