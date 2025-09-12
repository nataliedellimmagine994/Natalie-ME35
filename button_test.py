from machine import Pin
import time

# Define button on GPIO pin (adjust pin number to your wiring)
button = Pin(34, Pin.IN, Pin.PULL_UP)  # assumes button pulls pin to GND when pressed

now = time.localtime()   # get full time tuple
print(now[5])

mode = 0

def handle_button(pin):
    print("Button pressed!")
    global mode
    if mode == 0:
        mode = 1
        time.sleep(0.1)
    else:
        mode = 0
        time.sleep(0.1)
        
    print(mode)

# Attach interrupt to trigger on falling edge (button press)
button.irq(trigger=Pin.IRQ_FALLING, handler=handle_button)

# Main loop doing other work
while True:
    print("Doing other work...")
    if mode == 0:
        print("time")
    else:
        print("api")
    time.sleep(1)
    
    