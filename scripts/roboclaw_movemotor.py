# A short and sweet script to test movement of a single roboclaw motor channel
#   $ python roboclaw_movemotor.py 130

from time import sleep
import sys
from os import path

# need to add the roboclaw.py file in the path
sys.path.append(path.join(path.expanduser('~'), 'osr_ws/src/osr-rover-code/ROS/osr_control/osr_control'))
from roboclaw import Roboclaw

BAUD_RATE = 115200

def test_connection(address):
    """
    Test connection to Roboclaw controllers and return the connected Roboclaw object.

    :param address: The address of the Roboclaw device.
    :return: Roboclaw object if connected, otherwise None.
    """
    roboclaw0 = Roboclaw("/dev/serial0", BAUD_RATE)
    roboclaw1 = Roboclaw("/dev/serial1", BAUD_RATE)
    connected0 = roboclaw0.Open() == 1
    connected1 = roboclaw1.Open() == 1
    
    if connected0:
        print("Connected to /dev/serial0.")
        print(f"version: {roboclaw0.ReadVersion(address)}")
        print(f"encoders: {roboclaw0.ReadEncM1(address)}")
        return roboclaw0
    elif connected1:
        print("Connected to /dev/serial1.")
        print(f"version: {roboclaw1.ReadVersion(address)}")
        print(f"encoders: {roboclaw1.ReadEncM1(address)}")
        return roboclaw1
    else:
        print("Could not open comport /dev/serial0 or /dev/serial1. Ensure correct permissions and availability.")
        return None

def move_motor(rc, address, motor_id, drive_accel, target_qpps):
    """
    Move the specified motor at increasing speeds.

    :param rc: The connected Roboclaw object.
    :param address: The address of the Roboclaw device.
    :param motor_id: Motor identifier (1 for M1, 2 for M2).
    :param drive_accel: Acceleration rate for the motor.
    :param target_qpps: Target speed in QPPS (quadrature pulses per second).
    """
    print(f"Moving Motor {motor_id}:")
    for speed_cmd in range(10, target_qpps, 10):
        if motor_id == 1:
            rc.SpeedAccelM1(address, drive_accel, speed_cmd)
            speed = rc.ReadSpeedM1(address)
        else:
            rc.SpeedAccelM2(address, drive_accel, speed_cmd)
            speed = rc.ReadSpeedM2(address)
        
        if speed[0]:
            print(f'speed: {speed[1]}')
        else:
            print(f"Error reading speed for Motor {motor_id}")
        sleep(0.5)
    
    sleep(1)
    
    # Stop the motor
    if motor_id == 1:
        rc.ForwardM1(address, 0)
    else:
        rc.ForwardM2(address, 0)
    print(f"Motor {motor_id} stopped.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python roboclaw_movemotor.py <address>")
        sys.exit(1)

    address = int(sys.argv[1]) 

    # Test connection to Roboclaw
    rc = test_connection(address)
    
    if rc is None:
        sys.exit(1)
    
    # Set acceleration and speed parameters
    accel_max = 2**15 - 1
    accel_rate = 0.5
    drive_accel = int(accel_max * accel_rate)
    drive_accel = 100  # Slow acceleration for safety

    roboclaw_overflow = 2**15 - 1  # 32767 max speed
    target_qpps = 100  # Slow speed for testing

    # Move Motor M1
    move_motor(rc, address, 1, drive_accel, target_qpps)
    
    # Move Motor M2
    move_motor(rc, address, 2, drive_accel, target_qpps)
