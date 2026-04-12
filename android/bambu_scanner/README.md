# Bambu Scanner — Android

Application Android compagnon pour **Bambu Dashboard**. Lit les tags NFC MIFARE Classic des bobines Bambu Lab et envoie les données au dashboard via `POST /api/nfc/push`.

## Prérequis

- Android 7.0+ (API 24)
- Téléphone avec **chip NFC NXP** (MIFARE Classic). La plupart des Samsung, Pixel (Tensor), OnePlus sont compatibles. Les téléphones avec chip Broadcom NFC ne supportent pas MIFARE Classic.
- Android Studio Hedgehog (2023.1+) pour la compilation

## Compilation

1. Ouvrir `android/bambu_scanner/` dans Android Studio
2. Sync Gradle
3. Build → Run sur un téléphone physique (pas d'émulateur — NFC requis)

## Utilisation

1. Lancer l'app
2. Entrer l'URL du dashboard Home Assistant (ex: `http://192.168.1.42:8123/api/hassio_ingress/xxxxx`)
3. Approcher une bobine Bambu Lab du téléphone
4. Vérifier les infos affichées (type, couleur, poids)
5. Appuyer sur **Envoyer au Dashboard**

Le dashboard recevra la bobine comme un scan Flipper Zero — le modal « Bobine inconnue — Enregistrer » s'ouvrira automatiquement.

## Architecture

| Fichier | Rôle |
|---------|------|
| `BambuCrypto.kt` | HKDF key derivation (port de `bambu_crypto.c`) |
| `BambuParser.kt` | Parsing des blocs MIFARE (port de `bambu_parser.h`) |
| `BambuFilaments.kt` | Table de lookup variant ID → code + couleur |
| `BambuNfcReader.kt` | Lecture MIFARE Classic avec clés dérivées |
| `DashboardApi.kt` | POST HTTP vers `/api/nfc/push` |
| `MainActivity.kt` | UI + NFC foreground dispatch |

## Crédits

- **Erti** — développement de l'app Android et du dashboard
- **coom** — développement du module Flipper Zero `bambu_scanner`
- KDF importée de [ductai199x/BambuTagger](https://github.com/ductai199x/BambuTagger) (Tai Nguyen) — usage personnel uniquement
- Table de filaments : [queengooborg/Bambu-Lab-RFID-Library](https://github.com/queengooborg/Bambu-Lab-RFID-Library)
