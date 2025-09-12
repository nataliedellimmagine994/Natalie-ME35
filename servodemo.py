from machine import Pin, PWM
import time
import servo

# Set up servo on a specific pin
servo_pin = 15  # Change this to your ESP32 GPIO pin connected to the servo
servo = PWM(Pin(servo_pin))
servo.freq(50)  # Standard servo frequency is 50Hz

servo.duty_ns(500*1000)
time.sleep(1)
servo.duty_u16(int(1.5*65535/20))
time.sleep(1)
servo.duty(100)

