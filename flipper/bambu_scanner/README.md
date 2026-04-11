# Bambu Scanner — Plugin Flipper Zero

App Flipper Zero qui scanne les tags NFC MIFARE Classic 1K des bobines Bambu Lab
(avec clés dérivées par UID — compatibles bobines 2024+), parse les métadonnées
du filament, et les émet sur le CDC série USB sous la forme d'une ligne JSON
préfixée `BAMBU_NFC:`, consommable par le dashboard Bambu via l'API Web Serial
dans Chrome/Edge.

## Prérequis

| Composant | Détail |
|-----------|--------|
| **Flipper Zero** | Firmware officiel |
| **ufbt** | `pip install --user ufbt` |
| **Câble USB-C data** | Pas un câble charge-seule |
| **Chrome ou Edge** | Web Serial API non supportée dans Firefox/Safari |

## Build

```bash
cd flipper/bambu_scanner
python -m ufbt update   # au premier build, télécharge le SDK officiel
python -m ufbt          # produit dist/bambu_scanner.fap
```

> **Note Windows :** sur cette machine `ufbt` n'est pas dans le PATH après
> `pip install --user`. Utiliser `python -m ufbt` à la place.

## Installation sur le Flipper

Option 1 — via ufbt (compile + flash + launch en un seul coup) :

```bash
python -m ufbt launch
```

Option 2 — manuel via qFlipper :
1. qFlipper → File manager
2. Naviguer vers `SD Card/apps/NFC/`
3. Glisser-déposer `dist/bambu_scanner.fap`

## Utilisation

1. Sur le Flipper : Menu → Apps → NFC → **Bambu Scanner**
2. Approcher une bobine Bambu Lab du dos du Flipper
3. L'écran affiche le type, la couleur, le poids et l'UID du tag
4. Appuyer sur **[OK]** pour émettre les données sur le CDC série USB
5. **[Retour]** annule ou quitte

## Intégration dashboard

Le dashboard `bambu_dashboard` a un bouton "Scan Flipper" dans l'onglet
Inventaire. Après clic, Chrome demande l'accès au port série, on
sélectionne celui du Flipper, et à chaque scan le formulaire de création
de bobine s'ouvre pré-rempli.

## Format de la ligne série émise

```
\nBAMBU_NFC:{"tag_uid":"AABBCCDD","tray_type":"PLA","sub_brands":"PLA Basic","color_hex":"FF5500","color_name":"Orange","filament_code":"10101","initial_weight":1000,"brand":"Bambu Lab"}\n
```

Les deux `\n` (début ET fin) sont critiques pour le parser frontend.

## Attribution

La dérivation de clés (`bambu_crypto.c/h`) est importée telle quelle depuis
[ductai199x/BambuTagger](https://github.com/ductai199x/BambuTagger) — licence
"educational and personal use". Ne pas redistribuer commercialement.

Les headers de parsing (`bambu_parser.h`, `bambu_filaments.h`) et la logique
d'app (UI, thread, sortie série) viennent de l'ancien plugin `bambu_nfc` du
même projet (dérivé lui-même de `uzyn/flipper-bambu` à l'origine).

## Piège connu : port série occupé

Si tu utilises un moniteur série externe (PuTTY, screen, etc.) pour débugger
la sortie du plugin, **ferme-le** avant d'ouvrir le dashboard dans Chrome.
Les ports COM Windows sont exclusifs — Chrome ne pourra pas ouvrir un port
déjà utilisé par PuTTY, et inversement.
