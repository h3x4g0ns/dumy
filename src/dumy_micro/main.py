import _thread
from machine import Pin, UART, Servo

# Constants
L1_PORT = 10
L2_PORT = 11
L3_PORT = 12
OFFSET = 90.0

# Initialize Servo objects
l1 = Servo(Pin(L1_PORT))
l2 = Servo(Pin(L2_PORT))
l3 = Servo(Pin(L3_PORT))

# Function to parse float from string
def strlfcopy(src, size):
    try:
        return float(src[:size])
    except ValueError:
        return 0.0

# Servo control function
def servo_control():
    # Setup UART for serial communication
    uart = UART(1, baudrate=9600)

    terminated = False
    data = bytearray(16)
    i = 0

    while True:
        if uart.any():
            incoming = uart.read(1)
            if incoming == b'r':
                terminated = True
                i = 0
            else:
                data[i] = incoming[0]
                i += 1

        if terminated:
            data_str = data.decode('utf-8').split(',')
            angles = [strlfcopy(data_str[0], 5) + OFFSET,
                      strlfcopy(data_str[1], 5) + OFFSET,
                      strlfcopy(data_str[2], 5) + OFFSET]

            l1.angle(angles[0])
            l2.angle(angles[1])
            l3.angle(angles[2])

            data = bytearray(16)
            terminated = False

# Start the servo control thread on core 0
_thread.start_new_thread(servo_control, ())

# You can add your piezo control code for core 1 here
