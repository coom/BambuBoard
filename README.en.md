<div align="center">

> [🇫🇷 Français](README.md) · 🇬🇧 English

# 🎨 Bambu Dashboard

### *Home Assistant add-on repository to track, inventory and optimize your Bambu Lab spools*

![amd64](https://img.shields.io/badge/amd64-supported-success?style=flat-square)
![aarch64](https://img.shields.io/badge/aarch64-supported-success?style=flat-square)
![armv7](https://img.shields.io/badge/armv7-supported-success?style=flat-square)
![HA Add-on](https://img.shields.io/badge/Home%20Assistant-Add--on-41BDF5?style=flat-square&logo=home-assistant&logoColor=white)
![License](https://img.shields.io/badge/license-MIT-blue?style=flat-square)

**Direct MQTT LAN** *·* **Real-time AMS** *·* **Spool inventory** *·* **KPIs** *·* **Flipper Zero & Android NFC scanning**

</div>

---

## ✨ What you get

| | |
|---|---|
| 🖨️ **Real-time AMS** | The 4 slots, color, type, remaining weight — live via MQTT TLS |
| 📦 **Persistent inventory** | Spool catalog with automatic `tray_uuid` reconciliation → `active/idle/empty/archived` |
| 📊 **KPIs** | Total consumption, sessions, top materials, last 7 / 30 days |
| 🏷️ **Bambu NFC scanning** | Read 2024+ spool tags via a **Flipper Zero** or a NFC-capable **Android phone** |
| 🚫 **Zero Bambu Cloud** | Fully local, LAN only, no account required |

---

## 🚀 30-second install

> 1️⃣ Open **Settings → Add-ons → Store**
>
> 2️⃣ Menu **⋮** (top right) → **Repositories**
>
> 3️⃣ Paste the URL below and click **Add**:
>
> ```
> https://github.com/coom/BambuBoard
> ```
>
> 4️⃣ The **Bambu Dashboard Add-ons** section appears ✨
>
> 5️⃣ Click **Bambu Dashboard → Install**
>
> 6️⃣ Fill in `printer_ip`, `printer_serial`, `printer_access_code`
>
> 7️⃣ **Start** → **Open the Web UI** 🎉

---

## 📦 Included add-ons

| Add-on | Description | Version |
|---|---|:---:|
| 🎨 [**Bambu Dashboard**](./bambu_dashboard/) | Full dashboard: AMS, inventory, KPIs, NFC scanning | ![v1.1.0](https://img.shields.io/badge/v1.1.0-latest-success?style=flat-square) |

---

## 📱 Android application *(optional but handy)*

The [`android/bambu_scanner/`](./android/bambu_scanner/) folder contains a
companion Android app that scans Bambu Lab NFC spool tags directly with your
phone and sends them to the dashboard in one tap.

> 💡 **Ready-to-use APK**: download
> [`android/bambu_scanner/dist/bambu_scanner.apk`](./android/bambu_scanner/dist/bambu_scanner.apk),
> install it on your phone — that's it.
>
> **Compatible**: Samsung, Pixel (Tensor), OnePlus and any phone with an NXP
> NFC chip (MIFARE Classic). Android 7.0+.

The full guide (dashboard configuration, usage, troubleshooting) lives in the
[**Android app README**](./android/bambu_scanner/README.md).

---

## 🛰️ Flipper Zero plugin *(optional but cool)*

The [`flipper/bambu_scanner/`](./flipper/bambu_scanner/) folder contains a
Flipper Zero app that scans Bambu Lab NFC spool tags (UID-derived keys,
compatible with **2024+** spools) and forwards the metadata to the dashboard
via **USB Web Serial**.

> 💡 **Good news**: a pre-compiled `.fap` (official SDK 1.4.3) is committed
> straight to
> [`flipper/bambu_scanner/dist/bambu_scanner.fap`](./flipper/bambu_scanner/dist/bambu_scanner.fap).
>
> **No Python, no ufbt, no toolchain needed** — download, drag-and-drop into
> qFlipper, done. ✨

Details (custom build, alternate firmware, troubleshooting) are in the
[**plugin README**](./flipper/bambu_scanner/README.md).

---

## 🏗️ Architecture

```
┌────────────────┐   MQTT TLS :8883   ┌─────────────────────┐
│    Bambu Lab   │ ──────────────────▶│   bambu_dashboard   │
│     printer    │      (LAN only)    │     (HA add-on)     │
└────────────────┘                    └──────────┬──────────┘
                                                 │
                          ┌───────────────┬──────┼──────────────────────┐
                          │               │      │                      │
                          ▼               ▼      ▼                      ▼
                   HTTPS HA ingress  Port 8000  HA webhook        Web Serial API
                          │               │      │                      │
                          ▼               ▼      ▼                      ▼
                  ┌──────────────┐  ┌──────────┐ ┌─────────────┐ ┌──────────────┐
                  │   Browser    │  │ Android  │ │  HA Notify  │ │ Flipper Zero │
                  │ (vanilla SPA)│  │  NFC App │ │   (mobile)  │ │ bambu_scanner│
                  └──────────────┘  └──────────┘ └─────────────┘ └──────────────┘
```

---

## ✅ Compatibility

| | |
|---|---|
| 🖨️ **Printers** | Any Bambu Lab with AMS — *X1 / X1C / X1E / P1S / P1P / A1 / A1 mini* |
| 🏗️ **HA architectures** | `amd64` · `aarch64` · `armv7` |
| 🌐 **Browsers** *(NFC scanning)* | **Chrome** or **Edge** only — *Web Serial API required* |
| 📡 **Printer mode** | **LAN only** or LAN + Cloud *(local MQTT required)* |

---

## 👥 Credits

| Role | Person |
|---|---|
| 🧑‍💻 **Main author** | **Erti** *(HA add-on: FastAPI backend, SPA frontend, inventory, KPIs, NFC integration on the dashboard side)* |
| 🛰️ **Major contributor** | **coom** *(Flipper Zero plugin `bambu_scanner`, Android application `Bambu Scanner`)* |

> 💡 Upstream contributions *(BambuTagger KDF, parser derived from
> `flipper-bambu`)* are detailed in the
> [Flipper plugin README](./flipper/bambu_scanner/README.md#-attribution-and-licenses).

---

## 📜 License

The dashboard code is **MIT** licensed.

⚠️ The Flipper Zero app uses a KDF (`bambu_crypto.c/h`) imported from
[ductai199x/BambuTagger](https://github.com/ductai199x/BambuTagger) under an
*"educational and personal use"* license. See the
[plugin README](./flipper/bambu_scanner/README.md#-attribution-and-licenses).

---

<div align="center">

*Made with ❤️ and lots of PLA filament by **Erti** (with **coom** for the Flipper and the Android app)*

</div>
