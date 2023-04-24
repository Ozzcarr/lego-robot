#!/usr/bin/env pybricks-micropython
from pybricks.ev3devices import ColorSensor, Motor, TouchSensor
from pybricks.hubs import EV3Brick
from pybricks.parameters import Direction, Port, Stop, Color, Button
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

# List for the pickup and drop off locations
LOCATIONS = []

# Define the colors
COLOR_NAMES = {'#050d59': 'Blue', '#210808': 'Red', '#3d211c': 'Yellow', '#082121': 'Green'}
COLORS = []


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
    elbow_motor.run_until_stalled(-30, then=Stop.COAST, duty_limit=50)
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

    # ev3.speaker.play_notes(nokia, tempo=200)
    # ev3.speaker.play_notes(nokia, tempo=200)


def pickup(position):
    """Checks if an item is at an location and pickup"""
    base_motor.run_target(60, position[0])
    elbow_motor.run_target(80, position[1], then=Stop.HOLD)
    gripper_motor.run_until_stalled(200, then=Stop.HOLD, duty_limit=50)

    gripper_motor.hold()
    elbow_motor.run_target(60, 0)

    if gripper_motor.angle() < -5:
        return True
    else:
        gripper_motor.run_target(200, -90)
        return False


def release(position):
    """Release item at position"""
    base_motor.run_target(60, position[0])
    elbow_motor.run_target(60, position[1], then=Stop.HOLD)
    gripper_motor.run_target(200, -90)
    elbow_motor.run_target(60, 40)


def rgbp_to_hex(rgb):
    """Returns the hex value of the color from the RGB percentage values"""
    rgb = tuple(round(p * 2.55) for p in rgb)
    return '#{:02x}{:02x}{:02x}'.format(*rgb)


def diff(h1, h2):
    """Returns how far apart two hex values are"""
    def hex_to_int(s):
        return [int(s[i:i+2], 16) for i in range(1,7,2)]
    return sum(abs(i - j) for i, j in zip(*map(hex_to_int, (h1, h2))))


def color_index(color):
    """Returns the index to the closest color in COLORS"""
    return COLORS.index(min([(c, diff(c, rgbp_to_hex(color))) for c in COLORS], key=lambda x: x[1])[0])


def color_name(color):
    """Returns the name of the color"""
    return COLOR_NAMES[min([(c, diff(c, rgbp_to_hex(color))) for c, n in COLOR_NAMES.items()], key=lambda x: x[1])[0]]


def ev3_light(color):
    """Sets a color for the EV3 Brick light from color name"""
    if color == 'Blue':
        ev3.light.on(Color.ORANGE)
    elif color == 'Red':
        ev3.light.on(Color.RED)
    elif color == 'Yellow':
        ev3.light.on(Color.YELLOW)
    elif color == 'Green':
        ev3.light.on(Color.GREEN)


def set_location():
    """Returns the angles of the set position"""
    while Button.CENTER not in ev3.buttons.pressed():
        while Button.LEFT in ev3.buttons.pressed():
            base_motor.run(50)
        while Button.RIGHT in ev3.buttons.pressed():
            base_motor.run(-50)
        while Button.UP in ev3.buttons.pressed():
            elbow_motor.run(30)
        while Button.DOWN in ev3.buttons.pressed():
            elbow_motor.run(-30)

        base_motor.hold()
        elbow_motor.hold()

    elbow_angle = elbow_motor.angle()
    gripper_motor.run_target(200, -90)
    elbow_motor.run_target(60, 40)
    return (base_motor.angle(), elbow_angle)


def set_locations():
    """Set the pickup and drop off locations"""
    ev3.screen.print("Set pickup location")
    LOCATIONS.append(set_location())
    set_more_locations = True
    ev3.screen.print("Set drop-off locations")
    while set_more_locations:
        if Button.CENTER in ev3.buttons.pressed():
            if pickup(LOCATIONS[0]):
                COLORS.append(rgbp_to_hex(color_sensor.rgb()))
                elbow_motor.run_target(60, 40)
                ev3.screen.print(color_name(color_sensor.rgb()))
                ev3_light(color_name(color_sensor.rgb()))
                LOCATIONS.append(set_location())
            else:
                set_more_locations = False


def main():
    """Main function"""
    calibration()
    set_locations()
    ev3.screen.print("Main Loop")
    wait(5000)

    if len(LOCATIONS) < 2:
        return

    while True:
        if not pickup(LOCATIONS[0]):
            ev3.screen.print("No item")
            wait(3000)
            continue

        color = color_sensor.rgb()
        ev3.screen.print(color_name(color))
        ev3_light(color_name(color))
        release(LOCATIONS[color_index(color)+1])


if __name__ == "__main__":
    main()
