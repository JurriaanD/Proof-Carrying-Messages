#ifndef MAIN_H
#define MAIN_H

typedef struct message_t {
    uint8_t timer[2];
    uint8_t xor;
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

void read_page(uint8_t *block_buf, uint32_t offset);
uint8_t calculateXOR();

#endif