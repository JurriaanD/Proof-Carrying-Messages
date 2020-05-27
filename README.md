# Running an application
- Navigate to the application folder under `src/`
- Run `make`
- Setup your programmer of choice and an Arduino Uno
- Run `make flash`. You might have to edit the `Makefile` in the application folder to make it work with your programmer
- Run `python verifier.py` to start the application on the arduino.

# Dependencies
The verifiers are written in Python 3 and have some dependencies. To install these, go to `src/libs/python` and run `pip install -r requirements.txt`.
