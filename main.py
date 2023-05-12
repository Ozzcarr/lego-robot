#!/usr/bin/env pybricks-micropython
from pybricks.ev3devices import ColorSensor, Motor, TouchSensor
from pybricks.hubs import EV3Brick
from pybricks.parameters import Direction, Port, Stop, Color, Button
from pybricks.tools import wait
from pybricks.messaging import BluetoothMailboxServer, TextMailbox, BluetoothMailboxClient

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
PICKUP_LOCATION = None
SHARED_LOCATION = None
LOCATIONS = []

# Define the colors
COLOR_NAMES = {'#050d59': 'Blue', '#210808': 'Red', '#3d211c': 'Yellow', '#082121': 'Green'}
COLORS = []

# Bluetooth
MODE = 0  # 0 = default, 1 = server, 2 = client
SERVER_NAME = 'ev3dev'
M_CALIBRATION_DONE = 'calibration_done'
M_COLOR_DONE = 'color_done'
M_PICKUP = 'pickup'


def ev3_light(color=''):
    """Sets a color for the EV3 Brick light from color name"""
    if color == 'Blue' or color == 'Orange':
        ev3.light.on(Color.ORANGE)
    elif color == 'Red':
        ev3.light.on(Color.RED)
    elif color == 'Yellow':
        ev3.light.on(Color.YELLOW)
    elif color == 'Green':
        ev3.light.on(Color.GREEN)
    else:
        ev3.light.off()


def wait_for_message(mbox, msg):
    """Waits for a matching bluetooth message"""
    while not mbox.read() == msg:
        wait(200)


def raise_elbow(position):
    """Raises the gripper above all locations in the way"""
    elbow_angle = elbow_motor.angle()
    max_angle = elbow_angle
    interval = (base_motor.angle(), position[0])

    ALL_LOC = LOCATIONS.copy()
    if MODE != 0:
        ALL_LOC.append(SHARED_LOCATION)
    for loc in ALL_LOC:
        if min(interval)-10 <= loc[0] <= max(interval)+10 and loc[1] + 15 > max_angle:
            max_angle = loc[1] + 15

    if elbow_angle < max_angle:
        elbow_motor.run_target(60, max_angle)


def calibration(mbox=None):
    """Calibration of the sensors"""
    ev3_light('Orange')
    # Limit acceleration
    elbow_motor.control.limits(speed=60, acceleration=120)
    base_motor.control.limits(speed=60, acceleration=120)

    # Initialize the gripper
    gripper_motor.run_until_stalled(200, then=Stop.COAST, duty_limit=50)
    gripper_motor.reset_angle(0)
    gripper_motor.run_target(200, -90)

    # Initialize the elbow
    elbow_motor.run_until_stalled(-30, then=Stop.COAST, duty_limit=30)
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

    alexi = ["C4/16", "C4/16", "G4/16", "C4/16", "C4/16", "G4/16", "C4/16", "G4/16", 
            "D#4/16", "D#4/16", "A#4/16", "D#4/16", "A#3/16", "A#3/16", "F4/16", "A#3/16", 

            "C#4/16", "C#4/16", "G#4/16", "C#4/16", "C#4/16", "G#4/16", "C#4/16", "G#4/16", 
            "G#3/16", "G#3/16", "D#4/16", "G#3/16", "G#3/16", "F3/16", "C4/16", "C4/16", 

            "C4/16", "C4/16", "G4/16", "C4/16", "C4/16", "G4/16", "C4/16", "G4/16", 
            "D#4/16", "D#4/16", "A#4/16", "D#4/16", "A#3/16", "A#3/16", "F4/16", "A#3/16", 

            "C#4/16", "C#4/16", "G#4/16", "C#4/16", "C#4/16", "G#4/16", "C#4/16", "G#4/16", 
            "G#3/16", "G#3/16", "D#4/16", "G#3/16", "A#3/16", "G3/16", "D4/16", "D4/16"]

    roope = ["C4/16", "C4/16", "D#4/16", "C4/16", "C4/16", "D#4/16", "C4/16", "D#4/16", 
            "D#4/16", "D#4/16", "G4/16", "D#4/16", "D4/16", "D4/16", "F4/16", "D4/16", 

            "C#4/16", "C#4/16", "F4/16", "C#4/16", "C#4/16", "F4/16", "C#4/16", "F4/16", 
            "G#3/16", "G#3/16", "C4/16", "G#3/16", "F3/16", "C4/16", "G#4/16", "G4/16", 

            "C4/16", "C4/16", "D#4/16", "C4/16", "C4/16", "D#4/16", "C4/16", "D#4/16", 
            "D#4/16", "D#4/16", "G4/16", "D#4/16", "D4/16", "D4/16", "F4/16", "D4/16", 

            "C#4/16", "C#4/16", "F4/16", "C#4/16", "C#4/16", "F4/16", "C#4/16", "F4/16", 
            "G#3/16", "G#3/16", "C4/16", "G#3/16", "G3/16", "D4/16", "A#4/16", "A4/16"]

    if MODE == 1:
        mbox.send(M_CALIBRATION_DONE)
        mbox.wait()
        ev3_light('Green')
        ev3.speaker.play_notes(alexi, tempo=96)
    elif MODE == 2:
        wait_for_message(mbox, M_CALIBRATION_DONE)
        mbox.send(M_CALIBRATION_DONE)
        ev3_light('Green')
        ev3.speaker.play_notes(roope, tempo=96)
    else:
        ev3_light('Green')
        ev3.speaker.play_notes(nokia, tempo=200)


