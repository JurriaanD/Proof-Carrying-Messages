#include <util/delay.h>
#include <avr/pgmspace.h>
#include <string.h>
#include "main.h"
#include "messaging.h"
#include "serial.h"
#include "util.h"
#include "aes.h"

#define ARDUINO_AVR_UNO

#define AES_BLOCK_SIZE 16
#define AES_NONCE_LENGTH_BYTES AES_BLOCK_SIZE

uint8_t aes_key[] = {0x39, 0x79, 0x24, 0x42, 0x26, 0x45, 0x29, 0x48, 0x40, 0x4D, 0x63, 0x51, 0x66, 0x54, 0x6A, 0x57};

int main() {
	setup();
	while(1) {
		loop();
		_delay_ms(1000);
	}
}

void setup() {
    serial_init(MYUBRR);
    timer_init();
    /* Configure the ADC  = Analog Digital Conversion (used to get a pin reading) */
    // Set ADc ENable bit
    ADCSRA |= 1 << ADEN;
    // Configure ADC MUltipleXer
    ADMUX |= 1 << ADLAR;
    send_message_string("Arduino is ready to start sending encrypted sensor readings.");
    // Wait for start signal
    while (serial_read() != 's');
}

void loop() {
    timer_start();
    message_t msg;

    // Get a sensor reading
    msg.encrypted_data[0] = getSensorReading();

    // Pad the data we're going to encrypt to a multiple of the block size
    for (uint8_t i = 1; i < 16; i++) {
        msg.encrypted_data[i] = 15;
    }

    // Generate a nonce for AES CBC
    RNG(msg.aes_nonce, AES_NONCE_LENGTH_BYTES);

    // Add a timer reading and send the message
    int2bytes(timer_stop(), msg.timer);
    send_secure_reading(&msg);
}

void send_secure_reading(message_t *msg) {
    const int NB_BLOCKS = 1;

    uint8_t *nonce = msg->aes_nonce;

    aes128_ctx_t ctx;
    aes128_init(&aes_key, &ctx);
    for (int i = 0; i < NB_BLOCKS; i++) {
        for (int j = 0; j < AES_BLOCK_SIZE; j++) {
            msg->encrypted_data[i * AES_BLOCK_SIZE + j] ^= nonce[j];
        }
        aes128_enc(msg->encrypted_data + i * AES_BLOCK_SIZE, &ctx);
        nonce = msg->encrypted_data + i * AES_BLOCK_SIZE;
    }

    send_message((uint8_t *) msg, sizeof(message_t));
}

uint8_t getSensorReading() {
    /* Select A0 input */
    ADMUX &= 0xf0;
    /* Start getting & converting reading */
    ADCSRA |= 1 << ADSC;
    /* Wait for conversion to finish
    ADSC is set to 0 when the conversion is done */
    while (ADCSRA & (1 << ADSC));
    return ADCH;
}
