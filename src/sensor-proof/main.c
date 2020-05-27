#include <util/delay.h>
#include <avr/pgmspace.h>
#include <avr/interrupt.h>
#include <string.h>
#include <stdio.h>
#include "main.h"
#include "messaging.h"
#include "serial.h"
#include "util.h"
#include "aes.h"
#include "hmac-sha1.h"

#define ARDUINO_AVR_UNO
#define MEM_UPPER_BOUND 30720

#define AES_BLOCK_SIZE 16
#define AES_NONCE_LENGTH_BYTES AES_BLOCK_SIZE

#define MAC_LENGTH_BITS 160
#define MAC_LENGTH_BYTES MAC_LENGTH_BITS/8
#define MAC_NONCE_LENGTH_BYTES MAC_LENGTH_BYTES

#define BENCHMARK 1

uint8_t aes_key[] = {0x39, 0x79, 0x24, 0x42, 0x26, 0x45, 0x29, 0x48, 0x40, 0x4D, 0x63, 0x51, 0x66, 0x54, 0x6A, 0x57};
uint8_t hmac_key[] = {0x93, 0x79, 0x24, 0x42, 0x26, 0x45, 0x29, 0x48, 0x40, 0x4D, 0x63, 0x51, 0x66, 0x54, 0x6A, 0x57, 0xff, 0xff, 0xff, 0xff};

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
    send_message_string("Arduino is ready to start sending proof-carrying sensor readings.");
    // Wait for start signal
    while (serial_read() != 's');
}

void loop() {
    timer_start();
    message_t msg;

    // Generate the nonce for the HMAC
    RNG(msg.encrypted_data, MAC_NONCE_LENGTH_BYTES);

    // We use the nonce for the first block of the HMAC
    memcpy(msg.encrypted_data + MAC_OFFSET, msg.encrypted_data, MAC_NONCE_LENGTH_BYTES);
    attestation(msg.encrypted_data + MAC_OFFSET);

    // Get a sensor reading
    msg.encrypted_data[READING_OFFSET] = getSensorReading();

    // Pad the data we're going to encrypt to a multiple of the block size
    uint8_t padding = 48 - READING_OFFSET - 1;
    for (uint8_t i = READING_OFFSET + 1; i < 48; i++) {
        msg.encrypted_data[i] = padding;
    }

    // Generate a nonce for AES CBC
    RNG(msg.aes_nonce, AES_NONCE_LENGTH_BYTES);

    // Add a timer reading and send the message
#if BENCHMARK
    int2bytes(timer_stop(), msg.timer);
#else
    msg.timer[0] = 0;
    msg.timer[1] = 0;
#endif
    send_secure_reading(&msg);
}

void send_secure_reading(message_t *msg) {
    const int NB_BLOCKS = 3;

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

void load_key(uint8_t *buff, uint8_t *secret) {
    uint16_t i;
    /* Read page byte at a time at a time */
    for(i=0; i < 20; i++) {
        buff[i] = secret[i];
    }
}

/* Reads arbitrary page from progmem */
void read_page(uint8_t *block_buf, uint32_t offset) {
    uint16_t i;
    /* Read page byte at a time at a time */
    for(i=0; i < SPM_PAGESIZE; i++) {
        block_buf[i] = pgm_read_byte_near(offset);
        offset += 1;
    }
}

void attestation(uint8_t *mac) {
#if BENCHMARK == 0
    uint8_t sreg;
    sreg = SREG;
    cli();
#endif

    hmac_sha1_ctx_t ctx;
    uint8_t buf[SPM_PAGESIZE];
    uint32_t offset;
    
    /* Init hmac context with key (load 20 byte key temporary in buff) */
    load_key(buf, hmac_key);
    hmac_sha1_init(&ctx, buf, 160);

    /* Hash full image */
    offset = 0x00;
    while (offset < MEM_UPPER_BOUND) {
        read_page(buf, offset);
        /* Run block through HMAC, unroll loop */
        hmac_sha1_nextBlock(&ctx, buf);
        hmac_sha1_nextBlock(&ctx, buf + HMAC_SHA1_BLOCK_BYTES);
        /* Increment counter */
        offset += SPM_PAGESIZE;
    }

    /* Hash nonce */
    hmac_sha1_lastBlock(&ctx, mac, 160);

    /* Finalize */
    hmac_sha1_final(mac, &ctx);

#if BENCHMARK == 0
    SREG = sreg;
#endif
}
