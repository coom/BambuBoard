# Changelog

## 1.1.0 — 2026-04-17

### Changements

- **Interface bilingue FR/EN.** Le dashboard détecte automatiquement la
  langue du navigateur (FR par défaut, EN si le navigateur est en
  anglais). Un sélecteur **Automatique / Français / English** dans
  l'onglet Options permet de forcer la langue manuellement — le choix
  est persisté en `localStorage` (accès gardé par `try/catch` pour la
  navigation privée stricte).
- **Palette de couleurs bilingue** pour la déduction automatique du nom
  de couleur lors de l'enregistrement d'une bobine depuis un slot AMS
  (« Noir » en FR, « Black » en EN).
- **Dates et heures localisées** selon la langue active (format FR
  24 h vs EN 12 h AM/PM).
- **Backend :** nouvelle option `language: auto|fr|en` dans la config
  de l'add-on pour les messages d'erreur de l'API. `auto` se comporte
  comme `fr` (le frontend a sa propre auto-détection via
  `navigator.language`).
- **Documentation bilingue :** versions anglaises `README.en.md` et
  `DOCS.en.md` avec un bandeau de bascule FR/EN en tête de chaque
  document.

## 1.0.29 — 2026-04-16

### Changements

- **Conditionnement bobine** : nouveau champ « Bobine complète » /
  « Recharge » dans l'édition d'une bobine. Les recharges sont
  signalées par une icône `♻️` discrète dans l'inventaire (desktop,
  mobile et archivées). Toutes les bobines existantes restent en
  « Bobine complète » par défaut.

## 1.0.28 — 2026-04-13

### Corrections

- **Flipper .fap** : rebuild avec lecture tray_uuid (bloc 9).

## 1.0.27 — 2026-04-13

### Corrections

- **Fix JS cassé** : doublon de variable `trayUuid` dans le frontend
  qui empêchait le chargement de toutes les pages.

## 1.0.26 — 2026-04-13

### Changements

- **Unicité par tray_uuid** : l'identification des bobines utilise
  désormais le `tray_uuid` (lu depuis le tag NFC) comme critère
  principal, avec fallback sur `tag_uid`. Backend et frontend alignés.

## 1.0.25 — 2026-04-13

### Corrections

- **Tray UUID NFC** : le champ tray_uuid est correctement pré-rempli
  dans le formulaire d'ajout lors d'un scan NFC (nouvelles bobines et
  bobines existantes).
- **Affichage tray_uuid (Android)** : la card de résultat affiche le
  tray_uuid lu depuis le tag.

## 1.0.24 — 2026-04-13

### Nouveautés

- **Lecture du tray_uuid depuis le tag NFC** : le Flipper Zero et l'app
  Android lisent le bloc 9 (secteur 2) du tag MIFARE et transmettent
  le tray_uuid au dashboard. Le formulaire d'ajout est pré-rempli
  automatiquement.
- **Envoi automatique (Android)** : option cochable pour envoyer
  directement au dashboard après chaque scan NFC, sans interaction.
- **Bip sonore au scan (Android)** : confirmation sonore à chaque
  bobine détectée.

## 1.0.23 — 2026-04-12

### Nouveautés

- **Support multi-AMS** : le dashboard détecte et affiche tous les AMS
  connectés à l'imprimante (jusqu'à 4 AMS = 16 slots). La page AMS Live
  regroupe les slots par AMS avec un titre `AMS 1`, `AMS 2`, etc.
  Les badges de slot passent de `S1` à `A1:S1` quand plusieurs AMS sont
  détectés. Inventaire, statistiques et réconciliation fonctionnent
  avec les index globaux (0–15).

## 1.0.22 — 2026-04-12

### Suppressions

- **Bouton « + Racheter »** : supprimé de l'inventaire (mobile,
  desktop, archivées) et endpoint `POST /api/spools/{id}/rebuy`.
  Inutile depuis l'ajout du scan NFC offline.

## 1.0.21 — 2026-04-12

### Corrections

- **Faux logs de consommation** : quand une bobine scannée via NFC
  (log initial à 100 %) était ensuite vue par l'AMS à un % inférieur,
  le delta était faussement compté comme consommation (ex : 100 % → 0 %
  = −1000 g). Le backend aligne désormais le baseline au premier
  relevé AMS au lieu de logger un drop fictif. Migration automatique
  pour corriger les données existantes.

## 1.0.20 — 2026-04-12

### Corrections

