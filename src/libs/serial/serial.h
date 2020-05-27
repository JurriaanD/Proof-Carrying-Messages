void serial_init(unsigned int ubrr);

uint8_t serial_can_read();
uint8_t serial_available();
unsigned char serial_read();
void serial_read_bytes(uint8_t *data, uint8_t length);

uint8_t serial_can_write();
void serial_write(unsigned char data);
void serial_write_bytes(uint8_t *data, uint16_t length);
void serial_write_string(char *str);