#include <util/delay.h>
#include <avr/pgmspace.h>
#include "main.h"
#include "messaging.h"
#include "serial.h"
#include "util.h"

#define ARDUINO_AVR_UNO
/**
 * This program reads and sends the value from pin A0 once every second.
 **/
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
    send_message_string("Arduino is ready to start sending sensor readings.");
    // Wait for start signal
    while (serial_read() != 's');
}

void loop() {
    timer_start();
    uint8_t reading = getSensorReading();
    uint8_t timer[2];
    int2bytes(timer_stop(), timer);
    send_message((uint8_t[]) {timer[0], timer[1], reading}, 3);
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
