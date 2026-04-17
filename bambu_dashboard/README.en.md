# 🎨 Bambu Dashboard

> [🇫🇷 Français](README.md) · 🇬🇧 English

![Supports amd64][amd64-shield]
![Supports aarch64][aarch64-shield]
![Supports armv7][armv7-shield]

> **All-in-one Bambu Lab AMS dashboard** — spool tracking, consumption KPIs,
> Flipper Zero and Android NFC scanning.
> Integrated directly into Home Assistant via ingress. 🏠

---

## ✨ Features

- 📡 **Direct MQTT TLS connection** to the printer — *no Bambu Cloud, no
  Bambu Studio, zero account*
- 🖨️ **Real-time AMS view** — state of the 4 slots, type, color, remaining
  weight
- 📦 **Persistent spool inventory** — automatic reconciliation via
  `tray_uuid`, cycle `active → idle → empty → archived`
- 📊 **Consumption KPIs** — total, print sessions, top materials, last 7 /
  30 days
- 🏷️ **Bambu NFC scanning** — recognizes **2024+** spools via a Flipper
  Zero (pre-compiled `.fap` provided) or the **companion Android app**
  ([`Bambu Scanner`](../android/bambu_scanner/README.md))
- 🎨 **Smart pre-fill** — the color name is guessed from the hex (EN
  palette) and appended to the name *(e.g., "PLA Basic Black")*

---

## 🚀 Quick install

> **1.** Add this repository under **Settings → Add-ons → Store →
> Repositories**:
>
> ```
> https://github.com/coom/BambuBoard
> ```
>
> **2.** Install **Bambu Dashboard** from the section that appears ✨
>
> **3.** Fill in the **3 required fields** (`printer_ip`, `printer_serial`,
> `printer_access_code`) — see **Documentation** to retrieve them
>
> **4.** Start the add-on and open the web UI 🎉

---

## ⚙️ Minimal configuration

```yaml
printer_ip: "192.168.1.42"
printer_serial: "01P00A1B2C3D4E5F"
printer_access_code: "12345678"
```

> 📖 The **Documentation** tab details every option, the procedure to
> retrieve the printer credentials, and full troubleshooting.

---

## 👥 Credits

Project created by **Erti** *(HA add-on, backend, frontend)*. **coom** is a
major contributor *(Flipper Zero plugin `bambu_scanner`, Android
application `Bambu Scanner`)*.

---

[amd64-shield]: https://img.shields.io/badge/amd64-yes-green.svg
[aarch64-shield]: https://img.shields.io/badge/aarch64-yes-green.svg
[armv7-shield]: https://img.shields.io/badge/armv7-yes-green.svg
