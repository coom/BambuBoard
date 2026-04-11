# Changelog

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
