#include <stdint.h>

void send_message_hex(uint8_t *data, uint8_t len);
void send_message_string(const char *msg);
void send_message_uint16(uint16_t i);
void send_message_int(int i);
void send_message(uint8_t *data, uint8_t len);
void send_insecure_message(uint8_t *data, uint8_t len);
void send_secure_message(uint8_t *data, uint8_t dataLen);