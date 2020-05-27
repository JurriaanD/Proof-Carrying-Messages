import serial.tools.list_ports

def getPorts():
    """ Returns a list of all serial communication ports which are in use """
    return [x.device for x in serial.tools.list_ports.comports()]

if __name__ == "__main__":
    print(f"Connected COM ports: {getPorts()}")
