# Bambu Scanner — Android application

> [🇫🇷 Français](README.md) · 🇬🇧 English

Companion app for **Bambu Dashboard** (Home Assistant add-on).
Scan Bambu Lab spool NFC tags with your phone and register them directly in the dashboard.

> **© E-Odyssey 2026**

---

## Features

- NFC reading of Bambu Lab spools (MIFARE Classic 1K, UID-derived keys)
- Automatic identification: filament type, color, original weight
- One-tap send to Bambu Dashboard
- Authentication via configurable API key
- Works over local network (Wi-Fi), no cloud
- **Bilingual UI FR / EN** — follows the Android system locale by default, with an **Auto / Français / English** selector in the configuration card to force the language

---

## Compatibility

| Item | Required |
|------|----------|
| **Android** | 7.0 or higher (API 24+) |
| **NFC chip** | NXP (MIFARE Classic support) |
| **Bambu Dashboard** | 1.0.14 or higher (API key + exposed port support) |

### Compatible phones (non-exhaustive list)

| Brand | Tested / compatible models |
|-------|----------------------------|
| **Samsung** | Galaxy S (S7 and later), Galaxy A (A5x, A7x), Galaxy Note |
| **Google Pixel** | Pixel 6 / 7 / 8 / 9 (Tensor chip, NXP NFC) |
| **OnePlus** | Most recent models |

> **⚠️ Not compatible**: phones with a Broadcom NFC chip (some Huawei, older LG) do not support MIFARE Classic and cannot read Bambu Lab tags.

---

## Installation

1. Download the APK from the [`dist/bambu_scanner.apk`](dist/bambu_scanner.apk) folder
2. On your Android phone, allow installation from unknown sources (Settings → Security → Unknown sources)
3. Transfer the APK to the phone (USB cable, network share, email…)
4. Open the APK and install the application

---

## Dashboard configuration

Before using the app, the dashboard must be configured to accept external scans.

### 1. Expose the add-on port

Home Assistant's ingress does not support external POST requests. The add-on exposes port **8000** directly. In the add-on configuration (the **Configuration** tab in Home Assistant), make sure the port is mapped:

```
Network port: 8000/tcp → 8000
```

After the change, **restart the add-on**.

### 2. Configure an API key (optional but recommended)

In the Home Assistant add-on configuration, fill in the **nfc_api_key** field with a secret key of your choice (e.g., a long passphrase). The same key must be entered in the Android app.

If the field is left empty, the `/api/nfc/push` endpoint accepts requests without authentication.

### 3. Find the dashboard URL

The URL to enter in the app is the local IP address of your Home Assistant instance followed by port 8000:

```
http://<HOME_ASSISTANT_IP>:8000
```

Examples:
- `http://192.168.1.42:8000`
- `http://10.0.2.30:8000`
- `http://homeassistant.local:8000`

> **💡 Tip**: you can find your HA's IP in Settings → System → Network, or in your router's interface.

---

## Usage

### First launch

1. Open **Bambu Scanner** on your phone
2. Enter the **dashboard URL** (e.g. `http://192.168.1.42:8000`)
3. Enter the **API key** if you configured one
4. Tap the 💾 icon to save — these settings are persisted

### Scanning a spool

1. Make sure NFC is enabled on your phone
2. Hold the Bambu Lab spool's **RFID tag** against the back of the phone (NFC zone, usually top-center)
3. Keep contact for 1–2 seconds — the app shows **"Reading…"**
4. The spool information is displayed:
   - **Type**: e.g. `PLA Basic`, `PETG HF`, `ABS`
   - **Color**: name and visual preview
   - **Weight**: original weight in grams
   - **UID**: unique tag identifier

### Sending to the dashboard

1. Verify the displayed information
2. Tap **Send to Dashboard**
3. On success, the message **"Sent to dashboard!"** appears
4. On the dashboard (in your browser), the **"Scanned spool — Register"** modal opens automatically with all fields pre-filled
5. Verify the details and click **Register** in the dashboard

> **💡** The dashboard polls the backend every 3 seconds. The modal appears without any action on your part in the browser — you just need the dashboard page to be open.

### Scanning another spool

After sending, tap **New Scan** and approach the next spool.

---

## Troubleshooting

| Problem | Likely cause | Solution |
|---------|--------------|----------|
| **"NFC not available"** | Phone without NFC | Use a Flipper Zero instead |
| **"NFC disabled"** | NFC turned off in settings | Enable NFC (Settings → Connections → NFC) |
| **"Tag not recognized"** | Non-Bambu Lab tag, or Broadcom NFC chip | Check phone compatibility |
| **"MIFARE Classic not supported"** | Incompatible NFC chip | Phone does not support MIFARE Classic |
| **"Authentication error"** | NFC keys rejected | Incompatible tag (non-Bambu Lab or very old spool) |
| **"Send error: HTTP 403"** | Wrong API key | Check that the key in the app matches the one configured in the add-on |
| **"Send error: HTTP 405"** | Wrong URL (HA ingress) | Use the direct IP with port 8000, not the ingress URL |
| **"Send error: connection refused"** | Phone not on the same network | Connect to the same Wi-Fi as Home Assistant |
| **Modal not shown in the dashboard** | Dashboard page not open | Open the dashboard in a browser before sending |

---

## Credits

- **Erti** — main author of the Bambu Dashboard project
- **coom** — development of the Android application and the Flipper Zero plugin
- KDF based on [ductai199x/BambuTagger](https://github.com/ductai199x/BambuTagger) (Tai Nguyen) — personal use only
- Filament table: [queengooborg/Bambu-Lab-RFID-Library](https://github.com/queengooborg/Bambu-Lab-RFID-Library)
