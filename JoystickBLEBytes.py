'''
Bluetooth Joystick for RC Defensive Soccer Robot
ME 35 Final: Football
Written by Natalie Dell'Immagine
Sample code from Professor Milan Dahal
'''

from BLE_CEEO import Yell, Listen
import time
import json
from machine import ADC, Pin

count = 0
vrx = ADC(Pin(33)) # Joystick X
vry = ADC(Pin(34)) # Joystick Y
sw = Pin(5, Pin.IN, Pin.PULL_DOWN) # Joystick Button
open_gate = 0
#json_data = b'\x00\x00\x00'#{"g": open_gate, "d": 0, "t": 0} # first byte is gate, second is turn and third is drive
last_press = 0

def callback(data):
    print(data.decode())
        
def peripheral(name): 
    global p
    try:
        p = Yell(name, interval_us=30000, verbose = True)
        if p.connect_up():
            p.callback = callback
            print('Connected')
            time.sleep(1)
            
            while p.is_connected:
                message = collectData()
                print(message)
                sendMessage(message)
                time.sleep(.1)
        print('lost connection')
    except Exception as e:
        print('Error: ',e)
    finally:
        p.disconnect()
        print('closing up')
        
def sendMessage(message):
    #payload = str(json.dumps(message))
    p.send(message)
    print("sent message")

def collectData():
    global vrx, vry, sw, open_gate, last_press
    
    # get values from joystick
    x = vrx.read_u16()
    y = vry.read_u16()
    button = sw.value()
      
    
    if button == 0:
        now = time.ticks_ms()

        # debounce for 500 ms
        if time.ticks_diff(now, last_press) < 500:
            return bytes([open_gate, turn_data, drive_data])

        last_press = now  # update timestamp

        # toggle gate
        open_gate = not open_gate
        
    
    # update motors based on joystick x and y position
    if x > 60000:
        # turn right
        turn_data = 1
        #json_data["t"] = 1
    elif x == 0:
        turn_data = 2
        # turn left
        #json_data["t"] = -1
    else:
        turn_data = 0
        
    if y == 0:
        drive_data = 1
        # drive forward
        #json_data["d"] = 1
    elif y > 60000:
        # reverse
        drive_data = 2
        #json_data["d"] = -1
    else:
        # stop
        drive_data = 0
        #json_data["t"] = 0
        #json_data["d"] = 0
    
    return bytes([open_gate, turn_data, drive_data]) #json_data
         
peripheral('Natalie')