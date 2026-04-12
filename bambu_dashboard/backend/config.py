import os

PRINTER_IP = os.environ.get("PRINTER_IP", "")
PRINTER_SERIAL = os.environ.get("PRINTER_SERIAL", "")
PRINTER_ACCESS_CODE = os.environ.get("PRINTER_ACCESS_CODE", "")

HA_WEBHOOK_URL = os.environ.get("HA_WEBHOOK_URL", "")
HA_WEBHOOK_TOKEN = os.environ.get("HA_WEBHOOK_TOKEN", "")

LOW_STOCK_THRESHOLD = int(os.environ.get("LOW_STOCK_THRESHOLD", "20"))

NFC_API_KEY = os.environ.get("NFC_API_KEY", "")
