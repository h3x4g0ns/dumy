import _thread
from machine import Pin, UART, Servo, PWM
import time

# Constants
L1_PORT = 10
L2_PORT = 11
L3_PORT = 12
PIEZO_PIN = 13  # TODO: Replace with the actual pin number for the piezo buzzer
OFFSET = 90

# Global variables
piezo_flag = False
piezo_lock = _thread.allocate_lock()  # Create a lock for the piezo_flag variable

# Initialize Servo objects
l1 = Servo(Pin(L1_PORT))
l2 = Servo(Pin(L2_PORT))
l3 = Servo(Pin(L3_PORT))
piezo = PWM(Pin(PIEZO_PIN))

# Function to parse into from serial in
def to_int(src, size):
    try:
        return int(src[:size])
    except ValueError:
        return 0

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
            angles = [to_int(data_str[0], 5) + OFFSET,
                      to_int(data_str[1], 5) + OFFSET,
                      to_int(data_str[2], 5) + OFFSET]

            if angles[0] == 0 and angles[1] == 0 and angles[2] == 0:
                # trigger piezo buzzer
                with piezo_lock:
                    piezo_flag = True
            else:
                l1.angle(angles[0])
                l2.angle(angles[1])
                l3.angle(angles[2])

            terminated = False

# Piezo buzzer control function
def piezo_control():
    while True:
        # check if the piezo buzzer is triggered
        if piezo_flag:
            for i in range(50):
                piezo.freq(1500)  # Set frequency (e.g., A4 note)
                piezo.duty(50)   # Set duty cycle (volume)
                time.sleep(0.2)  # Play for 0.2 seconds
                piezo.freq(1000)  
                piezo.duty(75)
                time.sleep(0.2)
                piezo.freq(1200)
                piezo.duty(60)
                time.sleep(0.2)
                piezo.duty(0)    # Turn off the buzzer
                time.sleep(0.5)  # Pause for 0.2 seconds

            # acquire lock and rezet flag
            with piezo_lock:
                piezo_flag = False

# Start the servo control thread on core 0
_thread.start_new_thread(servo_control, ())

# Start the piezo control thread on core 1
_thread.start_new_thread(piezo_control, ())
