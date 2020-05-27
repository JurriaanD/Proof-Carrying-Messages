#include <stdint.h>
#include <stdlib.h>
#include <avr/interrupt.h>

void nibbleToHex(uint8_t nib, uint8_t *dest) {
    //*dest = nib < 10 ? nib + '0' : nib - 10 + 'a';
    if (nib < 10) {
        *dest = nib + '0';
    } else {
        *dest = nib - 10 + 'a';
    }
}

void bytesToHex(uint8_t *inp, int len, uint8_t *dest) {
    for (int i = 0; i < len; i++) {
        unsigned char c = inp[i];
        unsigned int low = c & 0xF;
        unsigned int high = c >> 4;
        nibbleToHex(high, dest + 2 * i + 0);
        nibbleToHex(low, dest + 2 * i + 1);
    }
}

// Big endian
void int2bytes(uint16_t in, uint8_t bytes[2]) {
    bytes[0] = in >> 8;
    bytes[1] = in & 0xFF;
}

uint16_t bytes2int(uint8_t *bytes) {
    return (bytes[0] << 8) + bytes[1];
}

/*  RNG() function.
Random number generator function.    
    Inputs: 
        size    - The size of the random data required.
        
    Outputs:
        dest    - The randomly generated data.

Note:   The RNG implemented here is only of demonstrative purposes.
        For use in cryptographic operations, this would have to be implemented
        using some inherently random input (e.g. noise). 
*/
uint8_t RNG(uint8_t *dest, unsigned size) {
    while(size){
        uint8_t val = (uint8_t) rand() + rand();
        *dest = val;
        ++dest;
        --size;
    }
    return 1;
}

static uint16_t timer_ticks;

void timer_init() {
    /* Set the Timer Mode to CTC */
    TCCR0A |= (1 << WGM01);
    /* OCRn =  [ (clock_speed / Prescaler_value) * Desired_time_in_Seconds ] - 1
       Set timer for 1 ms */
    OCR0A = 249;
    /* Enable interrupts */
    sei();
    /* Enable timer interrupts */
    TIMSK0 |= 1 << OCIE0A;
}

void timer_start() {
    timer_ticks = 0;
    /* Set prescaler to 64 and start timer*/
    TCCR0B |= (1 << CS01) | (1 << CS00);
}

uint16_t timer_elapsed() {
    return timer_ticks;
}

uint16_t timer_stop() {
    /* Stop timer */
    TCCR0B &= ~((1 << CS01) | (1 << CS00));
    return timer_ticks;
}

ISR (TIMER0_COMPA_vect) {
    timer_ticks++;
}