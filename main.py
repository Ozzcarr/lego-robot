#!/usr/bin/env pybricks-micropython
from pybricks.ev3devices import ColorSensor, Motor, TouchSensor
from pybricks.hubs import EV3Brick
from pybricks.parameters import Direction, Port, Stop, Color
from pybricks.tools import wait


# Initialize the EV3 brick.
ev3 = EV3Brick()

# Initialization and configuration of motors
gripper_motor = Motor(Port.A)
elbow_motor = Motor(Port.B, Direction.COUNTERCLOCKWISE, [8, 40])
base_motor = Motor(Port.C, Direction.COUNTERCLOCKWISE, [12, 36])

# Initialize sensors
touch_sensor = TouchSensor(Port.S1)
color_sensor = ColorSensor(Port.S2)

# Define the three destinations for picking up and moving the wheel stacks.
LEFT = 160
MIDDLE = 100
RIGHT = 40


def calibration():
    """Calibration of the sensors"""
    # Limit acceleration
    elbow_motor.control.limits(speed=60, acceleration=120)
    base_motor.control.limits(speed=60, acceleration=120)

    # Initialize the gripper
    gripper_motor.run_until_stalled(200, then=Stop.COAST, duty_limit=50)
    gripper_motor.reset_angle(0)
    gripper_motor.run_target(200, -90)

    # Initialize the elbow
    elbow_motor.run_time(-30, 1000)
    elbow_motor.run(15)
    while color_sensor.reflection() > 0:
        wait(10)
    elbow_motor.run_time(20, 400)
    elbow_motor.reset_angle(0)
    elbow_motor.hold()

    # Initialize the base
    base_motor.run(-60)
    while not touch_sensor.pressed():
        wait(10)
    base_motor.reset_angle(0)
    base_motor.hold()

    # Play music to indicate that the initialization is complete.
    nokia = ["E5/8", "D5/8", "F#4/4", "G#4/4", "C#5/8", "B4/8", "D4/4", "E4/4", "B4/8", "A4/8", "C#4/4", "E4/4", "A4/2", "R/2"]

    ev3.speaker.play_notes(nokia, tempo=200)
    ev3.speaker.play_notes(nokia, tempo=200)



def pickup(position):
    """Pickup item at position"""
    base_motor.run_target(60, position)
    elbow_motor.run_until_stalled(-80, then=Stop.COAST, duty_limit=30)
    gripper_motor.run_until_stalled(200, then=Stop.HOLD, duty_limit=50)
    elbow_motor.run_target(60, 0)


def release(position):
    """Release item at position"""
    base_motor.run_target(60, position)
    elbow_motor.run_until_stalled(-80, then=Stop.COAST, duty_limit=30)
    gripper_motor.run_target(200, -90)
    elbow_motor.run_target(60, 0)


def color():
    return color_sensor.color()


def main():
    """Main function"""
    calibration()

    rightColor = Color.RED
    leftColor = Color.BLUE

    while True:
        pickup(MIDDLE)
        ev3.screen.clear()
        ev3.screen.draw_text(40, 50, color())
        if color() == rightColor:
            release(RIGHT)
        elif color() == leftColor:
            release(LEFT)
        else:
            release(MIDDLE)



if __name__ == "__main__":
    main()
