# 🎨 Bambu Dashboard

![Supports amd64][amd64-shield]
![Supports aarch64][aarch64-shield]
![Supports armv7][armv7-shield]

> **Dashboard AMS Bambu Lab tout-en-un** — suivi bobines, KPIs de
> consommation, scan NFC Flipper Zero et Android.
> Intégré directement dans Home Assistant via l'ingress. 🏠

---

## ✨ Fonctionnalités

- 📡 **Connexion MQTT TLS directe** à l'imprimante — *pas de Bambu Cloud,
  pas de Bambu Studio, zéro compte*
- 🖨️ **Vue AMS temps réel** — état des 4 slots, type, couleur, poids
  restant
- 📦 **Inventaire bobines persistant** — réconciliation automatique via
  `tray_uuid`, cycle `active → idle → empty → archived`
- 📊 **KPIs de consommation** — total, sessions d'impression, top
  matériaux, 7 / 30 derniers jours
- 🏷️ **Scan NFC Bambu** — reconnaissance des bobines **2024+** via un
  Flipper Zero (`.fap` pré-compilé fourni) ou l'**app Android compagnon**
  ([`Bambu Scanner`](../android/bambu_scanner/README.md))
- 🎨 **Pré-remplissage intelligent** — le nom de couleur est deviné
  depuis le hex (palette FR) et suffixé au nom *(ex : « PLA Basic
  Noir »)*

---

## 🚀 Installation rapide

> **1.** Ajoute ce dépôt dans **Paramètres → Modules complémentaires →
> Boutique → Dépôts** :
>
> ```
> https://code.e-odyssey.net/coom/bambuboard
> ```
>
> **2.** Installe **Bambu Dashboard** depuis la section qui apparaît ✨
>
> **3.** Remplis les **3 champs obligatoires** (`printer_ip`,
> `printer_serial`, `printer_access_code`) — voir **Documentation** pour
> les récupérer
>
> **4.** Démarre l'add-on et ouvre l'interface Web 🎉

---

## ⚙️ Configuration minimale

```yaml
printer_ip: "192.168.1.42"
printer_serial: "01P00A1B2C3D4E5F"
printer_access_code: "12345678"
```

> 📖 L'onglet **Documentation** détaille toutes les options, la
> procédure pour récupérer les identifiants de l'imprimante, et le
> troubleshooting complet.

---

## 👥 Crédits

Projet créé par **Erti** *(add-on HA, backend, frontend)*. **coom** est
contributeur majeur *(plugin Flipper Zero `bambu_scanner`, application
Android `Bambu Scanner`)*.

---

[amd64-shield]: https://img.shields.io/badge/amd64-yes-green.svg
[aarch64-shield]: https://img.shields.io/badge/aarch64-yes-green.svg
[armv7-shield]: https://img.shields.io/badge/armv7-yes-green.svg
