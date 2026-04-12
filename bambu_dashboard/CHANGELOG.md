# Changelog

## 1.0.12 — 2026-04-12

### Améliorations

- **Port 8000 exposé** : le port de l'add-on est désormais accessible
  directement sur le réseau local (`http://<IP_HA>:8000`), sans passer
  par l'ingress HA. Permet à l'app Android Bambu Scanner d'envoyer les
  scans NFC via `POST /api/nfc/push` sans authentification ingress.

## 1.0.11 — 2026-04-12

### Améliorations

- **Endpoint `/api/debug`** : diagnostic accessible en navigateur qui
  affiche la version, le hash MD5 du frontend servi, si l'overlay
  `/share/` est actif (et son propre hash), et le chemin de la DB.
  Permet de troubleshooter les problèmes de MAJ sans accès SSH.
- **Warning overlay au démarrage** : si un fichier
  `/share/bambu_dashboard/frontend/index.html` est détecté, les logs
  de l'add-on affichent un avertissement clair au lieu d'un simple
  « info ».

## 1.0.10 — 2026-04-12

### Améliorations

- **Clamp backend** : les valeurs `remain` négatives envoyées par l'AMS
  (dérive de l'estimation par longueur extrudée) sont désormais
  clampées à 0 **avant** stockage en DB et en `ams_state`, pas
  seulement à l'affichage.
- **Sync AMS configurable par bobine** : nouvelle case à cocher
  « Synchroniser le restant avec l'AMS » dans le modal d'édition
  (cochée par défaut). Quand décochée, un champ « Restant manuel (%) »
  apparaît et la valeur saisie n'est plus écrasée par les messages
  MQTT. Re-cocher la case réactive la synchro AMS. Colonne
  `ams_sync` ajoutée à la table `spools` (migration automatique).
- Suppression du bouton 🎯 (remplacé par la case à cocher dans le
  modal, plus ergonomique).

## 1.0.9 — 2026-04-12

### Améliorations

- **Clamp à 0 %** : les valeurs de remain négatives (dérive de
  l'estimation AMS) ne s'affichent plus. Le pourcentage et le poids
  sont plafonnés à 0 minimum dans l'inventaire (desktop et mobile).
- **Bouton Recalibrer 🎯** : nouveau bouton sur chaque bobine pour
  saisir manuellement le pourcentage restant réel (0–100). Utile quand
  l'AMS surestime la consommation ou quand on remet une bobine
  partiellement utilisée. L'endpoint `PUT /api/spools/{id}/calibrate`
  écrit un nouveau log de consommation et met à jour l'état AMS.

## 1.0.8 — 2026-04-12

### Corrections

- **Chips de filtre inventaire** : les compteurs « Toutes / Dans AMS /
  En stock / Vides » utilisent désormais `liveStatus()` (cross-check
  AMS live) au lieu du statut DB brut, qui pouvait être désynchronisé
  et afficher un total incorrect (ex : 8 « Dans AMS » alors que seules
  3 bobines étaient physiquement dans l'AMS). Le filtre par clic sur
  un chip utilise également le statut live.

## 1.0.7 — 2026-04-12

### Améliorations

- **Tri inventaire étendu** : les colonnes Statut et AMS sont désormais
  triables. Statut trie par ordre logique (Dans AMS → En stock → Vide →
  Archivé), AMS trie par numéro de slot (S1–S4, puis les bobines hors
  AMS).

## 1.0.6 — 2026-04-12

### Améliorations

- **Tri de l'inventaire** : les colonnes Bobine, Type, Restant et Poids
  sont cliquables pour trier (ascendant ▲ / descendant ▼).
- **Bouton supprimer** : croix rouge ✕ sur chaque bobine (desktop et
  mobile) avec popup de confirmation avant suppression définitive.
- **Fix statut temps réel** : le badge « Dans AMS » / « En stock » est
  désormais calculé en cross-checkant le `tray_uuid` avec les données
  AMS live, au lieu de lire le statut DB potentiellement désynchronisé.

## 1.0.5 — 2026-04-11

### 👥 Crédits

- Ajout des crédits d'auteurs dans les docs : **Erti** (développement
  principal de l'add-on) et **coom** (co-développement du module
  Flipper Zero `bambu_scanner`). Sections ajoutées au `README.md`
  racine, `bambu_dashboard/README.md`, `bambu_dashboard/DOCS.md`, et
  `flipper/bambu_scanner/README.md` *(nouvelle sous-section « Auteurs »
  dans l'attribution)*.

## 1.0.4 — 2026-04-11

### ✨ Documentation

- **Refonte visuelle complète** des docs : emojis, badges shields.io,
  tableaux stylisés, blockquotes de callout (💡 / ⚠️ / ❌ / ✅),
  sommaires avec icônes, et en-têtes centrés. Les 4 fichiers majeurs
  sont refaits : `README.md` racine, `bambu_dashboard/README.md`,
  `bambu_dashboard/DOCS.md`, et `flipper/bambu_scanner/README.md`.
- Plus aucun changement de code — **bump de version uniquement** pour
  que Home Assistant détecte la 1.0.4 et propose l'update.

## 1.0.3 — 2026-04-11

### Documentation

- **Plugin Flipper** : promotion du chemin qFlipper comme installation
  par défaut grâce au `.fap` pré-compilé désormais versionné dans
  `flipper/bambu_scanner/dist/` (plus besoin d'installer Python/ufbt
  pour la plupart des utilisateurs). Le chemin ufbt est réorienté vers
  les cas avancés (dev, firmware custom).
- **DOCS.md** : nouvelle section *Enregistrer une bobine inconnue
  depuis l'AMS* qui documente le pré-remplissage complet du modal avec
  le nom de couleur deviné depuis le hex (feature 1.0.2).
- **README racine** : lien direct vers le `.fap` pré-compilé.

## 1.0.2 — 2026-04-11

### Améliorations

- **Modal "Bobine inconnue — Enregistrer"** : le nom de couleur est
  désormais deviné automatiquement à partir du hex exposé par l'AMS
  (palette de 23 couleurs françaises, recherche par distance euclidienne
  RGB). La case **Couleur** est pré-remplie (ex : `Noir`, `Rouge`,
  `Turquoise`) et le **Nom** est suffixé avec la couleur (ex : `PLA
  Basic Noir`) pour distinguer visuellement les bobines d'un même type
  dans l'inventaire.

## 1.0.1 — 2026-04-11

### Corrections

- **Scan Flipper Zero** : `printf()` dans l'app FAP n'était pas routé vers
  l'USB CDC sur firmware Flipper officiel — le dashboard ne recevait
  jamais la ligne `BAMBU_NFC:`. Installation d'un callback stdout
  explicite (`furi_thread_set_stdout_callback`) qui pipe vers
  `furi_hal_cdc_send(0, ...)` avec chunking 64 B + délai inter-paquet.
- **Modal "Bobine inconnue — Enregistrer"** : le formulaire s'ouvrait
  avec seulement 5 champs pré-remplis. Désormais, tous les champs
  exposés par l'AMS sont pré-remplis : `name` (fallback sub_brands),
  `brand` (Bambu Lab), `filament_code` (tray_info_idx), `initial_weight`
  (tray_weight réel), `initial_remain` (remain courant, plus 100 par
  défaut).
- **Modal UX** : le titre et le libellé du bouton se basaient sur la
  présence de l'objet `spool` au lieu de son `id`, ce qui affichait
  "Modifier la bobine / Mettre à jour" lors d'une création pré-remplie.

### Documentation

- Restructuration du repo en dépôt d'add-ons HA importable via URL
  Supervisor (`repository.yaml` + sous-dossier `bambu_dashboard/`)
- `README.md` racine + `README.md` / `DOCS.md` / `CHANGELOG.md` pour
  l'add-on
- `build.yaml` citant les images base officielles HA pour amd64,
  aarch64, armv7
- Guide utilisateur complet pour le plugin Flipper Zero
  (`flipper/bambu_scanner/README.md`) : installation ufbt et qFlipper,
  usage, intégration dashboard, troubleshooting

## 1.0.0 — 2026-04-11

Première version publiée en tant qu'add-on Home Assistant importable.

### Fonctionnalités

- Connexion MQTT TLS directe à l'imprimante Bambu Lab (pas de Cloud)
- Vue AMS temps réel : 4 slots, type/couleur/poids restant
- Inventaire persistant des bobines avec réconciliation automatique
  via `tray_uuid` et cycle `active → idle → empty → archived`
- KPIs : consommation totale, sessions, top matériaux, 7/30 jours
- Notifications stock bas via webhook Home Assistant
- Scan NFC via Flipper Zero (app `bambu_scanner` séparée, Web Serial)
- Support multi-arch : `amd64`, `aarch64`, `armv7`
- Overlay frontend `/share/bambu_dashboard/frontend/` pour itération
  rapide sans rebuild Docker
