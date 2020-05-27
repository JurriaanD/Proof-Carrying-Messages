#ifndef MAIN_H
#define MAIN_H

#include "aes.h"

// CPU Frequency aka Clock Speed
#undef F_CPU
#define F_CPU 16000000UL
#define BAUD 9600
// UBRR = USART Baud Rate Register
#define MYUBRR F_CPU/16/BAUD-1

typedef struct message_t {
    uint8_t timer[2];
    uint8_t aes_nonce[16];
    uint8_t encrypted_data[16];
} message_t;

int main();
void setup();
void loop();

void send_secure_reading(message_t *msg);
uint8_t getSensorReading();

#endif