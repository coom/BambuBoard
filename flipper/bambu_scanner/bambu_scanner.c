#include <furi.h>
#include <gui/gui.h>
#include <notification/notification_messages.h>
#include <nfc/nfc.h>
#include <lib/nfc/protocols/mf_classic/mf_classic.h>
#include <lib/nfc/protocols/mf_classic/mf_classic_poller_sync.h>
#include <lib/nfc/protocols/iso14443_3a/iso14443_3a_poller_sync.h>
#include "bambu_parser.h"
#include "bambu_filaments.h"
#include "bambu_crypto.h"

#define TAG "BambuNFC"

// BAMBU_KEY_A et DEFAULT_KEY_B supprimés (inutilisés en mode stub — à restaurer Task 4)

// ── Données spool parsées ─────────────────────────────────────────────────────

typedef struct {
    char tag_uid[24];       // UID hexadécimal
    char variant_id[8];     // ex: "A00-R3"
    char material_id[8];    // ex: "GFA00"
    char filament_type[17]; // ex: "PLA"
    char detailed_type[17]; // ex: "PLA Basic"
    uint8_t color_r, color_g, color_b, color_a;
    uint16_t weight_g;
    char filament_code[8];  // ex: "10204" (depuis lookup)
    char color_name[32];    // ex: "Hot Pink" (depuis lookup)
} BambuSpoolData;

// ── Parsing ───────────────────────────────────────────────────────────────────

static bool bambu_parse_mf_classic(const MfClassicData* mfc, BambuSpoolData* out) {
    if(!bambu_tag_is_valid(mfc)) return false;

    // UID
    const Iso14443_3aData* iso = mfc->iso14443_3a_data;
    out->tag_uid[0] = '\0';
    for(uint8_t i = 0; i < iso->uid_len && i < 10; i++) {
        char hex[3];
        snprintf(hex, sizeof(hex), "%02X", iso->uid[i]);
        size_t cur = strlen(out->tag_uid);
        if(cur + 2 < sizeof(out->tag_uid)) {
            out->tag_uid[cur]     = hex[0];
            out->tag_uid[cur + 1] = hex[1];
            out->tag_uid[cur + 2] = '\0';
        }
    }

    // Block 1: variant_id (bytes 0-6), material_id (bytes 8-13)
    const uint8_t* b1 = mfc->block[BLOCK_MATERIAL_IDS].data;
    bambu_copy_ascii_string(out->variant_id,  &b1[0], 7);
    bambu_copy_ascii_string(out->material_id, &b1[8], 6);

    // Block 2: filament type (PLA, PETG…)
    bambu_copy_ascii_string(out->filament_type, mfc->block[BLOCK_FILAMENT_TYPE].data, 16);

    // Block 4: detailed type (PLA Basic, PLA Matte…)
    bambu_copy_ascii_string(out->detailed_type, mfc->block[BLOCK_DETAILED_TYPE].data, 16);

    // Block 5: RGBA (bytes 0-3), weight LE uint16 (bytes 4-5)
    const uint8_t* b5 = mfc->block[BLOCK_COLOR_WEIGHT].data;
    out->color_r  = b5[0];
    out->color_g  = b5[1];
    out->color_b  = b5[2];
    out->color_a  = b5[3];
    out->weight_g = bambu_read_le16(&b5[4]);

    // Lookup filament_code et color_name depuis variant_id
    const BambuFilamentInfo* fi = bambu_lookup_filament(out->variant_id);
    if(fi) {
        strncpy(out->filament_code, fi->filament_code, sizeof(out->filament_code) - 1);
        out->filament_code[sizeof(out->filament_code) - 1] = '\0';
        strncpy(out->color_name, fi->color_name, sizeof(out->color_name) - 1);
        out->color_name[sizeof(out->color_name) - 1] = '\0';
    } else {
        // Fallback : material_id comme code, couleur en hex
        strncpy(out->filament_code, out->material_id, sizeof(out->filament_code) - 1);
        out->filament_code[sizeof(out->filament_code) - 1] = '\0';
        snprintf(out->color_name, sizeof(out->color_name),
                 "#%02X%02X%02X", out->color_r, out->color_g, out->color_b);
    }

    return true;
}

// ── Application ───────────────────────────────────────────────────────────────

typedef struct {
    Gui* gui;
    ViewPort* view_port;
    FuriMessageQueue* event_queue;
    BambuSpoolData spool;

    bool scanning;
    bool scan_done;
    bool scan_failed;
    bool sent;

    FuriThread* nfc_thread;
} BambuNfcApp;

// ── Thread NFC ────────────────────────────────────────────────────────────────

