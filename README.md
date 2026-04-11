# Bambu Dashboard — Home Assistant Add-ons

Dépôt d'add-ons Home Assistant pour superviser une imprimante Bambu Lab
avec AMS : suivi de bobines, KPIs de consommation, notifications de stock
bas, et scan NFC des bobines 2024+ via un Flipper Zero.

## Ajouter ce dépôt dans Home Assistant

1. Ouvrir **Paramètres → Modules complémentaires → Boutique des modules complémentaires**
2. Menu ⋮ (en haut à droite) → **Dépôts**
3. Coller l'URL :
   ```
   https://code.e-odyssey.net/coom/bambuboard
   ```
4. **Ajouter** → fermer la boîte de dialogue
5. La section **Bambu Dashboard Add-ons** apparaît en bas de la boutique
6. Cliquer sur **Bambu Dashboard** → **Installer**
7. Configurer les options (`printer_ip`, `printer_serial`, `printer_access_code`)
8. **Démarrer**, puis **Ouvrir l'interface Web** (via l'ingress HA)

## Add-ons inclus

| Add-on | Description |
|---|---|
| [Bambu Dashboard](./bambu_dashboard/) | Dashboard complet : AMS, inventaire bobines, KPIs, scan NFC Flipper |

## Plugin Flipper Zero (optionnel)

Le dossier [`flipper/bambu_scanner/`](./flipper/bambu_scanner/) contient
une application Flipper Zero qui scanne les tags NFC des bobines Bambu
Lab et les envoie au dashboard via USB Web Serial. Il s'installe
indépendamment de Home Assistant — voir le
[README du plugin](./flipper/bambu_scanner/README.md) pour le build et
l'installation sur le Flipper.

## Architecture

```
┌────────────┐  MQTT TLS   ┌─────────────────┐  HTTPS ingress  ┌─────────┐
│ Imprimante │ ──────────▶ │ bambu_dashboard │ ──────────────▶ │ Browser │
│ Bambu Lab  │             │  (add-on HA)    │                 │  (SPA)  │
└────────────┘             └─────────────────┘                 └────┬────┘
                                   │                                │ Web Serial
                                   │ Webhook low-stock              │
                                   ▼                                ▼
                            ┌─────────────┐                  ┌─────────────┐
                            │ HA Notify   │                  │ Flipper Zero│
                            └─────────────┘                  │ bambu_scan. │
                                                             └─────────────┘
```

## Compatibilité

- **Imprimantes** : toute imprimante Bambu Lab avec AMS (X1/X1C/X1E, P1S, P1P, A1, A1 mini)
- **Architectures HA** : amd64, aarch64, armv7
- **Navigateurs** (pour le scan NFC Flipper) : Chrome ou Edge uniquement (Web Serial API requise)

## Licence

MIT pour le code du dashboard. Voir
[`flipper/bambu_scanner/README.md`](./flipper/bambu_scanner/README.md) pour
les licences spécifiques à l'app Flipper (KDF importée de BambuTagger,
"educational and personal use").
