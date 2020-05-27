void nibbleToHex(uint8_t nib, uint8_t *dest);
void bytesToHex(uint8_t *inp, int len, uint8_t *dest);
void int2bytes(uint16_t in, uint8_t bytes[2]);
uint16_t bytes2int(uint8_t *bytes);

uint8_t RNG(uint8_t *dest, unsigned size);

void timer_init();
void timer_start();
uint16_t timer_elapsed();
uint16_t timer_stop();