def pickup(position, pause=3000):
    """Checks if an item is at an location and pickup"""
    raise_elbow(position)
    base_motor.run_target(60, position[0])
    elbow_motor.run_target(80, position[1], then=Stop.HOLD)
    wait(pause)

    gripper_motor.run_until_stalled(200, then=Stop.HOLD, duty_limit=50)
    gripper_motor.hold()

    if gripper_motor.angle() < -5:
        return True
    else:
        gripper_motor.run_target(200, -90)
        return False


def release(position):
    """Release item at position"""
    raise_elbow(position)
    base_motor.run_target(60, position[0])
    elbow_motor.run_target(60, position[1], then=Stop.HOLD)
    gripper_motor.run_target(200, -90)


def rgbp_to_hex(rgb):
    """Returns the hex value of the color from the RGB percentage values"""
    if rgb[0] == '#':
        return rgb
    else:
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


def move_base(position):
    """Moves the base_motor to a position"""
    raise_elbow(position)
    base_motor.run_target(60, position[0])


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
    return (base_motor.angle(), elbow_angle)


def read_color():
    """Reads color_sensor value"""
    elbow_motor.run_target(60, 0)
    color = color_sensor.rgb()
    ev3.screen.print(color_name(color))
    ev3_light(color_name(color))
    return color


def set_locations():
    """Set the pickup and drop off locations"""

    if MODE == 1 or MODE == 2:
        ev3.screen.print("Set shared location")
        global SHARED_LOCATION
        SHARED_LOCATION = set_location()
    wait(1000)

    if MODE == 0 or MODE == 1:
        ev3.screen.print("Set pickup location")
    elif MODE == 2:
        ev3.screen.print("Set rest position")

    global PICKUP_LOCATION
    PICKUP_LOCATION = set_location()
    wait(1000)
    ev3.screen.print("Position set")

    set_more_locations = True
    ev3.screen.print("Set drop-off locations")
    ev3.screen.print("Click to set \nnew position")

    while set_more_locations:
        if Button.CENTER in ev3.buttons.pressed():
            if MODE == 0 or MODE == 1:
                if pickup(PICKUP_LOCATION):
                    color = read_color()
                    COLORS.append(rgbp_to_hex(color))
                    ev3.screen.print("Set new location")
                    LOCATIONS.append(set_location())
                    ev3.screen.print("Click to set \nnew position")
                else:
                    set_more_locations = False
            elif MODE == 2:
                if pickup(SHARED_LOCATION):
                    color = read_color()
                    COLORS.append(rgbp_to_hex(color))
                    ev3.screen.print("Set new location")
                    LOCATIONS.append(set_location())
                    ev3.screen.print("Click to set \nnew position")
                else:
                    set_more_locations = False

    if MODE == 2:
        move_base(PICKUP_LOCATION)


