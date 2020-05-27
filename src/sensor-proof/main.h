#ifndef MAIN_H
#define MAIN_H

#include "libs/aes128/aes.h"

/*
                    Message structure
+---------+-----------+------------+----------+--------+
| Timer   | AES nonce | HMAC nonce |   MAC    |  Data  |
+---------+-----------+------------+----------+--------+
| 2 bytes | 16 bytes  | 20 bytes   | 20 bytes | 1 byte |
+---------+-----------+------------+----------+--------+
The HMAC nonce, MAC and data are encrypted with AES in CBC mode
*/

#define MAC_NONCE_OFFSET 0
#define MAC_OFFSET 20
#define READING_OFFSET 40

typedef struct message_t {
    uint8_t timer[2];
    uint8_t aes_nonce[16];
    uint8_t encrypted_data[48];
} message_t;

// CPU Frequency aka Clock Speed
#undef F_CPU
#define F_CPU 16000000UL
#define BAUD 9600
// UBRR = USART Baud Rate Register
#define MYUBRR F_CPU/16/BAUD-1

int main();
void setup();
void loop();

void send_secure_reading(message_t *msg);
uint8_t getSensorReading();
void attestation(uint8_t *mac);

#endif