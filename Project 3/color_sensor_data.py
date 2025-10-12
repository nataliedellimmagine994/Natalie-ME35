import machine
import time
from machine import SoftI2C, Pin
from veml6040 import VEML6040

try:
    i2c = SoftI2C(scl=Pin(22), sda=Pin(21), freq=100000) #Check for I2C pins from pinouts
    print("I2C initialized successfully.")
except Exception as e:
    print(f"Error initializing I2C: {e}")
    exit()


try:
    sensor = VEML6040(i2c)
    print("VEML6040 sensor object created.")
except Exception as e:
    print(f"Error creating VEML6040 object: {e}")
    exit()
    
IT_40MS = (0b000 << 4) # 40 ms
sensor.set_integration_time(IT_40MS)

def color_sensor():
    try:
        sensor.trigger_measurement()
        red, green, blue, white = sensor.read_rgbw()
        #print(f"Red: {red}, Green: {green}, Blue: {blue}, White: {white}")
        r = red
        g = green
        b = blue
        w = white
        return [r, g, b, w]
    except OSError as e:
        if e.args[0] == 19: # errno 19 is ENODEV (No such device)
            print("I2C Error: VEML6040 not responding. Check wiring.")
        else:
            print(f"I2C Read Error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    
new_value = [0, 0, 0, 0]
running_total = [0, 0, 0, 0]
average = [0, 0, 0, 0]
averages_total = [0, 0, 0, 0]
final_answer = [0, 0, 0, 0]


for i in range(20):
    new_value = color_sensor()
    running_total[0] += new_value[0] 
    running_total[1] += new_value[1]
    running_total[2] += new_value[2]
    running_total[3] += new_value[3]
    
average[0] = running_total[0] / 20
average[1] = running_total[1] / 20
average[2] = running_total[2] / 20
average[3] = running_total[3] / 20
    
print(average)
    