- **Tag UID normalisé** : l'AMS envoie un `tag_uid` de 16 caractères
  (ex : `2A9153EF00000100`) alors que les scanners NFC Flipper/Android
  ne capturent que les 8 premiers (ex : `2A9153EF`). Tous les `tag_uid`
  sont désormais normalisés à 8 caractères (4 octets UID MIFARE) à la
  réception et en base. La réconciliation `tag_uid → tray_uuid`
  fonctionne quel que soit la source du scan.
- **Dédoublonnage automatique** : migration au démarrage qui détecte
  les bobines avec le même `tag_uid` (après normalisation), transfère
  les logs de consommation vers la bobine la plus ancienne, et supprime
  les doublons.

## 1.0.19 — 2026-04-12

### Corrections

- **Dernières impressions** : les sessions sans consommation (ajouts
  initiaux de bobines, logs à 100%) sont exclues. Seules les sessions
  avec une décroissance réelle apparaissent.
- **KPI « Bobines en stock »** : le compteur « dans AMS » affichait
  le nombre total de bobines avec statut `active` en base (ex : 19)
  au lieu du nombre réellement présent dans l'AMS (ex : 4). Le compteur
  utilise désormais la table `ams_state` pour refléter l'état physique
  réel de l'AMS.

### Suppressions

- **Notifications Home Assistant** : suppression complète du système
  de notifications par webhook (options `ha_webhook_url`,
  `ha_webhook_token`, `low_stock_threshold`, endpoint
  `/api/notifications/test`, module `notifications.py`, bouton
  « Tester la notification » dans la page Options). Le seuil stock bas
  reste affiché dans les KPIs à titre indicatif (fixé à 20%).

## 1.0.18 — 2026-04-12

### Corrections

- **Sessions d'impression inversées** : la progression de consommation
  s'affichait à l'envers (ex : 8% → 17% au lieu de 17% → 8%). Les
  champs `start_pct` / `end_pct` et `start_time` / `end_time` sont
  désormais en ordre chronologique correct.

### Améliorations

- **Nom du fichier imprimé** : le `subtask_name` (ou `gcode_file`) est
  capturé depuis les messages MQTT de l'imprimante et enregistré dans
  les logs de consommation. Affiché dans les sessions de la page
  Statistiques avec une icône document.
- Migration automatique : colonne `print_job` ajoutée à
  `consumption_logs`.

## 1.0.17 — 2026-04-12

### Améliorations

- **Thème vert Bambu** : toutes les couleurs d'accent (boutons, badges,
  chips, KPIs, inputs focus, etc.) passent de l'orange au vert Bambu
  (#00AE42) pour une identité visuelle cohérente.
- **Réconciliation `tray_uuid` sur scan NFC** : quand une bobine scannée
  (Android ou Flipper) est actuellement dans l'AMS, le `tray_uuid` est
  automatiquement résolu depuis l'état AMS live et pré-rempli dans le
  formulaire (ou utilisé lors de l'ajout automatique).

## 1.0.16 — 2026-04-12

### Améliorations

- **Logo** : "Board" passe du orange au vert Bambu (#00AE42)
- **Onglet "Maintenance" renommé "Options"**
- **Auto add NFC** : deux options dans la page Options permettent
  l'ajout automatique des bobines scannées (Android et/ou Flipper Zero)
  sans passer par le formulaire de confirmation. Les préférences sont
  sauvegardées dans le navigateur (localStorage).

## 1.0.15 — 2026-04-12

### Nouveautés

- **Application Android Bambu Scanner** : app compagnon pour scanner les
  bobines Bambu Lab via NFC (MIFARE Classic, clés dérivées par UID) et
  les enregistrer dans le dashboard en un tap. Thème Material Blue,
  icône NFC vectorielle, authentification par clé API. APK distribué
  dans `android/bambu_scanner/dist/`.
- **Documentation utilisateur Android** : guide complet d'installation,
  configuration du dashboard (port exposé, clé API), utilisation
  pas-à-pas et dépannage.

## 1.0.14 — 2026-04-12

### Améliorations

- **Clé API NFC** : nouvelle option `nfc_api_key` dans la configuration
  de l'add-on. Si renseignée, l'endpoint `POST /api/nfc/push` exige le
  header `X-API-Key` correspondant. Permet de sécuriser l'accès au port
  8000 exposé sans nécessiter un Long-Lived Access Token HA.

## 1.0.13 — 2026-04-12

### Corrections

- **Polling NFC pour app Android** : le frontend poll désormais
  `GET /api/nfc/pending` toutes les 3 secondes. Quand l'app Android
  (ou tout client externe) envoie un scan via `POST /api/nfc/push`,
  le modal d'enregistrement s'ouvre automatiquement dans le navigateur.
  Auparavant, seul le Flipper Zero fonctionnait (données reçues via
  Web Serial, sans passer par le backend).

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
