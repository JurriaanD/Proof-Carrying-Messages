#include <util/delay.h>
#include <avr/pgmspace.h>
#include <avr/interrupt.h>
#include <string.h>
#include <stdio.h>
#include "main.h"
#include "messaging.h"
#include "serial.h"
#include "util.h"

#define ARDUINO_AVR_UNO
#define MEM_UPPER_BOUND 30720

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
    send_message_string("Arduino is ready for secure sensor readings.");
    // Wait for start signal
    while (serial_read() != 's');
}

void loop() {
    timer_start();
    message_t msg;

    msg.xor = calculateXOR();

    // Send back a 16 bit timer reading expressing the elapsed time in ms
    int2bytes(timer_stop(), msg.timer);
    send_message((uint8_t*) &msg, sizeof(msg));
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

uint8_t calculateXOR() {
    uint8_t i;
    uint8_t result;
    uint16_t offset;
    uint8_t buf[SPM_PAGESIZE];
    uint8_t xor[SPM_PAGESIZE];

    // Read the first page into the xor result array
    read_page(xor, 0);

    // XOR all the other pages
    offset = SPM_PAGESIZE;
    while (offset < MEM_UPPER_BOUND) {
        // Read page into buffer
        read_page(buf, offset);
        // XOR buffer with intermediate result
        for (i = 0; i < SPM_PAGESIZE; ++i) {
            xor[i] ^= buf[i];
        }
        offset += SPM_PAGESIZE;
    }

    // Reduce the xor array to a single value
    result = 0;
    for (i = 0; i < SPM_PAGESIZE; ++i) {
        result ^= xor[i];
    }

    return result;
}
