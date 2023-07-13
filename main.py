import board
import busio

# Set up the serial connection
uart = busio.UART(board.USB, 9600)  # Use the appropriate UART interface

# Read the integer value sent from the computer
while True:
    if uart.in_waiting > 0:
        value = uart.read(1)[0]  # Read a single byte
        print("Received value:", value)
