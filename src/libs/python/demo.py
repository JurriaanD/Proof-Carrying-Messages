import serial
from time import sleep

s = serial.Serial("/dev/ttyACM0", 9600)

while True:
    print(s.readline().decode(encoding="utf8").strip('\r\n'))
    sleep(0.1)
