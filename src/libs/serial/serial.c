// http://ww1.microchip.com/downloads/en/DeviceDoc/Atmel-7810-Automotive-Microcontrollers-ATmega328P_Datasheet.pdf
// https://github.com/jsoloPDX/Inductive-Proximity-MIDI-Controller-PSU-Capstone-Project-11/wiki/Serial-Communication-Using-ATMEGA328
// UART = Universal Asynchronous Receiver/Transmitter

#include <avr/io.h>
#include <avr/interrupt.h>
#include <stdlib.h>
#include <util/delay.h>
#include "LightweightRingBuff.h"
#include "serial.h"

// Right now all of our I/O is blocking, might want to look at buffering & interrupts if this is problematic
static RingBuff_t *rxbuf;

void serial_init(unsigned int ubrr) {
	/*
	Set baud rate
	UBRR0H contains the 4 most significant bits of the
	baud rate. UBRR0L contains the 8 least significant
	bits. The microcontroller uses little-endian.
	*/  
	UBRR0H = (unsigned char)(ubrr>>8);
	UBRR0L = (unsigned char)ubrr;	

	// Enable sending data (transmitter) and receiving data (receiver)
	// See page 160 in the datasheet
	// TXEN0 and RXEN0 tell us which bits we need to set to 1
	UCSR0B = (1<<TXEN0) | (1<<RXEN0);

	// Enable interrupt on receiving data
	UCSR0B |= (1<<RXCIE0);
	// Create ring buffer for received data
	rxbuf = malloc(sizeof(RingBuff_t));
	RingBuffer_InitBuffer(rxbuf);
	
	/* Set frame format: 2 stop bit (???) and 8 bits/char */
	UCSR0C = (1<<USBS0) | (3<<UCSZ00);

	// Enable global interrupts
	sei();
}

// Data received interrupt vector
ISR(USART_RX_vect) {
	uint8_t data = UDR0;
	RingBuffer_Insert(rxbuf, data);
}

// Returns true if the receiver buffer is not empty
uint8_t serial_can_read() {
    return !RingBuffer_IsEmpty(rxbuf);
}

uint8_t serial_available() {
	return RingBuffer_GetCount(rxbuf);
}

// Reads a single byte
uint8_t serial_read() {
	while (!serial_can_read());
    return RingBuffer_Remove(rxbuf);
}

// Reads bytes into the given buffer
void serial_read_bytes(uint8_t *data, uint8_t length) {
	int i;
	for (i = 0; i < length; ++i) {
		while (!serial_can_read());
		data[i] = RingBuffer_Remove(rxbuf);
	}
}

// Returns true if the transmitter buffer is empty
uint8_t serial_can_write() {
	return UCSR0A & (1<<UDRE0);
}

// Writes a single byte
void serial_write(uint8_t data) {
	while (!serial_can_write());
	
	UDR0 = data;
}

// Writes bytes from the buffer to the transmitter buffer
void serial_write_bytes(uint8_t *data, uint16_t length) {
	int i;
	for (i = 0; i < length; ++i) {
		while (!serial_can_write());
		UDR0 = data[i];
	}
}

// Writes the given string to the transmitter buffer
void serial_write_string(char *str) {
	while (*str) {
		while (!serial_can_write());
		UDR0 = *str;
	}
}