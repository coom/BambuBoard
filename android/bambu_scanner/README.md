# Bambu Scanner — Application Android

Application compagnon pour **Bambu Dashboard** (add-on Home Assistant).
Scanne les tags NFC des bobines Bambu Lab avec votre téléphone et les enregistre directement dans le dashboard.

> **© E-Odyssey 2026**

---

## Fonctionnalités

- Lecture NFC des bobines Bambu Lab (MIFARE Classic 1K, clés dérivées par UID)
- Identification automatique : type de filament, couleur, poids d'origine
- Envoi en un tap vers Bambu Dashboard
- Authentification par clé API configurable
- Fonctionne en réseau local (Wi-Fi), sans cloud

---

## Compatibilité

| Élément | Requis |
|---------|--------|
| **Android** | 7.0 ou supérieur (API 24+) |
| **Chip NFC** | NXP (support MIFARE Classic) |
| **Bambu Dashboard** | 1.0.14 ou supérieur (support clé API + port exposé) |

### Téléphones compatibles (liste non exhaustive)

| Marque | Modèles testés / compatibles |
|--------|-------------------------------|
| **Samsung** | Galaxy S (S7 et +), Galaxy A (A5x, A7x), Galaxy Note |
| **Google Pixel** | Pixel 6 / 7 / 8 / 9 (chip Tensor, NXP NFC) |
| **OnePlus** | La plupart des modèles récents |

> **⚠️ Non compatible** : les téléphones équipés d'un chip NFC Broadcom (certains Huawei, anciens LG) ne supportent pas MIFARE Classic et ne pourront pas lire les tags Bambu Lab.

---

## Installation

1. Téléchargez l'APK depuis le dossier [`dist/bambu_scanner.apk`](dist/bambu_scanner.apk)
2. Sur votre téléphone Android, autorisez l'installation depuis des sources inconnues (Paramètres → Sécurité → Sources inconnues)
3. Transférez l'APK sur le téléphone (câble USB, partage réseau, e-mail…)
4. Ouvrez l'APK et installez l'application

---

## Configuration du dashboard

Avant d'utiliser l'app, le dashboard doit être configuré pour accepter les scans externes.

### 1. Exposer le port de l'add-on

L'ingress Home Assistant ne supporte pas les requêtes POST externes. L'add-on expose le port **8000** directement. Vérifiez dans la configuration de l'add-on (onglet **Configuration** dans Home Assistant) que le port est bien mappé :

```
Port réseau : 8000/tcp → 8000
```

Après modification, **redémarrez l'add-on**.

### 2. Configurer une clé API (optionnel mais recommandé)

Dans la configuration de l'add-on Home Assistant, renseignez le champ **nfc_api_key** avec une clé secrète de votre choix (ex : un mot de passe long). Cette même clé devra être saisie dans l'app Android.

Si le champ est laissé vide, l'endpoint `/api/nfc/push` accepte les requêtes sans authentification.

### 3. Trouver l'URL du dashboard

L'URL à saisir dans l'app est l'adresse IP locale de votre instance Home Assistant suivie du port 8000 :

```
http://<IP_HOME_ASSISTANT>:8000
```

Exemples :
- `http://192.168.1.42:8000`
- `http://10.0.2.30:8000`
- `http://homeassistant.local:8000`

> **💡 Astuce** : vous pouvez trouver l'IP de votre HA dans Paramètres → Système → Réseau, ou dans l'interface de votre routeur.

---

## Utilisation

### Premier lancement

1. Ouvrez **Bambu Scanner** sur votre téléphone
2. Saisissez l'**URL du dashboard** (ex : `http://192.168.1.42:8000`)
3. Saisissez la **clé API** si vous en avez configuré une
4. Appuyez sur l'icône 💾 pour sauvegarder — ces paramètres sont mémorisés

### Scanner une bobine

1. Vérifiez que le NFC est activé sur votre téléphone
2. Approchez le **tag RFID** de la bobine Bambu Lab contre le dos du téléphone (zone NFC, généralement en haut au centre)
3. Maintenez le contact 1 à 2 secondes — l'app affiche **« Lecture en cours… »**
4. Les informations de la bobine s'affichent :
   - **Type** : ex. `PLA Basic`, `PETG HF`, `ABS`
   - **Couleur** : nom et aperçu visuel
   - **Poids** : poids d'origine en grammes
   - **UID** : identifiant unique du tag

### Envoyer au dashboard

1. Vérifiez les informations affichées
2. Appuyez sur **Envoyer au Dashboard**
3. Si l'envoi réussit, le message **« Envoyé au dashboard ! »** apparaît
4. Sur le dashboard (dans votre navigateur), le modal **« Bobine scannée — Enregistrer »** s'ouvre automatiquement avec tous les champs pré-remplis
5. Vérifiez les infos et cliquez sur **Enregistrer** dans le dashboard

> **💡** Le dashboard interroge automatiquement le backend toutes les 3 secondes. Le modal apparaît sans action de votre part côté navigateur — il suffit que la page du dashboard soit ouverte.

### Scanner une autre bobine

Après l'envoi, appuyez sur **Nouveau Scan** et approchez la bobine suivante.

---

## Dépannage

| Problème | Cause probable | Solution |
|----------|---------------|----------|
| **« NFC non disponible »** | Téléphone sans NFC | Utilisez un Flipper Zero à la place |
| **« NFC désactivé »** | NFC coupé dans les paramètres | Activez le NFC (Paramètres → Connexions → NFC) |
| **« Tag non reconnu »** | Tag non Bambu Lab, ou chip NFC Broadcom | Vérifiez la compatibilité du téléphone |
| **« MIFARE Classic non supporté »** | Chip NFC incompatible | Le téléphone ne supporte pas MIFARE Classic |
| **« Erreur d'authentification »** | Clés NFC rejetées | Tag non compatible (bobine non Bambu Lab ou très ancienne) |
| **« Erreur d'envoi : HTTP 403 »** | Clé API incorrecte | Vérifiez que la clé dans l'app correspond à celle configurée dans l'add-on |
| **« Erreur d'envoi : HTTP 405 »** | URL incorrecte (ingress HA) | Utilisez l'IP directe avec le port 8000, pas l'URL ingress |
| **« Erreur d'envoi : connexion refusée »** | Téléphone pas sur le même réseau | Connectez-vous au même Wi-Fi que Home Assistant |
| **Modal non affiché dans le dashboard** | Page du dashboard non ouverte | Ouvrez le dashboard dans un navigateur avant d'envoyer |

---

## Crédits

- **Erti** — développement de l'application Android et du dashboard
- **coom** — développement du module Flipper Zero `bambu_scanner`
- KDF basée sur [ductai199x/BambuTagger](https://github.com/ductai199x/BambuTagger) (Tai Nguyen) — usage personnel uniquement
- Table de filaments : [queengooborg/Bambu-Lab-RFID-Library](https://github.com/queengooborg/Bambu-Lab-RFID-Library)
