# Documentation — Configuration du widget Gantt Grist

## Vue d'ensemble

Le widget a deux niveaux de configuration, chacun géré par un mécanisme Grist différent.

```
┌─────────────────────────────────────────────────────────────────┐
│  PANEL NATIF GRIST  (icône ⚙️ Colonnes du widget)              │
│                                                                  │
│  Table principale (Tasks)                                        │
│    → sélectionnée via le panneau "Table" du widget              │
│    → nom récupéré automatiquement via selectedTable.getTableId() │
│                                                                  │
│  Colonnes de Tasks                                               │
│    → mappées via le panneau "Colonnes" du widget                 │
│    → déclarées dans grist.ready({ columns })                     │
│    → reçues à l'exécution via onRecords(mappings)               │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│  PANEL DE CONFIG DU SCRIPT  (bouton ⚙️ dans le widget)         │
│                                                                  │
│  Tables secondaires + leurs colonnes                             │
│    → responsables, opérations, catégories de tâches             │
│    → persistés via grist.setOptions / grist.onOptions           │
│    → partagés entre tous les utilisateurs du document           │
│    → survivent aux déconnexions et rechargements                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 1. Variables runtime

```javascript
// ── Table principale ────────────────────────────────────────────
let TABLE = {
    tasks:             null,   // rempli par onRecords → getTableId()
    responsableProjet: null,   // rempli par onOptions → applyOptions()
    operations:        null,   // rempli par onOptions → applyOptions()
    phases:            null,   // rempli par onOptions → applyOptions()
};
let _mainTableId = null;       // copie de TABLE.tasks, pour filtrer les selects

// ── Colonnes Tasks ───────────────────────────────────────────────
// Initialisées avec les noms logiques (= les 'name' déclarés dans grist.ready).
// Grist les remplace par les noms physiques réels via onRecords(mappings).
const TASK_COL_KEYS = { titre, dateDebut, duree, statut, ... };
let COL = { ...TASK_COL_KEYS };

// ── Colonnes des tables secondaires ─────────────────────────────
// Initialisées à null. Remplies par applyOptions() au chargement.
let COL_CHEF   = { nom: null, fonction: null, actif: null };
let COL_OPS    = { nom: null, numOpe: null, statut: null };
let COL_PHASES = { nom: null, numOrder: null, couleur: null };
```

---

## 2. Options persistées (clés grist.setOptions)

Ces clés sont stockées dans le document Grist par `saveConfig()` et relues par `onOptions()`.

| Clé                 | Cible runtime              | Description                       |
|---------------------|----------------------------|-----------------------------------|
| `_configured`       | *(sentinel)*               | `true` si config sauvegardée ≥1x  |
| `tableChefProjet`   | `TABLE.responsableProjet`  | Nom Grist de la table responsables|
| `tableOperations`   | `TABLE.operations`         | Nom Grist de la table opérations  |
| `tablePhases`       | `TABLE.phases`             | Nom Grist de la table catégories  |
| `colChefNom`        | `COL_CHEF.nom`             | Colonne nom affiché (responsable) |
| `colChefFonction`   | `COL_CHEF.fonction`        | Colonne fonction                  |
| `colChefActif`      | `COL_CHEF.actif`           | Colonne booléen actif             |
| `colOpsNom`         | `COL_OPS.nom`              | Colonne nom opération             |
| `colOpsNumOpe`      | `COL_OPS.numOpe`           | Colonne numéro opération          |
| `colOpsStatut`      | `COL_OPS.statut`           | Colonne statut opération          |
| `colPhasesNom`      | `COL_PHASES.nom`           | Colonne nom catégorie             |
| `colPhasesNumOrder` | `COL_PHASES.numOrder`      | Colonne numéro d'ordre            |
| `colPhasesCouleur`  | `COL_PHASES.couleur`       | Colonne couleur (hex)             |
| `colTitreAdapte`    | `COL.titreAdapte`          | Colonne titre adapté (Tasks)      |

---

## 3. Séquence d'initialisation

```
grist.ready({ columns: [...] })
        │
        ├─► onRecords(records, mappings)  ──────────────────────────────┐
        │       │                                                        │
        │       ├─ 1er appel : getTableId() → TABLE.tasks, _mainTableId │
        │       ├─ applyMappings(mappings) → COL.*                      │
        │       └─ setTimeout(50ms) ─► await optionsReady ─────────────►│
        │                                                                │
        └─► onOptions(gristOptions)                                      │
                │                                                        │
                ├─ options = gristOptions ?? lsLoadOptions()  ◄── fallback localStorage
                │                                             (Ctrl+Shift+R → Grist envoie null)
                ├─ applyOptions(options) → TABLE.*, COL_CHEF.*, COL_OPS.*, COL_PHASES.*
                ├─ resolveOptionsReady() ◄── débloque onRecords ────────►│
                │                                                        │
                └─ hasConfig ?                                           │
                    OUI → (rien)                                         │
                    NON → openConfigPanel() après 400ms                  │
                                                                         │
                                                          loadAllData() ◄┘
                                                              │
                                                              ├─ fetchTable(TABLE.tasks) → tasks[]
                                                              ├─ loadSecondaryData()
                                                              │     ├─ TABLE.responsableProjet null ? → team=[]
                                                              │     ├─ TABLE.operations null ?        → projects=[]
                                                              │     └─ TABLE.phases null ?            → phases=[]
                                                              │         sinon fetchTable → données + checkMissingCols
                                                              └─ render()
