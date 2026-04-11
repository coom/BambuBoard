# Bambu Dashboard

![Supports amd64][amd64-shield]
![Supports aarch64][aarch64-shield]
![Supports armv7][armv7-shield]

Dashboard AMS Bambu Lab avec suivi des bobines, KPIs de consommation et
notifications de stock bas — intégré directement dans Home Assistant via
l'ingress.

## Fonctionnalités

- **Connexion MQTT directe** à l'imprimante (TLS, port 8883) — pas besoin
  de la Bambu Cloud ni du Bambu Studio
- **Vue AMS temps réel** : état des 4 slots, type/couleur/poids restant
- **Inventaire bobines** : catalogue persistant, réconciliation auto
  via `tray_uuid`, cycle `active → idle → empty → archived`
- **KPIs** : consommation totale, sessions d'impression, top matériaux,
  consommation sur 7/30 jours
- **Notifications stock bas** : webhook Home Assistant quand une bobine
  descend sous un seuil configurable
- **Scan NFC Bambu** : reconnaissance des bobines 2024+ via un Flipper
  Zero (voir [`flipper/bambu_scanner/`](../flipper/bambu_scanner/))

## Installation rapide

1. Ajoute ce dépôt dans **Paramètres → Modules complémentaires →
   Boutique → Dépôts** :
   `https://code.e-odyssey.net/coom/bambuboard`
2. Installe **Bambu Dashboard** depuis la section qui apparaît
3. Remplis les 3 champs obligatoires (`printer_ip`, `printer_serial`,
   `printer_access_code`) — voir **Documentation** pour les récupérer
4. Démarre l'add-on et ouvre l'interface Web

## Configuration minimale

```yaml
printer_ip: "192.168.1.42"
printer_serial: "01P00A1B2C3D4E5F"
printer_access_code: "12345678"
```

Voir l'onglet **Documentation** pour les options complètes, la
récupération des identifiants de l'imprimante, et le troubleshooting.

[amd64-shield]: https://img.shields.io/badge/amd64-yes-green.svg
[aarch64-shield]: https://img.shields.io/badge/aarch64-yes-green.svg
[armv7-shield]: https://img.shields.io/badge/armv7-yes-green.svg
