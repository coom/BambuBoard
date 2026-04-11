<div align="center">

# 🛰️ Bambu Scanner — Plugin Flipper Zero

### *Scanne les tags NFC des bobines Bambu Lab et envoie les métadonnées au dashboard*

![Firmware](https://img.shields.io/badge/Firmware-Official%20SDK%201.4.3-orange?style=flat-square)
![API](https://img.shields.io/badge/API-87.1-orange?style=flat-square)
![NFC](https://img.shields.io/badge/NFC-MIFARE%20Classic%201K-blue?style=flat-square)
![Bobines](https://img.shields.io/badge/Bobines-2024%2B-success?style=flat-square)

</div>

---

> 📡 Application Flipper Zero qui scanne les tags NFC **MIFARE Classic
> 1K** des bobines Bambu Lab *(avec clés dérivées par UID — compatibles
> bobines **2024+**)*, parse les métadonnées du filament, et les émet
> sur **l'USB CDC série** sous la forme d'une ligne JSON préfixée
> `BAMBU_NFC:`, consommée par l'add-on Bambu Dashboard via la
> **Web Serial API** dans Chrome/Edge.

---

## 📑 Sommaire

- [📋 Prérequis matériels et logiciels](#-prérequis-matériels-et-logiciels)
- [🎯 Installation simple *(qFlipper, binaire pré-compilé)*](#-installation--chemin-simple-qflipper-binaire-pré-compilé)
- [🔨 Installation avancée *(ufbt, build local)*](#-installation--chemin-ufbt-build-local--flash)
- [🎮 Utilisation sur le Flipper](#-utilisation-sur-le-flipper)
- [🔗 Intégration avec le dashboard](#-intégration-avec-le-dashboard)
- [📄 Format de la ligne série émise](#-format-de-la-ligne-série-émise)
- [🩺 Troubleshooting](#-troubleshooting)
- [📜 Attribution et licences](#-attribution-et-licences)

---

## 📋 Prérequis matériels et logiciels

| Composant | Détail |
|---|---|
| 🐬 **Flipper Zero** | Firmware **officiel** *(testé API 87.1 / SDK 1.4.3)* |
| 🔌 **Câble USB-C data** | ⚠️ **Pas un câble charge-seule** — essentiel ! |
| 🐍 **Python 3** | *Uniquement si tu veux builder l'app toi-même (chemin ufbt)* |
| 📦 **ufbt** | `pip install --user ufbt` — *chemin ufbt uniquement* |
| 🌐 **Chrome ou Edge** | Web Serial API **non supportée** dans Firefox/Safari |
| 🔒 **Origine HTTPS** | L'ingress Home Assistant est déjà HTTPS → ✅ OK |

> ℹ️ Le **firmware officiel** suffit — pas besoin de Unleashed, Momentum ou
> RogueMaster.

---

## 🎯 Installation — chemin simple *(qFlipper, binaire pré-compilé)*

> ✨ **La méthode recommandée pour 99 % des utilisateurs.**
>
> Un `.fap` pré-compilé est directement **versionné dans le repo** à
> [`flipper/bambu_scanner/dist/bambu_scanner.fap`][fap-direct].
>
> 🚫 **Pas besoin de Python**, 🚫 **pas besoin d'ufbt**,
> 🚫 **pas de toolchain à installer** — *télécharge, drag-and-drop,
> c'est installé*.

[fap-direct]: https://code.e-odyssey.net/coom/bambuboard/raw/branch/main/flipper/bambu_scanner/dist/bambu_scanner.fap

**1.** 📥 Télécharge [`bambu_scanner.fap`][fap-direct] *(clic droit →
Enregistrer sous)*, ou clone le repo et prends-le dans
`flipper/bambu_scanner/dist/`

**2.** 🖥️ Ouvre **qFlipper** et connecte ton Flipper

**3.** 📁 Onglet **File manager**

**4.** 🗂️ Navigue vers **SD Card → apps → NFC**

**5.** 🖱️ Glisse-dépose `bambu_scanner.fap` dans ce dossier

**6.** 🔌 Débranche-rebranche ton Flipper

✅ L'app apparaît dans **Apps → NFC → Bambu Scanner** 🎉

> ⚠️ Le `.fap` versionné est compilé avec le **SDK officiel 1.4.3 / API
> 87.1**. Si ton Flipper tourne sur un **firmware custom** *(Unleashed,
> Momentum, RogueMaster)*, passe par le chemin ufbt ci-dessous — *les
> FAP ne sont pas binaire-compatibles entre firmwares*.

---

## 🔨 Installation — chemin ufbt *(build local + flash)*

> 🛠️ **À utiliser si** tu veux modifier le plugin, recompiler avec un
> firmware custom, ou simplement flasher directement depuis la ligne
> de commande.

```bash
cd flipper/bambu_scanner
python -m ufbt update   # première fois seulement : télécharge le SDK officiel
python -m ufbt launch   # build + flash + launch sur le Flipper 🚀
```

> 💡 **Note Windows** : après `pip install --user ufbt`, la commande
> `ufbt` n'est *généralement pas* dans le PATH. **Utilise toujours
> `python -m ufbt`** à la place. Pareil pour `ufbt update`,
> `ufbt launch`, etc.

✅ L'app apparaît dans **Apps → NFC → Bambu Scanner** sur le Flipper.

### 📦 Build sans flash

Si tu préfères juste recompiler le `.fap` pour l'installer manuellement
*(ex : le committer dans le repo après une modif)* :

```bash
cd flipper/bambu_scanner
python -m ufbt          # produit dist/bambu_scanner.fap
```

Le fichier `dist/bambu_scanner.fap` peut ensuite être copié via qFlipper
*(voir la section précédente)*.

---

## 🎮 Utilisation sur le Flipper

**1.** 📱 Ouvre **Apps → NFC → Bambu Scanner** sur le Flipper

**2.** 👀 L'écran affiche *« Approchez une bobine Bambu Lab du Flipper »*

**3.** 🏷️ Approche le **dos du Flipper** d'un tag NFC de bobine Bambu
*(il y en a un sur chaque bobine officielle, à l'intérieur du carton
central)*

**4.** ✨ Dès que le scan réussit, l'écran affiche :

- 🧵 Le **type détaillé** *(ex : `PLA Marble`)*
- 🎨 La **couleur** *(ex : `White Marble`)*
- ⚖️ Le **poids initial** *(ex : `1000 g`)*

**5.** ▶️ Appuie sur **[OK]** pour émettre les données vers le PC via
USB CDC

**6.** 📤 L'écran affiche *« Envoyé ! »* — tu peux soit :

- **[OK]** pour scanner une nouvelle bobine 🔄
- **[Retour]** pour quitter l'app 🚪

### ⚠️ En cas de tag non reconnu

Si l'écran affiche *« Tag non reconnu »* :

- ✅ Vérifie que c'est bien une bobine **Bambu Lab officielle** *(les
  génériques n'ont pas de tag NFC)*
- 🎯 **Repositionne** la bobine *(le tag est proche du centre, pas du
  bord)*
- ⏳ Certaines bobines **anciennes** *(avant 2024)* peuvent utiliser des
  clés différentes et ne pas être lisibles
- 🔁 Appuie sur **[OK]** pour réessayer

---

## 🔗 Intégration avec le dashboard

L'add-on Bambu Dashboard a un bouton 🛰️ **« Scan Flipper »** dans
l'onglet **Inventaire** :

**1.** 🖱️ Clique **Scan Flipper** → un modal s'ouvre avec **Connecter**

**2.** 🔌 Clique **Connecter** — Chrome affiche son sélecteur de port
série

**3.** 🎯 Sélectionne le port du Flipper *(généralement étiqueté
« USB Serial Device » sur Windows ou `/dev/ttyACM0` sur Linux)*

**4.** ✅ Le modal passe à *« Flipper connecté — scanne une bobine »*

**5.** 🏷️ Sur le Flipper, fais ton scan et confirme avec **[OK]**

**6.** ✨ Le formulaire de création de bobine s'ouvre **pré-rempli**
avec toutes les métadonnées du tag *(nom, couleur, poids, UID)*

**7.** 💾 Ajuste si nécessaire et valide — la bobine est ajoutée à
l'inventaire 🎉

> 🔁 Si le `tag_uid` existe **déjà** dans l'inventaire, un toast t'en
> informe et ouvre directement la bobine existante — *pas de doublon*.

---

## 📄 Format de la ligne série émise

```
\nBAMBU_NFC:{"tag_uid":"D54AAD02","tray_type":"PLA","sub_brands":"PLA Marble","color_hex":"F7F3F0","color_name":"White Marble","filament_code":"13103","initial_weight":1000,"brand":"Bambu Lab"}\n
```

> ⚠️ Les deux `\n` *(début **et** fin)* sont **critiques** pour le
> parser du frontend. Tous les champs sont émis en **ASCII pur** *(pas
> d'UTF-8)*.

### 🔬 Implémentation interne *(note technique)*

> Dans une FAP sur firmware Flipper officiel, `printf()` n'est **pas**
> routé vers l'USB CDC par défaut.
>
> Le plugin installe explicitement un callback
> `furi_thread_set_stdout_callback` qui pipe stdout vers
> `furi_hal_cdc_send(0, ...)` en découpant les gros buffers en paquets
> de **64 octets** (`CDC_DATA_SZ`) avec **1 ms de délai** entre chunks
> *(sans quoi le buffer matériel USB est écrasé avant transmission)*.
>
> 📎 Voir `bambu_scanner.c` fonction `bambu_cdc_stdout`.

---

## 🩺 Troubleshooting

### ❌ Chrome : *« Failed to open serial port »*

> 🔒 **Cause la plus fréquente** : un autre programme tient le port
> COM. *Sur Windows, les ports COM sont exclusifs.*

- 🛑 Ferme **qFlipper**, **PuTTY**, **Arduino IDE**, **Serial Monitor
  VS Code**, ou tout autre moniteur série
- ☠️ Dans **Task Manager**, kill les process `qFlipper.exe`,
  `putty.exe`, `python.exe` éventuellement bloqués
- 🔌 Débranche et rebranche le Flipper
- 🔄 Réessaie dans Chrome

### ❌ Chrome : *« Web Serial is not supported »*

- 🌐 Utilise **Chrome ou Edge** *(Firefox et Safari n'ont pas Web
  Serial)*
- 🔒 Assure-toi d'être sur une **origine sécurisée** : l'ingress HA est
  **HTTPS** par défaut → ✅ OK, mais `http://localhost` fonctionne
  aussi en développement

### ❌ Le modal *« Flipper connecté »* ne passe pas au formulaire

- 🔍 Ouvre **DevTools Console** *(F12 → onglet Console)* et refais le
  scan
- 👀 Tu devrais voir soit le formulaire s'ouvrir, soit une erreur
  `BAMBU_NFC parse error` si le JSON est corrompu
- ⚠️ Si **aucun message** n'apparaît dans la console, l'app Flipper
  n'arrive pas à écrire sur le CDC — **reflash le plugin**
  *(`python -m ufbt launch`)* pour être sûr d'avoir la dernière version

### ❌ L'app Flipper ne se lance pas après installation

- ✅ Vérifie que tu as bien un Flipper Zero à jour
  *(**Settings → Firmware Info → Version**)*
- ℹ️ Si tu as le **firmware officiel**, l'app compilée avec le SDK
  1.4.3 / API 87.1 devrait tourner sans problème
- ⚠️ Sur des **firmwares custom** *(Unleashed/Momentum)*, il faut
  **rebuilder** avec leur SDK spécifique — *l'app n'est pas
  binaire-compatible entre firmwares*

---

## 📜 Attribution et licences

### 🔐 Dérivation de clés *(KDF)*

Les fichiers `bambu_crypto.c` / `bambu_crypto.h` *(dérivation
HMAC-SHA256 des clés MIFARE à partir de l'UID)* sont importés tels
quels depuis
[**ductai199x/BambuTagger**](https://github.com/ductai199x/BambuTagger).

> ⚠️ **Licence originale** : *« educational and personal use »* —
> **ne pas redistribuer commercialement**.

### 🧩 Parsing des bobines

Les headers `bambu_parser.h` et `bambu_filaments.h` *(lookup tables de
codes de filament et noms de couleurs Bambu)* viennent de l'ancien
plugin `bambu_nfc` de ce repo, lui-même dérivé de
[**uzyn/flipper-bambu**](https://github.com/uzyn/flipper-bambu) à
l'origine.

### ✍️ Logique d'app

Le code UI/thread/sortie série *(`bambu_scanner.c`)* est écrit
**spécifiquement pour ce projet**, mais la structure *(view_port,
message queue, thread NFC)* reprend le même pattern que l'ancien
`bambu_nfc`.

---

<div align="center">

*Happy scanning* 🐬✨

</div>
