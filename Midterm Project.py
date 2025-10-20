from machine import Pin, PWM
import neopixel
from encoder import Motor
import math
import time


#distance = input("Launch distance: ")

motor = Motor(12, 13, 32, 39)

launch = True
if_distance = False
if_launch = False

def determine_speed(x):
    speed = 4.147 * x + 34.259
    speed1 = 39.169 * math.exp(0.0621 * x)
    speed2 = 0.0174 * x**2 + 3.8749 * x + 35.137
    motor.setSpeed(0,speed)
    time.sleep(1)
    motor.stop()


print("Ping pong ball launcher. Range from 2-15 inches")

while launch:
    
    # Get a valid distance
    while True:
        try:
            distance = int(input("Launch distance (inches): "))
            if 2 <= distance <= 15:
                break  # valid input, exit loop
            else:
                print("Requested launch distance is not within the launcher range. Enter a new distance.")
        except ValueError:
            print("Please enter a valid integer.")

    print("Launching ping pong ball", distance, "inches")
    determine_speed(distance)
    time.sleep(2)

    # Ask if user wants to launch again
    while True:
        launch_again = input("Would you like to launch the ball again (Y/N)? ").strip().upper()
        if launch_again == "N":
            launch = False
            break
        elif launch_again == "Y":
            break  # launch stays True, continue outer loop
        else:
            print("Invalid input, please input 'Y' or 'N'.")

print("Thank you for launching the ping pong ball")
    
        


