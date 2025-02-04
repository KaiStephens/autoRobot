import serial
import time
import numpy as np
import cv2
import math

# Motor commands
FORWARD = "f"
BACK    = "b"
LEFT    = "l"
RIGHT   = "r"
STOP    = "s"

def move(direction, esp32):
    """Send the appropriate motor commands to ESP32."""
    print(direction)
    if esp32 is None:
        print(f"Simulating move: {direction}")
        return
    try:
        if direction == FORWARD:
            esp32.write(b"motor1/forward\nmotor2/forward\n")
        elif direction == BACK:
            esp32.write(b"motor1/reverse\nmotor2/reverse\n")
        elif direction == LEFT:
            esp32.write(b"motor1/forward\nmotor2/reverse\n")
        elif direction == RIGHT:
            esp32.write(b"motor2/forward\nmotor1/reverse\n")
        elif direction == STOP:
            esp32.write(b"motor1/brake\nmotor2/brake\n")
    except Exception as e:
        print(f"Error sending command: {e}")

def calculate_relative_angle(position1, behind_position1, position2):
    # Calculate the orientation vector of the first object
    orientation_vector = (position1[0] - behind_position1[0], position1[1] - behind_position1[1])
    
    # Calculate the vector from the first object to the second object
    to_second_object_vector = (position2[0] - position1[0], position2[1] - position1[1])

    # Calculate angles of the vectors relative to the x-axis
    orientation_angle = math.atan2(orientation_vector[1], orientation_vector[0])
    to_second_object_angle = math.atan2(to_second_object_vector[1], to_second_object_vector[0])

    # Compute the relative angle
    relative_angle = math.degrees(to_second_object_angle - orientation_angle)

    # Normalize the angle to the range [-180, 180]
    relative_angle = (relative_angle + 180) % 360 - 180

    return relative_angle

def moveRobot(esp32, robotFront, robotBack, destination):
    # Calculate the relative angle to the destination
    relative_angle = calculate_relative_angle(robotFront, robotBack, destination)

    dx = robotFront[0] - destination[0]
    dy = robotFront[1] - destination[1]
    distance = math.sqrt(dx**2 + dy**2)

    if distance <= 75:
        move(STOP, esp32)
        return
    
    print(f"Relative angle: {relative_angle}")
    # Determine the movement direction based on the relative angle
    if -10 <= relative_angle <= 10:
        move(FORWARD, esp32)
    elif relative_angle > 0:
        move(RIGHT, esp32)
    elif relative_angle < 0:
        move(LEFT, esp32)