def connect():
    """Connects to another robot via Bluetooth"""
    if MODE == 0:
        return None
    ev3_light('Orange')

    if MODE == 1:
        server = BluetoothMailboxServer()
        mbox = TextMailbox('msg', server)
        ev3.screen.print("Waiting for connection..")
        server.wait_for_connection()
    elif MODE == 2:
        client = BluetoothMailboxClient()
        mbox = TextMailbox('msg', client)
        ev3.screen.print("Establishing connection..")
        client.connect(SERVER_NAME)

    ev3.screen.print("Connected")
    ev3_light('Green')
    return mbox


def mode_selection():
    """Lets the user select the robot mode"""
    ev3.screen.print(" Up - Server. \nDown - client \nLeft - default")  # ?
    ev3_light('Orange')
    global MODE
    MODE = -1
    while MODE == -1:
        if Button.LEFT in ev3.buttons.pressed():
            MODE = 0
            ev3.screen.print("Default picked!")
        elif Button.UP in ev3.buttons.pressed():
            MODE = 1
            ev3.screen.print("Server picked!")
        elif Button.DOWN in ev3.buttons.pressed():
            MODE = 2
            ev3.screen.print("Client picked!")
    ev3_light('Green')
    wait(1000)
    return


def share_colors(mbox):
    """Shares client colors to server"""
    if mbox is None:
        return

    color_message = '*'.join(COLORS)

    if MODE == 1:
        ev3.screen.print("Waiting for client")
        wait_for_message(mbox, M_COLOR_DONE)
        mbox.send(M_COLOR_DONE)
        mbox.wait()
        COLORS.extend(mbox.read().split('*'))
    elif MODE == 2:
        mbox.send(M_COLOR_DONE)
        ev3.screen.print("Waiting for server")
        mbox.wait()
        mbox.send(color_message)

    wait(1000)
    mbox.send(M_PICKUP)


def release_from_color(mbox):
    """Releases an item based on its color"""
    color = None
    if MODE == 0 or MODE == 1:
        color = read_color()
    elif MODE == 2:
        color = mbox.read()

    index = color_index(color)

    if index >= len(LOCATIONS):  # Drop off at shared location
        release(SHARED_LOCATION)
        move_base(PICKUP_LOCATION)
        mbox.send(rgbp_to_hex(color))
        mbox.wait()
    else:
        ev3_light(color_name(color))
        release(LOCATIONS[index])
    ev3_light()


def try_pickup(position, mbox):
    """Attempts to pickup an item at a given position"""
    pause = 3000
    if MODE == 2:
        pause = 0

    if not pickup(position, pause):
        ev3.screen.print("No item")
        wait(3000)
    else:
        release_from_color(mbox)


def robot_process(mbox):
    """Robot process that loops"""
    if MODE == 0 or MODE == 1:
        try_pickup(PICKUP_LOCATION, mbox)
    elif MODE == 2:
        move_base(PICKUP_LOCATION)  # Resting position
        mbox.wait()
        ev3_light(color_name(mbox.read()))
        try_pickup(SHARED_LOCATION, mbox)
        mbox.send(M_PICKUP)


def main():
    """Main function"""
    mode_selection()
    mbox = connect()
    calibration(mbox)
    set_locations()
    share_colors(mbox)

    ev3.screen.print("Main Loop")
    wait(2000)

    while True:
        robot_process(mbox)


if __name__ == "__main__":
    main()

