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
M_LOCKED = 'locked'
M_EMPTY = 'empty'
M_OCC = 'occupied'


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
        wait(500)


def raise_elbow(position):
    """Raises the gripper above all locations in the way"""
    elbow_angle = elbow_motor.angle()
    max_angle = elbow_angle
    interval = (base_motor.angle(), position[0])

    for loc in LOCATIONS:
        if min(interval)-10 <= loc[0] <= max(interval)+10 and loc[1] > max_angle:
            max_angle = loc[1]

    elbow_motor.run_target(60, max_angle)
    elbow_motor.run_time(60, 200)


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

    if MODE == 1:
        mbox.send(M_CALIBRATION_DONE)
        mbox.wait()
        ev3_light('Green')
        ev3.speaker.play_notes(nokia, tempo=200)  # Server part
    elif MODE == 2:
        wait_for_message(M_CALIBRATION_DONE)
        mbox.send(M_CALIBRATION_DONE)
        # wait for timing ?
        ev3_light('Green')
        ev3.speaker.play_notes(nokia, tempo=200)  # Client part
    else:
        ev3_light('Green')
        ev3.speaker.play_notes(nokia, tempo=200)


def pickup(position):
    """Checks if an item is at an location and pickup"""
    raise_elbow(position)
    base_motor.run_target(60, position[0])
    elbow_motor.run_target(80, position[1], then=Stop.HOLD)
    gripper_motor.run_until_stalled(200, then=Stop.HOLD, duty_limit=50)

    gripper_motor.hold()
    # elbow_motor.run_target(60, 0)

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
    # elbow_motor.run_target(60, 40)


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
    elbow_motor.run_time(60, 200)
    # elbow_motor.run_target(60, 0)
    return (base_motor.angle(), elbow_angle)


def read_color_experimental():
    """Reads color_sensor value"""
    red = 0
    green = 0
    blue = 0

    elbow_motor.run_target(60, -5)
    for i in range(5):
        elbow_motor.run(25)
        color = color_sensor.rgb()

        if color[0] > red:
            red = color[0]
        if color[1] > green:
            green = color[1]
        if color[2] > blue:
            blue = color[2]

        wait(80)

    color = (red, green, blue)
    # ev3.screen.print(color_name(color))
    ev3.screen.print(color)
    ev3_light(color_name(color))
    return color


def read_color():
    """Reads color_sensor value"""
    elbow_motor.run_target(60, 0)
    color = color_sensor.rgb()
    ev3.screen.print(color_name(color))
    ev3_light(color_name(color))
    return color


def set_locations():
    """Set the pickup and drop off locations"""
    ev3.screen.print("Set pickup location")
    PICKUP_LOCATION = set_location()

    if MODE != 0:
        ev3.screen.print("Set shared location")
        SHARED_LOCATION = set_location()

    set_more_locations = True
    ev3.screen.print("Set drop-off locations")

    while set_more_locations:
        if Button.CENTER in ev3.buttons.pressed():
            if pickup(PICKUP_LOCATION):
                color = read_color()
                COLORS.append(rgbp_to_hex(color))       
                LOCATIONS.append(set_location())
            else:
                set_more_locations = False


def connect():
    """Connects to another robot via Bluetooth"""
    if MODE == 2:
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
    ev3.screen.print("Press Up for Server. \n Press Down for client \n Press Left for default")  # ?
    ev3_light('Orange')
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
    wait(1500)
    return


def share_colors(mbox):
    """Shares the colors between the robots"""
    if mbox is None:
        return

    color_message = '*'.join(COLORS)

    if MODE == 1:  # Server
        ev3.screen.print("Waiting for client")
        wait_for_message(M_COLOR_DONE)
        mbox.send(color_message)
        mbox.wait()
    elif MODE == 2:
        mbox.send(M_COLOR_DONE)
        ev3.screen.print("Waiting for server")
        mbox.wait()
        mbox.send(color_message)

    COLORS.extend(mbox.read().split('*'))
    wait(1000)
    mbox.send(M_EMPTY)


def messaging(mbox):
    """Responds to messages"""
    if mbox.read() == M_LOCKED or mbox.read() == M_PICKUP:
        mbox.send(M_OCC)
    elif mbox.read() == M_EMPTY:
        mbox.send(M_EMPTY)


def drop_at_shared_location(mbox):
    """Drops an item at the shared location"""
    mbox.send(M_LOCKED)
    release(SHARED_LOCATION)
    move_base(PICKUP_LOCATION)
    mbox.send(M_PICKUP)
    wait_for_message(M_OCC)


def release_from_color(mbox):
    """Releases an item based on its color"""
    color = read_color()
    index = color_index(color)

    if index >= len(LOCATIONS):  # Drop off at shared location
        if mbox.read() == M_EMPTY:
            drop_at_shared_location(mbox)

        elif mbox.read() == M_OCC:
            wait_for_message(M_EMPTY)
            wait(2000)
            drop_at_shared_location(mbox)

        elif mbox.read() == M_LOCKED:
            mbox.send(M_OCC)
            release(PICKUP_LOCATION)
            mbox.wait()

        elif mbox.read() == M_PICKUP:
            mbox.send(M_OCC)
            release(PICKUP_LOCATION)

    else:
        release(LOCATIONS[index])


def robot_process(mbox):
    """Robot process that loops"""
    messaging(mbox)

    if mbox.read() == M_PICKUP:
        mbox.send(M_OCC)
        if not pickup(SHARED_LOCATION):
            ev3.screen.print("No item")
            move_base(PICKUP_LOCATION)
        else:
            move_base(PICKUP_LOCATION)
            mbox.send(M_EMPTY)
            release_from_color(mbox)

        mbox.send(M_EMPTY)
        while mbox.read() == M_PICKUP:
            wait(200)

    elif mbox.read() == M_LOCKED:
        wait(2000)
        return

    else:
        if not pickup(PICKUP_LOCATION):
            ev3.screen.print("No item")
            wait(3000)
        else:
            release_from_color(mbox)


def test_read_color_experimental():
    calibration()
    while True:
        elbow_motor.run_until_stalled(-80, then=Stop.COAST, duty_limit=30)
        gripper_motor.run_until_stalled(200, then=Stop.HOLD, duty_limit=50)
        read_color_experimental()
        wait(500)
        gripper_motor.run_target(200, -90)
        wait(1500)


def test_read_color():
    calibration()
    elbow_motor.run_until_stalled(-80, then=Stop.COAST, duty_limit=30)
    gripper_motor.run_until_stalled(200, then=Stop.HOLD, duty_limit=50)
    while True:
        while Button.CENTER not in ev3.buttons.pressed():
            while Button.UP in ev3.buttons.pressed():
                elbow_motor.run(30)
            while Button.DOWN in ev3.buttons.pressed():
                elbow_motor.run(-30)

        elbow_motor.hold()
        ev3.screen.print(color_sensor.rgb())


def main():
    """Main function"""
    mode_selection()
    mbox = connect()
    calibration(mbox)
    set_locations()
    share_colors(mbox)

    ev3.screen.print("Main Loop")
    wait(5000)

    while True:
        robot_process(mbox)


if __name__ == "__main__":
    main()
