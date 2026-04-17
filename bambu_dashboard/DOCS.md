# 📖 Bambu Dashboard — Documentation

> 🇫🇷 Français · [🇬🇧 English](https://github.com/coom/BambuBoard/blob/main/bambu_dashboard/DOCS.en.md)

---

## 📋 Prérequis

| | |
|---|---|
| 🏠 **Home Assistant** | **OS** ou **Supervised** — *le mode Container n'a pas le Supervisor donc ne supporte pas les add-ons* |
| 🖨️ **Imprimante** | Bambu Lab avec AMS, accessible en réseau local depuis HA |
| 📡 **Mode réseau** | **LAN activé** sur l'imprimante *(obligatoire — le broker MQTT local est désactivé sinon)* |

---

## 🔑 Récupérer les identifiants de l'imprimante

Sur l'écran tactile de l'imprimante :

| Champ | 📍 Chemin |
|---|---|
| `printer_ip` | Réglages → **Wi-Fi** → *(adresse IP affichée)* |
| `printer_serial` | Réglages → **À propos** → **S/N** *(format `01P00A1B2C3D4E5F`)* |
| `printer_access_code` | Réglages → **Réseau** → **Code d'accès** *(8 chiffres)* |

> ⚠️ **Important** : active **Mode LAN uniquement** (ou LAN + Cloud)
> dans Réglages → Réseau. Sans ça, le broker MQTT local est désactivé
> et l'add-on **ne peut pas se connecter**.

---

## ⚙️ Options de configuration

```yaml
printer_ip: "192.168.1.42"          # IP locale de l'imprimante
printer_serial: "01P00A1B2C3D4E5F"  # S/N (16 caractères)
printer_access_code: "12345678"     # Code d'accès LAN (8 chiffres)
ha_webhook_url: ""                   # (optionnel) webhook pour notifs
ha_webhook_token: ""                 # (optionnel) Bearer token si requis
low_stock_threshold: 20              # Seuil en % pour notif stock bas
```

### 🔔 Notifications Home Assistant

Pour recevoir une notification dans HA quand une bobine passe sous
`low_stock_threshold` :

**1.** Crée une automation dans HA qui écoute un webhook :

```yaml
trigger:
  - platform: webhook
    webhook_id: bambu_low_stock
    allowed_methods: [POST]
    local_only: true
action:
  - service: notify.mobile_app_xxx
    data:
      title: "{{ trigger.json.title }}"
      message: "{{ trigger.json.message }}"
```

**2.** Dans les options de l'add-on, colle l'URL du webhook :

```yaml
ha_webhook_url: "http://supervisor/core/api/webhook/bambu_low_stock"
```

> 💡 La notif est envoyée **une seule fois par franchissement** du
> seuil — pas de spam.

---

## 🎯 Utilisation

### 🏁 Premier démarrage

**1.** Après avoir démarré l'add-on, ouvre l'interface Web via **Ouvrir
l'interface Web** ou le panneau latéral **Bambu** 🎨

**2.** L'onglet **AMS** affiche l'état courant des 4 slots dès le
premier message MQTT reçu *(quelques secondes)*

**3.** L'onglet **Inventaire** est vide — il se remplit **automatiquement**
au fur et à mesure que les bobines sont détectées dans l'AMS

### 🔄 Cycle de vie d'une bobine

| Statut | Signification | Transition |
|:---:|---|---|
| 🟢 `active` | Bobine physiquement dans l'AMS, associée à un `tray_uuid` | *Automatique (détection AMS)* |
| 🔵 `idle` | Bobine connue mais pas actuellement chargée | *Automatique (retrait AMS)* |
| 🔴 `empty` | `remain ≤ 0%` | *Automatique* |
| ⚫ `archived` | Bobine retirée du catalogue | **Manuel** *(bouton « Archiver »)* |

> 🛒 Le bouton **Racheter** archive l'ancienne bobine et en crée une
> nouvelle copie à **100 %** / `idle`, utile quand tu rachètes le même
> filament.

### ✨ Enregistrer une bobine inconnue depuis l'AMS

Quand une bobine chargée dans l'AMS n'existe pas encore dans
l'inventaire, son slot affiche un bouton 🏷️ **« Bobine inconnue —
Enregistrer »**. Le formulaire s'ouvre **pré-rempli** avec *toutes* les
métadonnées exposées par l'imprimante :

| Champ | Source | Exemple |
|---|---|---|
| **Nom** | `sub_brands` + *couleur devinée* | `PLA Basic Noir` |
| **Marque** | défaut | `Bambu Lab` |
| **Code filament** | `tray_info_idx` | `GFA00` |
| **Couleur *(hex)*** | `color` *(exposé par l'AMS)* | `#000000` |
| **Couleur *(nom)*** | *deviné* depuis le hex | `Noir` |
| **Poids initial** | `tray_weight` | `1000 g` |
| **Remain initial** | valeur courante AMS | `98 %` |
| **tray_uuid / tag_uid** | auto | *(réconciliation)* |

> 🎨 Le nom de couleur est deviné via une palette de **23 couleurs
> françaises** (recherche par distance euclidienne RGB) pour distinguer
> visuellement les bobines d'un même type dans l'inventaire.

Ajuste ce que tu veux et valide — la bobine est créée en 🟢 `active`
*(puisqu'elle est présente dans l'AMS)*.

### 🏷️ Scan NFC via Flipper Zero

Si tu as un Flipper Zero avec l'app `bambu_scanner` installée :

**1.** Onglet **Inventaire** → bouton 🛰️ **Scan Flipper**

**2.** **Connecter** → sélectionne le port série du Flipper

**3.** Lance l'app `bambu_scanner` sur le Flipper, approche une bobine

**4.** Confirme avec **OK** sur le Flipper

**5.** Le formulaire de création de bobine s'ouvre **pré-rempli** ✨

> 🌐 **Navigateur requis** : **Chrome** ou **Edge** — *Web Serial n'est
> pas supporté par Firefox/Safari*.

> 📖 Voir [`flipper/bambu_scanner/README.md`](../flipper/bambu_scanner/README.md)
> pour l'installation du plugin Flipper (un `.fap` pré-compilé est
> fourni, pas besoin de builder).

---

## 🛠️ Overlay frontend *(itération rapide)*

L'add-on supporte un **overlay du frontend** via
`/share/bambu_dashboard/frontend/` pour modifier `index.html` **sans
rebuild de l'image Docker** :

**1.** Copie `frontend/index.html` de l'image dans
`/share/bambu_dashboard/frontend/index.html`

**2.** Modifie-le librement

**3.** **Redémarre l'add-on** — les modifs sont appliquées instantanément 🔄

> 🗑️ Supprime le fichier pour revenir à la version embarquée dans
> l'image Docker.

---

## 💾 Persistance des données

- 📁 La base **SQLite** est dans `/data/bambu.db` *(persistée par HA
  entre redémarrages de l'add-on et mises à jour)*
- ⚡ Mode **WAL** activé *(performances + lectures concurrentes)*
- 📉 Les logs de consommation sont **append-only**, filtrés par un
  seuil de **2 %** *(pour éviter le bruit MQTT)*

---

## 🩺 Troubleshooting

### ❌ L'add-on démarre mais `connected: false` dans l'AMS

- ✅ Vérifie le **Mode LAN** sur l'imprimante
- ✅ Vérifie que `printer_ip` est **atteignable** depuis HA *(ping)*
- ✅ Vérifie le `printer_access_code` *(attention aux caractères spéciaux)*
- 📋 Regarde les logs de l'add-on : erreurs **TLS** ou **auth** = code
  ou S/N faux

### ❌ *« Failed to open serial port »* au scan Flipper

> 🔒 **Cause la plus fréquente** : un autre programme tient le port COM.

- 🛑 **Ferme qFlipper, PuTTY, Arduino IDE, tout moniteur série** qui
  pourrait tenir le port COM ouvert *(Windows → ports COM exclusifs)*
- 🔌 **Débranche et rebranche** le Flipper
- 🔄 **Relance Chrome**

### ❌ Le formulaire ne s'ouvre pas après scan Flipper

- ✅ Assure-toi que l'app sur le Flipper est bien **`bambu_scanner`**
  *(pas l'ancien `bambu_nfc`)*
- 🔍 Ouvre **Chrome DevTools** *(F12)* et regarde l'onglet Console pour
  les erreurs `BAMBU_NFC parse error`
- 🔒 Vérifie que tu es bien en **HTTPS** sur HA *(l'ingress HA est
  HTTPS par défaut — Web Serial exige une origine sécurisée)*

### ❌ Les notifications stock bas ne partent pas

- ✅ Vérifie que `ha_webhook_url` est rempli
- 🧪 **Teste le webhook manuellement** avec `curl`
- ℹ️ Les notifs sont émises **une seule fois par franchissement** du
  seuil *(anti-spam MQTT)* — change de bobine pour retester

---

## 🔗 Liens utiles

- 📦 **Dépôt** : https://github.com/coom/BambuBoard
- 🛰️ **Plugin Flipper** : [`flipper/bambu_scanner/`](../flipper/bambu_scanner/)
- 📜 **Changelog** : [`CHANGELOG.md`](./CHANGELOG.md)

---

## 👥 Crédits

Développé par **Erti**, avec l'aide de **coom** sur le module Flipper
Zero *(app `bambu_scanner`)*. Voir les contributions upstream dans le
[README du plugin Flipper](../flipper/bambu_scanner/README.md#-attribution-et-licences).
