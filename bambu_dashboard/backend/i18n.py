"""Dictionnaire i18n backend — erreurs API.

La langue est figée au démarrage via config.RESOLVED_LANGUAGE. Ce module
sera également utilisé quand les notifications HA seront implémentées
(clés notif.* à ajouter à ce moment-là).
"""
from config import RESOLVED_LANGUAGE

STRINGS = {
    "fr": {
        "error.spool.not_found":       "Bobine non trouvée",
        "error.spool.name_required":   "Le champ 'name' est requis",
        "error.spool.status_required": "Le champ 'status' est requis",
        "error.spool.invalid_status":  "Statut invalide ou bobine non trouvée",
        "error.nfc.api_key_invalid":   "Clé API invalide",
        "error.nfc.missing_fields":    "Champs requis : tag_uid, tray_type",
    },
    "en": {
        "error.spool.not_found":       "Spool not found",
        "error.spool.name_required":   "The 'name' field is required",
        "error.spool.status_required": "The 'status' field is required",
        "error.spool.invalid_status":  "Invalid status or spool not found",
        "error.nfc.api_key_invalid":   "Invalid API key",
        "error.nfc.missing_fields":    "Required fields: tag_uid, tray_type",
    },
}


def t(key: str, **params) -> str:
    """Retourne la chaine traduite pour la langue resolvue.

    Fallback: langue courante -> fr -> cle brute. Substitution {var} via .format.
    """
    lang_dict = STRINGS.get(RESOLVED_LANGUAGE, STRINGS["fr"])
    s = lang_dict.get(key) or STRINGS["fr"].get(key) or key
    return s.format(**params) if params else s