static int32_t nfc_thread_worker(void* ctx) {
    BambuNfcApp* app = (BambuNfcApp*)ctx;

    Nfc* nfc = nfc_alloc();
    bool success = false;

    // ── Passe 1 : lire l'UID via ISO14443-3A (sans auth MIFARE) ─────────
    Iso14443_3aData* iso_data = iso14443_3a_alloc();
    Iso14443_3aError iso_err = iso14443_3a_poller_sync_read(nfc, iso_data);
    FURI_LOG_I(TAG, "iso_read=%d uid_len=%u", iso_err, iso_data->uid_len);

    if(iso_err == Iso14443_3aErrorNone && iso_data->uid_len > 0) {
        // ── Passe 2 : dériver les 16 clés depuis l'UID ─────────────────
        BambuKeys derived;
        calculate_all_keys(iso_data->uid, iso_data->uid_len, &derived);

        FURI_LOG_I(TAG, "keys derived, first=%02X%02X%02X%02X%02X%02X",
            derived.keys[0][0], derived.keys[0][1], derived.keys[0][2],
            derived.keys[0][3], derived.keys[0][4], derived.keys[0][5]);

        // ── Passe 3 : lire le tag MFC avec les clés dérivées ───────────
        MfClassicData* mfc_data = mf_classic_alloc();
        mfc_data->type = MfClassicType1k;

        MfClassicDeviceKeys keys;
        memset(&keys, 0, sizeof(keys));
        for(uint8_t i = 0; i < BAMBU_NUM_SECTORS; i++) {
            memcpy(keys.key_a[i].data, derived.keys[i], BAMBU_KEY_LENGTH);
            memcpy(keys.key_b[i].data, derived.keys[i], BAMBU_KEY_LENGTH);
            keys.key_a_mask |= (1ULL << i);
            keys.key_b_mask |= (1ULL << i);
        }

        MfClassicError err = mf_classic_poller_sync_read(nfc, &keys, mfc_data);
        FURI_LOG_I(TAG, "mf_read=%d", err);

        if(err == MfClassicErrorNone || err == MfClassicErrorPartialRead) {
            success = bambu_parse_mf_classic(mfc_data, &app->spool);
            FURI_LOG_I(TAG, "parse=%d uid=%s detailed=%s",
                success, app->spool.tag_uid, app->spool.detailed_type);
        }

        mf_classic_free(mfc_data);
    }

    iso14443_3a_free(iso_data);
    nfc_free(nfc);

    if(success) {
        app->scan_done = true;
    } else {
        app->scan_failed = true;
    }
    app->scanning = false;
    return 0;
}

static void start_nfc_scan(BambuNfcApp* app) {
    if(app->nfc_thread) {
        furi_thread_join(app->nfc_thread);
        furi_thread_free(app->nfc_thread);
        app->nfc_thread = NULL;
    }
    app->scan_failed = false;
    app->scanning    = true;
    app->nfc_thread  = furi_thread_alloc_ex("BambuScan", 4 * 1024, nfc_thread_worker, app);
    furi_thread_start(app->nfc_thread);
}

// ── Envoi série (Web Serial API) ──────────────────────────────────────────────
// Format : \nBAMBU_NFC:{...}\n  — le navigateur filtre sur ce préfixe.

static void send_via_serial(BambuNfcApp* app) {
    char json[512];
    snprintf(json, sizeof(json),
        "{"
        "\"tag_uid\":\"%s\","
        "\"tray_type\":\"%s\","
        "\"sub_brands\":\"%s\","
        "\"color_hex\":\"%02X%02X%02X\","
        "\"color_name\":\"%s\","
        "\"filament_code\":\"%s\","
        "\"initial_weight\":%u,"
        "\"brand\":\"Bambu Lab\""
        "}",
        app->spool.tag_uid,
        app->spool.filament_type,
        app->spool.detailed_type,
        app->spool.color_r, app->spool.color_g, app->spool.color_b,
        app->spool.color_name,
        app->spool.filament_code,
        app->spool.weight_g);

    printf("\nBAMBU_NFC:%s\n", json);
    app->sent = true;
}

// ── Rendu écran ───────────────────────────────────────────────────────────────

