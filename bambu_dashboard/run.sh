#!/usr/bin/with-contenv bashio
set -e

export PRINTER_IP="$(bashio::config 'printer_ip')"
export PRINTER_SERIAL="$(bashio::config 'printer_serial')"
export PRINTER_ACCESS_CODE="$(bashio::config 'printer_access_code')"
export HA_WEBHOOK_URL="$(bashio::config 'ha_webhook_url')"
export HA_WEBHOOK_TOKEN="$(bashio::config 'ha_webhook_token')"
export LOW_STOCK_THRESHOLD="$(bashio::config 'low_stock_threshold')"
export BAMBU_DB_PATH="/data/bambu.db"

bashio::log.info "Bambu Dashboard starting..."
bashio::log.info "Printer IP: ${PRINTER_IP}"
bashio::log.info "DB path:    ${BAMBU_DB_PATH}"

# Overlay du frontend depuis /share/bambu_dashboard/frontend/ si présent.
# Permet de mettre à jour index.html sans rebuild de l'image Docker.
# ATTENTION : si ce dossier contient un ancien index.html, il écrasera
# la version embarquée dans l'image et les MAJ ne seront pas visibles !
SHARE_FRONTEND="/share/bambu_dashboard/frontend"
if [ -d "${SHARE_FRONTEND}" ] && [ -f "${SHARE_FRONTEND}/index.html" ]; then
    bashio::log.warning "Frontend: OVERLAY ACTIF depuis ${SHARE_FRONTEND}"
    bashio::log.warning "Si le dashboard semble ancien apres une MAJ, supprimez ${SHARE_FRONTEND}/index.html"
    cp -r "${SHARE_FRONTEND}/." /app/frontend/
else
    bashio::log.info "Frontend: utilisation de l'image embarquee"
fi

cd /app/backend
exec python3 -m uvicorn main:app --host 0.0.0.0 --port 8000
