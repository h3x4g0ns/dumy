import _thread
from machine import Pin, UART, PWM

# Constants
L1_PORT = 10
L2_PORT = 11
L3_PORT = 12
OFFSET = 90

# Function to parse into from serial in
def to_int(src, size):
    try:
        return int(src[:size])
    except ValueError:
        return 0

#clamps the input value, which can range between inmin and inmax, between outmin and outmax.
def clampPWM(i, inMin, inMax, outMin, outMax):
    return max(min((i - inMin)*(outMax - outMin)//(inMax-inMin) + outMin, outMax), outMin)

# Servo control function
def servo_control():
    # Setup UART for serial communication
    uart = UART(1, baudrate=9600)

    #set up PWM pins
    l1 = PWM(L1_PORT, freq=50, duty_ns=0)
    l2 = PWM(L2_PORT, freq=50, duty_ns=0)
    l3 = PWM(L3_PORT, freq=50, duty_ns=0)

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
            angles = [clampPWM(data_str[0], -90, 90, 0, 65535),
                      clampPWM(data_str[1], -90, 90, 0, 65535),
                      clampPWM(data_str[2], -90, 90, 0, 65535)]

            l1.duty_u16(angles[0])
            l2.duty_u16(angles[1])
            l3.duty_u16(angles[2])
            
            terminated = False

# Start the servo control thread on core 0
_thread.start_new_thread(servo_control, ())

# TODO: piezo buzzer control
# add your piezo control code for core 1 here
