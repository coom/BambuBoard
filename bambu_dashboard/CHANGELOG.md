# Changelog

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
