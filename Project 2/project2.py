from machine import Pin, I2C, PWM
import time
import math
# --------------------------
# Accelerometer (LIS3DHTR)
# --------------------------
i2c = I2C(0, scl=Pin(22), sda=Pin(21), freq=400000)
LIS3DH_ADDR = 0x19
def lis3dh_init():
    i2c.writeto_mem(LIS3DH_ADDR, 0x20, b’\x57')  # 100Hz, all axes enabled
    i2c.writeto_mem(LIS3DH_ADDR, 0x23, b’\x00')  # ±2g range
def lis3dh_read():
    data = i2c.readfrom_mem(LIS3DH_ADDR, 0x28 | 0x80, 6)
    x = int.from_bytes(data[0:2], ‘little’, True)
    y = int.from_bytes(data[2:4], ‘little’, True)
    z = int.from_bytes(data[4:6], ‘little’, True)
    return x, y, z
def get_tilt():
    x, y, z = lis3dh_read()
    return math.degrees(math.atan2(x, z))
lis3dh_init()
# --------------------------
# Motor setup
# --------------------------
MOTOR_PIN = 12
DIR_PIN = 13
MAX_SPEED = 300   # max PWM duty to prevent fast spinning
DEADZONE_SIZE = 5 # ± degrees around flat
motor_pwm = PWM(Pin(MOTOR_PIN), freq=1000)
motor_dir = Pin(DIR_PIN, Pin.OUT)
def motor_stop():
    motor_pwm.duty(0)      # stop motor
    motor_dir.value(0)      # set direction low
def motor_run(direction, speed):
    motor_dir.value(direction)
    motor_pwm.duty(speed)
# --------------------------
# Helper for data collection
# --------------------------
def collect_samples(duration=10):
    samples = []
    start = time.ticks_ms()
    while time.ticks_diff(time.ticks_ms(), start) < duration * 1000:
        tilt = get_tilt()
        samples.append(tilt)
        print(“Tilt:“, tilt)
        time.sleep(0.1)
    return sum(samples) / len(samples) if samples else 0
# --------------------------
# Calibration Mode
# --------------------------
print(“=== CALIBRATION MODE ===“)
input(“Press Enter when ready for DEADZONE (flat) measurement...“)
deadzone_center = collect_samples(10)
input(“Press Enter when ready for LEFT tilt measurement...“)
left_ref = collect_samples(10)
input(“Press Enter when ready for RIGHT tilt measurement...“)
right_ref = collect_samples(10)
print(“\nCalibration complete!“)
print(“Deadzone center = {:.1f}°“.format(deadzone_center))
print(“Left ref = {:.1f}°“.format(left_ref))
print(“Right ref = {:.1f}°“.format(right_ref))
input(“Press Enter to continue into playback mode...“)
# --------------------------
# Playback Mode
# --------------------------
print(“=== PLAYBACK MODE ===“)
try:
    while True:
        tilt = get_tilt()
        # Deadzone check
        if abs(tilt - deadzone_center) <= DEADZONE_SIZE:
            motor_stop()
            action = “Deadzone”
        # Tilt left closer to left_ref
        elif abs(tilt - left_ref) < abs(tilt - right_ref):
            motor_run(0, MAX_SPEED)
            action = “Left”
        # Tilt right closer to right_ref
        else:
            motor_run(1, MAX_SPEED)
            action = “Right”
        print(“Tilt: {:.1f}° | Action: {}“.format(tilt, action))
        time.sleep(0.1)
except KeyboardInterrupt:
    print(“\nStopping program...“)
finally:
    motor_stop()        # stop motor safely
    motor_pwm.deinit()  # release PWM on exit
    print(“Motor fully stopped :white_check_mark:”)
