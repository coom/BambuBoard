# 📖 Bambu Dashboard — Documentation

> [🇫🇷 Français](https://github.com/coom/BambuBoard/blob/main/bambu_dashboard/DOCS.md) · 🇬🇧 English

---

## 📋 Prerequisites

| | |
|---|---|
| 🏠 **Home Assistant** | **OS** or **Supervised** — *Container mode has no Supervisor and therefore does not support add-ons* |
| 🖨️ **Printer** | Bambu Lab with AMS, reachable on the local network from HA |
| 📡 **Network mode** | **LAN enabled** on the printer *(mandatory — the local MQTT broker is disabled otherwise)* |

---

## 🔑 Retrieving printer credentials

On the printer's touchscreen:

| Field | 📍 Path |
|---|---|
| `printer_ip` | Settings → **Wi-Fi** → *(displayed IP address)* |
| `printer_serial` | Settings → **About** → **S/N** *(format `01P00A1B2C3D4E5F`)* |
| `printer_access_code` | Settings → **Network** → **Access Code** *(8 digits)* |

> ⚠️ **Important**: enable **LAN-only mode** (or LAN + Cloud)
> under Settings → Network. Without this, the local MQTT broker is disabled
> and the add-on **cannot connect**.

---

## ⚙️ Configuration options

```yaml
printer_ip: "192.168.1.42"          # Local IP of the printer
printer_serial: "01P00A1B2C3D4E5F"  # S/N (16 characters)
printer_access_code: "12345678"     # LAN access code (8 digits)
ha_webhook_url: ""                   # (optional) webhook for notifications
ha_webhook_token: ""                 # (optional) Bearer token if required
low_stock_threshold: 20              # Threshold in % for low-stock notification
```

### 🔔 Home Assistant notifications

To receive a notification in HA when a spool drops below
`low_stock_threshold`:

**1.** Create an automation in HA that listens to a webhook:

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

**2.** In the add-on options, paste the webhook URL:

```yaml
ha_webhook_url: "http://supervisor/core/api/webhook/bambu_low_stock"
```

> 💡 The notification is sent **once per threshold crossing** —
> no spam.

---

## 🎯 Usage

### 🏁 First start

**1.** After starting the add-on, open the web interface via **Open
Web UI** or the **Bambu** 🎨 side panel

**2.** The **AMS** tab shows the current state of all 4 slots as soon as
the first MQTT message is received *(within a few seconds)*

**3.** The **Inventory** tab is empty — it fills up **automatically**
as spools are detected in the AMS

### 🔄 Spool lifecycle

| Status | Meaning | Transition |
|:---:|---|---|
| 🟢 `active` | Spool physically in the AMS, associated with a `tray_uuid` | *Automatic (AMS detection)* |
| 🔵 `idle` | Spool known but not currently loaded | *Automatic (removed from AMS)* |
| 🔴 `empty` | `remain ≤ 0%` | *Automatic* |
| ⚫ `archived` | Spool removed from the catalogue | **Manual** *(« Archive » button)* |

> 🛒 The **Rebuy** button archives the old spool and creates a new
> copy at **100 %** / `idle`, useful when you repurchase the same
> filament.

### ✨ Registering an unknown spool from the AMS

When a spool loaded in the AMS does not yet exist in the inventory,
its slot shows a 🏷️ **"Unknown spool — Register"** button. The form
opens **pre-filled** with *all* the metadata exposed by the printer:

| Field | Source | Example |
|---|---|---|
| **Name** | `sub_brands` + *guessed colour* | `PLA Basic Black` |
| **Brand** | default | `Bambu Lab` |
| **Filament code** | `tray_info_idx` | `GFA00` |
| **Colour *(hex)*** | `color` *(exposed by the AMS)* | `#000000` |
| **Colour *(name)*** | *guessed* from the hex | `Black` |
| **Initial weight** | `tray_weight` | `1000 g` |
| **Initial remain** | current AMS value | `98 %` |
| **tray_uuid / tag_uid** | auto | *(reconciliation)* |

> 🎨 The colour name is guessed via a palette of **23 colours**
> (Euclidean RGB distance search) to visually distinguish
> spools of the same type in the inventory.

Adjust whatever you like and confirm — the spool is created as 🟢 `active`
*(since it is present in the AMS)*.

### 🏷️ NFC scan via Flipper Zero

If you have a Flipper Zero with the `bambu_scanner` app installed:

**1.** **Inventory** tab → 🛰️ **Flipper Scan** button

**2.** **Connect** → select the Flipper's serial port

**3.** Launch the `bambu_scanner` app on the Flipper, hold a spool close

**4.** Confirm with **OK** on the Flipper

**5.** The spool creation form opens **pre-filled** ✨

> 🌐 **Browser required**: **Chrome** or **Edge** — *Web Serial is
> not supported by Firefox/Safari*.

> 📖 See [`flipper/bambu_scanner/README.md`](../flipper/bambu_scanner/README.md)
> for Flipper plugin installation (a pre-compiled `.fap` is
> provided — no build required).

---

## 🛠️ Frontend overlay *(rapid iteration)*

The add-on supports a **frontend overlay** via
`/share/bambu_dashboard/frontend/` to modify `index.html` **without
rebuilding the Docker image**:

**1.** Copy `frontend/index.html` from the image into
`/share/bambu_dashboard/frontend/index.html`

**2.** Edit it freely

**3.** **Restart the add-on** — changes are applied immediately 🔄

> 🗑️ Delete the file to revert to the version embedded in
> the Docker image.

---

## 💾 Data persistence

- 📁 The **SQLite** database is located at `/data/bambu.db` *(persisted by HA
  between add-on restarts and updates)*
- ⚡ **WAL** mode enabled *(performance + concurrent reads)*
- 📉 Consumption logs are **append-only**, filtered by a
  **2 %** threshold *(to avoid MQTT noise)*

---

## 🩺 Troubleshooting

### ❌ The add-on starts but `connected: false` in the AMS

- ✅ Check **LAN mode** on the printer
- ✅ Check that `printer_ip` is **reachable** from HA *(ping)*
- ✅ Check the `printer_access_code` *(watch out for special characters)*
- 📋 Look at the add-on logs: **TLS** or **auth** errors = wrong code
  or S/N

### ❌ *"Failed to open serial port"* on Flipper scan

> 🔒 **Most common cause**: another program is holding the COM port.

- 🛑 **Close qFlipper, PuTTY, Arduino IDE, any serial monitor** that
  could be holding the COM port open *(Windows → exclusive COM ports)*
- 🔌 **Unplug and replug** the Flipper
- 🔄 **Relaunch Chrome**

### ❌ The form does not open after Flipper scan

- ✅ Make sure the app on the Flipper is **`bambu_scanner`**
  *(not the old `bambu_nfc`)*
- 🔍 Open **Chrome DevTools** *(F12)* and check the Console tab for
  `BAMBU_NFC parse error` errors
- 🔒 Verify you are on **HTTPS** on HA *(the HA ingress is
  HTTPS by default — Web Serial requires a secure origin)*

### ❌ Low-stock notifications are not sent

- ✅ Check that `ha_webhook_url` is filled in
- 🧪 **Test the webhook manually** with `curl`
- ℹ️ Notifications are sent **once per threshold crossing**
  *(anti-spam)* — swap the spool to retest

---

## 🔗 Useful links

- 📦 **Repository**: https://github.com/coom/BambuBoard
- 🛰️ **Flipper plugin**: [`flipper/bambu_scanner/`](../flipper/bambu_scanner/)
- 📜 **Changelog**: [`CHANGELOG.md`](./CHANGELOG.md)

---

## 👥 Credits

Developed by **Erti**, with contributions from **coom** on the Flipper
Zero module *(the `bambu_scanner` app)*. See upstream contributions in the
[Flipper plugin README](../flipper/bambu_scanner/README.md#-attribution-et-licences).
