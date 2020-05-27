#include <stdio.h>
#include <string.h>
#include "messaging.h"
#include "util.h"
#include "serial.h"

void send_message_hex(uint8_t *data, uint8_t len) {
    uint8_t hexHash[2 * len];
    bytesToHex(data, len, hexHash);
    send_message(hexHash, 2 * len);
}

void send_message_string(const char *msg) {
    uint16_t strlen = -1;
    while (msg[++strlen] != 0);
    send_message((uint8_t*) msg, strlen);
}

void send_message(uint8_t *data, uint8_t len) {
    uint8_t len_B[2];
    int2bytes(len, len_B);
    serial_write_bytes(len_B, 2);
    serial_write_bytes(data, len);
}