static void draw_callback(Canvas* canvas, void* ctx) {
    BambuNfcApp* app = (BambuNfcApp*)ctx;
    canvas_clear(canvas);
    canvas_set_font(canvas, FontPrimary);

    if(app->scanning) {
        canvas_draw_str(canvas, 2, 12, "Bambu NFC");
        canvas_set_font(canvas, FontSecondary);
        canvas_draw_str(canvas, 2, 28, "Scan en cours...");
        canvas_draw_str(canvas, 2, 40, "Approchez la bobine.");
        canvas_draw_str(canvas, 2, 56, "[Retour] Quitter");
        return;
    }

    if(!app->scan_done) {
        canvas_draw_str(canvas, 2, 12, "Bambu NFC");
        canvas_set_font(canvas, FontSecondary);
        if(app->scan_failed) {
            canvas_draw_str(canvas, 2, 28, "Tag non reconnu.");
            canvas_draw_str(canvas, 2, 40, "[OK] Reessayer");
        } else {
            canvas_draw_str(canvas, 2, 28, "Approchez une bobine");
            canvas_draw_str(canvas, 2, 40, "Bambu Lab du Flipper.");
        }
        canvas_draw_str(canvas, 2, 56, "[Retour] Quitter");
        return;
    }

    if(app->sent) {
        canvas_draw_str(canvas, 2, 12, "Envoye !");
        canvas_set_font(canvas, FontSecondary);
        canvas_draw_str(canvas, 2, 24, app->spool.detailed_type);
        canvas_draw_str(canvas, 2, 36, app->spool.color_name);
        char weight[24];
        snprintf(weight, sizeof(weight), "Poids: %ug", app->spool.weight_g);
        canvas_draw_str(canvas, 2, 48, weight);
        canvas_draw_str(canvas, 2, 60, "[OK] Nouveau  [Ret] Quitter");
        return;
    }

    // Scan réussi, confirmation avant envoi
    canvas_draw_str(canvas, 2, 12, app->spool.detailed_type);
    canvas_set_font(canvas, FontSecondary);
    canvas_draw_str(canvas, 2, 24, app->spool.color_name);
    char weight[24];
    snprintf(weight, sizeof(weight), "Poids: %ug", app->spool.weight_g);
    canvas_draw_str(canvas, 2, 36, weight);
    canvas_draw_str(canvas, 2, 48, app->spool.tag_uid);
    canvas_draw_str(canvas, 2, 60, "[OK] Envoyer  [Ret] Annuler");
}

static void input_callback(InputEvent* event, void* ctx) {
    BambuNfcApp* app = (BambuNfcApp*)ctx;
    furi_message_queue_put(app->event_queue, event, 0);
}

// ── Main ──────────────────────────────────────────────────────────────────────

int32_t bambu_scanner_app(void* p) {
    UNUSED(p);

    BambuNfcApp* app = malloc(sizeof(BambuNfcApp));
    memset(app, 0, sizeof(BambuNfcApp));

    app->event_queue = furi_message_queue_alloc(8, sizeof(InputEvent));
    app->view_port   = view_port_alloc();
    view_port_draw_callback_set(app->view_port, draw_callback, app);
    view_port_input_callback_set(app->view_port, input_callback, app);

    app->gui = furi_record_open(RECORD_GUI);
    gui_add_view_port(app->gui, app->view_port, GuiLayerFullscreen);

    NotificationApp* notifications = furi_record_open(RECORD_NOTIFICATION);

    bool running         = true;
    bool awaiting_confirm = false;

    start_nfc_scan(app);

    while(running) {
        if(app->scan_done && !awaiting_confirm && !app->sent) {
            awaiting_confirm = true;
            notification_message(notifications, &sequence_success);
        }

        InputEvent event;
        if(furi_message_queue_get(app->event_queue, &event, 100) == FuriStatusOk) {
            if(event.type == InputTypeShort) {
                if(event.key == InputKeyBack) {
                    if(app->sent) {
                        // Nouveau scan
                        memset(&app->spool, 0, sizeof(BambuSpoolData));
                        app->scan_done = false;
                        app->scan_failed = false;
                        app->sent = false;
                        awaiting_confirm = false;
                        start_nfc_scan(app);
                    } else if(awaiting_confirm) {
                        awaiting_confirm = false;
                        app->scan_done   = false;
                        memset(&app->spool, 0, sizeof(BambuSpoolData));
                        start_nfc_scan(app);
                    } else {
                        running = false;
                    }
                } else if(event.key == InputKeyOk) {
                    if(app->scan_failed) {
                        app->scan_failed = false;
                        start_nfc_scan(app);
                    } else if(awaiting_confirm) {
                        awaiting_confirm = false;
                        send_via_serial(app);
                    } else if(app->sent) {
                        memset(&app->spool, 0, sizeof(BambuSpoolData));
                        app->scan_done = false;
                        app->sent = false;
                        awaiting_confirm = false;
                        start_nfc_scan(app);
                    }
                }
            }
        }

        view_port_update(app->view_port);
    }

    if(app->nfc_thread) {
        furi_thread_join(app->nfc_thread);
        furi_thread_free(app->nfc_thread);
    }

    gui_remove_view_port(app->gui, app->view_port);
    furi_record_close(RECORD_GUI);
    furi_record_close(RECORD_NOTIFICATION);
    view_port_free(app->view_port);
    furi_message_queue_free(app->event_queue);
    free(app);

    return 0;
}
