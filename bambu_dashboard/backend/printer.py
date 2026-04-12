"""Connexion MQTT directe au printer Bambu Lab (comme ha-bambulab).
Pas de dépendance lourde — juste paho-mqtt + TLS."""

import json
import ssl
import threading
import uuid
import paho.mqtt.client as mqtt


PUSH_ALL = json.dumps({
    "pushing": {"sequence_id": "0", "command": "pushall"}
})


class PrinterManager:
    def __init__(self):
        self._ip = ""
        self._access_code = ""
        self._serial = ""
        self._client: mqtt.Client | None = None
        self._connected = False
        self._cache = {"connected": False, "slots": []}
        self._current_print_job: str | None = None
        self._lock = threading.Lock()

    def reconfigure(self, ip: str, access_code: str, serial: str):
        self._ip = ip
        self._access_code = access_code
        self._serial = serial

    def _parse_color(self, raw: str) -> str | None:
        if raw and len(raw) >= 6:
            return f"#{raw[:6]}"
        return None

    def _on_connect(self, client, userdata, flags, rc, properties=None):
        if rc == 0:
            self._connected = True
            topic = f"device/{self._serial}/report"
            client.subscribe(topic)
            # Demander un push complet de toutes les données
            client.publish(f"device/{self._serial}/request", PUSH_ALL)
        else:
            self._connected = False

    def _on_disconnect(self, client, userdata, rc, properties=None):
        self._connected = False
        with self._lock:
            self._cache = {"connected": False, "slots": []}

    def _on_message(self, client, userdata, msg):
        try:
            data = json.loads(msg.payload)
        except (json.JSONDecodeError, ValueError):
            return

        print_data = data.get("print", {})

        # Capturer le nom du fichier en cours d'impression
        subtask = print_data.get("subtask_name")
        gcode = print_data.get("gcode_file")
        if subtask:
            self._current_print_job = subtask
        elif gcode:
            self._current_print_job = gcode

        ams_info = print_data.get("ams", {})
        ams_list = ams_info.get("ams", [])
        if not ams_list:
            return

        ams = ams_list[0]
        trays_by_id = {}
        for t in ams.get("tray", []):
            try:
                trays_by_id[int(t["id"])] = t
            except (KeyError, ValueError):
                continue

        slots = []
        for i in range(4):
            tray = trays_by_id.get(i)
            if tray and tray.get("tray_type"):
                remain = tray.get("remain")
                if isinstance(remain, str) and remain.isdigit():
                    remain = int(remain)
                slots.append({
                    "index": i,
                    "tray_uuid": tray.get("tray_uuid") or None,
                    "tag_uid": tray.get("tag_uid") or None,
                    "tray_type": tray.get("tray_type") or None,
                    "tray_sub_brands": tray.get("tray_sub_brands") or None,
                    "tray_id_name": tray.get("tray_id_name") or None,
                    "tray_info_idx": tray.get("tray_info_idx") or None,
                    "nozzle_temp_min": int(tray["nozzle_temp_min"]) if tray.get("nozzle_temp_min") else None,
                    "nozzle_temp_max": int(tray["nozzle_temp_max"]) if tray.get("nozzle_temp_max") else None,
                    "color": self._parse_color(tray.get("tray_color", "")),
                    "remain": remain,
                    "tray_weight": tray.get("tray_weight"),
                    "diameter": tray.get("tray_diameter"),
                })
            else:
                slots.append({
                    "index": i,
                    "tray_uuid": None, "tag_uid": None, "tray_type": None,
                    "tray_sub_brands": None, "tray_id_name": None,
                    "tray_info_idx": None, "nozzle_temp_min": None,
                    "nozzle_temp_max": None, "color": None, "remain": None,
                    "tray_weight": None, "diameter": None,
                })

        new_data = {"connected": True, "slots": slots, "print_job": self._current_print_job}

        # Appeler le callback d'enrichissement si défini
        if self._enrich_callback:
            try:
                self._enrich_callback(new_data)
            except Exception:
                pass

        with self._lock:
            self._cache = new_data

    def connect(self, enrich_callback=None):
        """Connexion MQTT directe au printer — non bloquant.
        enrich_callback(data) est appelé à chaque message AMS reçu."""
        self._enrich_callback = enrich_callback

        if not self._ip or not self._serial:
            return

        client = mqtt.Client(
            client_id=f"bambu_dashboard_{uuid.uuid4().hex[:8]}",
            protocol=mqtt.MQTTv311,
        )
        client.username_pw_set("bblp", self._access_code)

        # TLS sans vérification du certificat (comme ha-bambulab)
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        client.tls_set_context(ctx)

        client.on_connect = self._on_connect
        client.on_disconnect = self._on_disconnect
        client.on_message = self._on_message

        client.connect_async(self._ip, port=8883, keepalive=60)
        client.loop_start()  # Thread de fond — non bloquant
        self._client = client

    def disconnect(self):
        if self._client:
            try:
                self._client.loop_stop()
                self._client.disconnect()
            except Exception:
                pass
        self._connected = False

    def get_ams_data(self) -> dict:
        """Retourne le dernier état AMS connu (instantané)."""
        with self._lock:
            return self._cache


printer_manager = PrinterManager()