```

**Point critique :** `onRecords` et `onOptions` peuvent arriver dans n'importe quel ordre.
La `Promise optionsReady` garantit que `loadAllData` attend toujours `applyOptions`.

---

## 4. Cache localStorage

Grist envoie `onOptions(null)` dans deux situations :
- **Hard refresh** (Ctrl+Shift+R) : comportement documenté de Grist
- **Table renommée** : Grist efface les options si une table référencée disparaît

Le cache localStorage est une copie de sauvegarde écrite à chaque `saveConfig()` :

```javascript
const LS_KEY = 'gantt_config_' + (hostname + pathname).replace(/[^a-z0-9]/gi, '_');
// Clé unique par URL → indépendante entre projets Grist différents
```

Priorité de lecture : `gristOptions` (Grist) → `lsLoadOptions()` (cache) → `null`

---

## 5. Sauvegarde de la config (saveConfig)

Appelée par le bouton "Enregistrer" du panel de config du script.

```
1. Lire les valeurs des selects HTML (cfg-tableChefProjet, cfg-colChefNom, ...)
2. Appliquer immédiatement → TABLE.*, COL_CHEF.*, COL_OPS.*, COL_PHASES.*
3. Construire l'objet opts { _configured: true, tableChefProjet, ..., colPhasesNumOrder, ... }
4. lsSaveOptions(opts)        → localStorage (fallback Ctrl+Shift+R)
5. await grist.setOptions(opts) → document Grist (persistance principale)
6. closeConfigPanel()
7. await loadAllData()        → recharger avec les nouveaux noms
```

`gristReady` est positionné à `true` dès le début de `initGrist()` (avant `loadAllData`),
ce qui permet à `saveConfig` d'appeler `setOptions` même si le panel s'est ouvert
avant le premier chargement complet des données.

---

## 6. Détection des problèmes au chargement

`loadSecondaryData()` distingue deux situations :

| Situation | Comportement |
|-----------|-------------|
| `TABLE.x === null` | Table non encore configurée — ignorée silencieusement, données vides |
| `TABLE.x` défini mais fetchTable échoue | Table introuvable (renommée ?) — alerte rouge + panel de config |
| Colonne configurée absente des données | Alerte orange + panel de config |

---

## 7. Panel de config du script — éléments HTML

| ID élément              | data-group | data-col-role | Cible               |
|-------------------------|------------|---------------|---------------------|
| `cfg-tableChefProjet`   | —          | —             | TABLE.responsableProjet |
| `cfg-colChefNom`        | chef       | nom           | COL_CHEF.nom        |
| `cfg-colChefFonction`   | chef       | fonction      | COL_CHEF.fonction   |
| `cfg-colChefActif`      | chef       | actif         | COL_CHEF.actif      |
| `cfg-tableOperations`   | —          | —             | TABLE.operations    |
| `cfg-colOpsNom`         | ops        | nom           | COL_OPS.nom         |
| `cfg-colOpsNumOpe`      | ops        | numOpe        | COL_OPS.numOpe      |
| `cfg-colOpsStatut`      | ops        | statut        | COL_OPS.statut      |
| `cfg-tablePhases`       | —          | —             | TABLE.phases        |
| `cfg-colPhasesNom`      | phases     | nom           | COL_PHASES.nom      |
| `cfg-colPhasesNumOrder` | phases     | numOrder      | COL_PHASES.numOrder |
| `cfg-colPhasesCouleur`  | phases     | couleur       | COL_PHASES.couleur  |

`data-group` permet à `loadColumnsForGroup(group, tableName)` de peupler
tous les selects d'un groupe en une seule passe après sélection de la table.
`data-col-role` permet de retrouver la valeur courante dans `COL_CHEF/COL_OPS/COL_PHASES`.
