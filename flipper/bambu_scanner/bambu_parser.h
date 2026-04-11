// Bambu Lab NFC Parser - Core Parsing Logic
// Source: https://github.com/uzyn/flipper-bambu
//
// This header contains the portable parsing functions shared between
// the Flipper Zero plugin and the test suite.

#ifndef BAMBU_PARSER_H
#define BAMBU_PARSER_H

#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>
#include <string.h>

// Block layout for Bambu Lab spool RFID tags (Mifare Classic 1K)
#define BLOCK_MATERIAL_IDS      1   // Variant ID (bytes 0-6) + Material ID "GFxxx" (bytes 8-13)
#define BLOCK_FILAMENT_TYPE     2   // Filament type ASCII (PLA, PETG, ABS...)
#define BLOCK_DETAILED_TYPE     4   // Detailed type ASCII (PLA Basic, PLA Matte...)
#define BLOCK_COLOR_WEIGHT      5   // RGBA (bytes 0-3), weight g (bytes 4-5 LE), diameter mm (bytes 8-11 LE float)
#define BLOCK_TEMPERATURES      6   // Drying temp (0-1), hours (2-3), hotend max (8-9), min (10-11)
#define BLOCK_NOZZLE            8   // Nozzle diameter float (bytes 12-15)
#define BLOCK_SPOOL_WIDTH      10   // Spool width mm*100 uint16 (bytes 4-5)
#define BLOCK_PRODUCTION_DATE  12   // Production date ASCII YYYY_MM_DD_HH_MM
#define BLOCK_FILAMENT_LENGTH  14   // Filament length meters uint16 (bytes 4-5)

// Helper: Read little-endian uint16
static inline uint16_t bambu_read_le16(const uint8_t* data) {
    return (uint16_t)(data[0] | (data[1] << 8));
}

// Helper: Read little-endian uint32 as float (IEEE 754)
static inline float bambu_read_le_float(const uint8_t* data) {
    union { uint32_t u; float f; } val;
    val.u = (uint32_t)(data[0] | (data[1] << 8) | (data[2] << 16) | (data[3] << 24));
    return val.f;
}

// Helper: Check if block contains printable ASCII (null padding allowed)
static inline bool bambu_is_printable_ascii(const uint8_t* data, size_t len) {
    bool found = false;
    for(size_t i = 0; i < len; i++) {
        if(data[i] == 0) continue;
        if(data[i] < 0x20 || data[i] > 0x7E) return false;
        found = true;
    }
    return found;
}

// Helper: Copy null-terminated ASCII string from block data
static inline void bambu_copy_ascii_string(char* dest, const uint8_t* src, size_t max_len) {
    size_t i;
    for(i = 0; i < max_len && src[i] != 0 && src[i] >= 0x20 && src[i] <= 0x7E; i++) {
        dest[i] = (char)src[i];
    }
    dest[i] = '\0';
}

// Known filament types for validation
static const char* const BAMBU_KNOWN_FILAMENT_TYPES[] = {
    "PLA", "PETG", "ABS", "TPU", "PA", "PC", "ASA", "PVA", "HIPS", "PET"
};
#define BAMBU_NUM_FILAMENT_TYPES (sizeof(BAMBU_KNOWN_FILAMENT_TYPES) / sizeof(BAMBU_KNOWN_FILAMENT_TYPES[0]))

// Validation: returns true only if this looks like a Bambu Lab spool tag
static inline bool bambu_tag_is_valid(const MfClassicData* data) {
    if(data->type != MfClassicType1k) return false;

    // Block 1 bytes 8-9 must be "GF"
    const uint8_t* block1 = data->block[BLOCK_MATERIAL_IDS].data;
    if(block1[8] != 'G' || block1[9] != 'F') return false;

    // Block 2 must start with a known filament type
    const uint8_t* block2 = data->block[BLOCK_FILAMENT_TYPE].data;
    bool valid_type = false;
    for(size_t i = 0; i < BAMBU_NUM_FILAMENT_TYPES; i++) {
        size_t len = strlen(BAMBU_KNOWN_FILAMENT_TYPES[i]);
        if(memcmp(block2, BAMBU_KNOWN_FILAMENT_TYPES[i], len) == 0) {
            valid_type = true;
            break;
        }
    }
    if(!valid_type) return false;

    // Block 4 must be printable ASCII
    if(!bambu_is_printable_ascii(data->block[BLOCK_DETAILED_TYPE].data, 16)) return false;

    // Block 5 bytes 8-11: diameter must be 1.6-2.0 mm or 2.7-3.0 mm
    float diameter = bambu_read_le_float(&data->block[BLOCK_COLOR_WEIGHT].data[8]);
    if(!((diameter >= 1.6f && diameter <= 2.0f) || (diameter >= 2.7f && diameter <= 3.0f))) return false;

    return true;
}

#endif // BAMBU_PARSER_H
