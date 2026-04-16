import os

PRINTER_IP = os.environ.get("PRINTER_IP", "")
PRINTER_SERIAL = os.environ.get("PRINTER_SERIAL", "")
PRINTER_ACCESS_CODE = os.environ.get("PRINTER_ACCESS_CODE", "")

NFC_API_KEY = os.environ.get("NFC_API_KEY", "")

LANGUAGE = os.environ.get("BAMBU_LANGUAGE", "auto")
RESOLVED_LANGUAGE = "fr" if LANGUAGE in ("auto", "") else LANGUAGE
