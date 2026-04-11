<div align="center">

# 🎨 Bambu Dashboard

### *Dépôt d'add-ons Home Assistant pour suivre, inventorier et optimiser tes bobines Bambu Lab*

![amd64](https://img.shields.io/badge/amd64-supported-success?style=flat-square)
![aarch64](https://img.shields.io/badge/aarch64-supported-success?style=flat-square)
![armv7](https://img.shields.io/badge/armv7-supported-success?style=flat-square)
![HA Add-on](https://img.shields.io/badge/Home%20Assistant-Add--on-41BDF5?style=flat-square&logo=home-assistant&logoColor=white)
![License](https://img.shields.io/badge/license-MIT-blue?style=flat-square)

**MQTT LAN direct** *·* **AMS temps réel** *·* **Inventaire bobines** *·* **KPIs** *·* **Scan NFC Flipper Zero**

</div>

---

## ✨ Ce que tu obtiens

| | |
|---|---|
| 🖨️ **AMS temps réel** | Les 4 slots, couleur, type, poids restant, affichés en direct via MQTT TLS |
| 📦 **Inventaire persistant** | Catalogue des bobines avec réconciliation auto `tray_uuid` → `active/idle/empty/archived` |
| 📊 **KPIs** | Consommation totale, sessions, top matériaux, 7/30 derniers jours |
| 🔔 **Alertes stock bas** | Webhook Home Assistant automatique sous un seuil configurable |
| 🏷️ **Scan NFC Bambu** | Lecture des tags des bobines 2024+ via un Flipper Zero — **le `.fap` est fourni pré-compilé** |
| 🚫 **Zéro Cloud Bambu** | Tout est local, LAN uniquement, pas de compte requis |

---

## 🚀 Installation en 30 secondes

> 1️⃣ Ouvre **Paramètres → Modules complémentaires → Boutique**
>
> 2️⃣ Menu **⋮** (en haut à droite) → **Dépôts**
>
> 3️⃣ Colle l'URL ci-dessous et clique **Ajouter** :
>
> ```
> https://code.e-odyssey.net/coom/bambuboard
> ```
>
> 4️⃣ La section **Bambu Dashboard Add-ons** apparaît ✨
>
> 5️⃣ Clique **Bambu Dashboard → Installer**
>
> 6️⃣ Renseigne `printer_ip`, `printer_serial`, `printer_access_code`
>
> 7️⃣ **Démarrer** → **Ouvrir l'interface Web** 🎉

---

## 📦 Add-ons inclus

| Add-on | Description | Version |
|---|---|:---:|
| 🎨 [**Bambu Dashboard**](./bambu_dashboard/) | Dashboard complet : AMS, inventaire, KPIs, scan NFC | ![v1.0.3](https://img.shields.io/badge/v1.0.3-latest-success?style=flat-square) |

---

## 🛰️ Plugin Flipper Zero *(optionnel mais cool)*

Le dossier [`flipper/bambu_scanner/`](./flipper/bambu_scanner/) contient une app
Flipper Zero qui scanne les tags NFC des bobines Bambu Lab (clés dérivées par
UID, compatibles bobines **2024+**) et envoie les métadonnées au dashboard via
**USB Web Serial**.

> 💡 **Bonne nouvelle** : un `.fap` pré-compilé (SDK officiel 1.4.3) est
> directement versionné à
> [`flipper/bambu_scanner/dist/bambu_scanner.fap`](./flipper/bambu_scanner/dist/bambu_scanner.fap).
>
> **Pas besoin de Python, d'ufbt, ni de toolchain** — télécharge, drag-and-drop
> dans qFlipper, c'est installé. ✨

Les détails (build custom, firmware alternatif, troubleshooting) sont dans le
[**README du plugin**](./flipper/bambu_scanner/README.md).

---

## 🏗️ Architecture

```
┌────────────────┐   MQTT TLS :8883   ┌─────────────────────┐
│   Imprimante   │ ──────────────────▶│   bambu_dashboard   │
│   Bambu Lab    │      (LAN only)    │     (add-on HA)     │
└────────────────┘                    └──────────┬──────────┘
                                                 │
                          ┌──────────────────────┼──────────────────────┐
                          │                      │                      │
                          ▼                      ▼                      ▼
                  HTTPS ingress HA         Webhook HA            Web Serial API
                          │                      │                      │
                          ▼                      ▼                      ▼
                  ┌──────────────┐       ┌─────────────┐         ┌──────────────┐
                  │  Navigateur  │       │  HA Notify  │         │ Flipper Zero │
                  │  (SPA vanilla)│       │   (mobile)  │         │ bambu_scanner│
                  └──────────────┘       └─────────────┘         └──────────────┘
```

---

## ✅ Compatibilité

| | |
|---|---|
| 🖨️ **Imprimantes** | Toute Bambu Lab avec AMS — *X1 / X1C / X1E / P1S / P1P / A1 / A1 mini* |
| 🏗️ **Architectures HA** | `amd64` · `aarch64` · `armv7` |
| 🌐 **Navigateurs** *(scan NFC)* | **Chrome** ou **Edge** uniquement — *Web Serial API requise* |
| 📡 **Mode imprimante** | **LAN uniquement** ou LAN + Cloud *(MQTT local obligatoire)* |

---

## 👥 Crédits

| Rôle | Personne |
|---|---|
| 🧑‍💻 **Développement principal** | **Erti** *(add-on HA : backend FastAPI, frontend SPA, inventaire, KPIs, scan NFC côté dashboard)* |
| 🛰️ **Co-développement module Flipper Zero** | **coom** *(assistance sur l'app `bambu_scanner` : routage CDC stdout, packaging ufbt, intégration série)* |

> 💡 Contributions upstream *(KDF BambuTagger, parser dérivé de
> `flipper-bambu`)* détaillées dans le
> [README du plugin Flipper](./flipper/bambu_scanner/README.md#-attribution-et-licences).

---

## 📜 Licence

Le code du dashboard est sous **MIT**.

⚠️ L'app Flipper Zero utilise une KDF (`bambu_crypto.c/h`) importée de
[ductai199x/BambuTagger](https://github.com/ductai199x/BambuTagger) sous
licence *"educational and personal use"*. Voir le
[README du plugin](./flipper/bambu_scanner/README.md#-attribution-et-licences).

---

<div align="center">

*Fait avec ❤️ et beaucoup de filament PLA par **Erti** (avec l'aide de **coom** sur le Flipper)*

</div>
