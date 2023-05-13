# LEGO Robot

![The robot](http://robotsquare.com/wp-content/uploads/2013/10/45544_crane-550x227.jpg)


## Introduction

This is a repository for the [LEGO® MINDSTORMS® EV3](https://education.lego.com/en-us/products/lego-mindstorms-education-ev3-core-set/5003400#lego-mindstorms-education-ev3) robot. With the code in this repository, you can have your own sorting robot using a Lego EV3 Mindstorms Kit and Pybricks software.
The robot has a range of impressive capabilities, including:
- The ability to pick up and set down objects at user-defined locations.
- Detect and determine the color of objects.
- Sort objects by their colors into different locations.
- Communicate with another robot to expand the places where objects can be placed.

This readme will guide you through the installation and usage of the program, as well as provide detailed information on the robot's features and functionalities.


## Getting started

To get started, you will need to install Python and VS Code on your computer. You can download the latest version of Python from the [official website](https://www.python.org/downloads/). Once you have downloaded and installed Python, you can download and install [Visual Studio Code](https://code.visualstudio.com/download).

Next, you will need to install the Pybricks library. Pybricks is a Python library that provides an easy-to-use interface for programming LEGO robots. You can install Pybricks using pip, which is a package installer for Python, or follow [these instructions](https://github.com/pybricks/pybricksdev). To install with pip, open the terminal or command prompt and run the following command:
```
pip install pybricksdev
```
This will install the latest version of Pybricks on your computer.

Next we recommend installing the LEGO® MINDSTORMS® EV3 MicroPython VS Code extension to help with connecting to the robot. This can be done by searching for '***lego-education.ev3-micropython***' in the extenstions tab in VS Code and downloading the showing extension.

Now comes the part where you download the code that the robot will run. In [releases](https://github.com/Ozzcarr/lego-robot/releases), from the latest release, download the **lego-robot.zip** and extract the folder inside to a place of your liking. In VS Code, open the explorer by using the button on the left or by pressing Ctrl+Shift+E, click on "Open Folder" and open the folder you just extracted from the zip file.


## Building and running

In this part you will get to know how to get the robot up and running. This will include:
- Connecting the robot to the computer
- Uploading the code and running the program
- Calibrating one robot
- Connecting the robot to another robot
- Calibrating two robots
- Running the robot or robots

### Connect to PC

To connect the robot to the PC, ensure that the robot is powered on and connected to the PC with a USB cable. Then the steps are the following:
1. In VS Code, open the explorer by using the button on the left or by pressing Ctrl+Shift+E.
2. Click on "EV3DEV DEVICE BROWSER" in the bottom of the explorer to extend it.
3. Click on "Click here to connect a device".
4. You should now see your robot in the menu that popped up. Click on it to connect.

### Run the program

To run the program you first need to upload the code to the robot. After you have connected the robot to the PC, this can be done by clicking the download button in the "EV3DEV DEVICE BROWSER". To run the program and run it at the same time, press F5.

To run the code once it is uploaded, follow these steps:
1. Go to file browser.
2. Click on the folder "lego-robot".
3. Click on "main.py".

The program should now start running.

### Calibrating one robot

When the program is running, press left-button to enter default mode, where only a single robot is used. The robot will then calibrate, it is important that the robot can move freely at this phase. At the end of the calibration phase the robot will play a tune.

After the calibration it is time to set locations. The robot will ask for a pickup location. Use the buttons (up, down, left, right) to navigate to the pickup location, then press the middle button in order to save the location.

The next step is to set drop-off locations. Place an item at the pickup location and press the middle button on the robot. The robot will pickup the item and read the color of it. Then use the buttons to navigate to the drop-off location of that color. When at the drop-off location, press the middle button to save it. Then place a new item at the pickup location and press the middle button, the process is then repeated. When all items has been calibrated, press the middle button, if there is no item at the pickup location, the calibration of colors will end.

### Connecting to another robot

To connect two robots with each other the following steps need to be made.

On both robots the bluetooth visibility needs to be on. This can be achieved via the following steps.

1. In the menu of the robot open "Wireless and Networks".
2. Select Bluetooth.
3. Turn on Bluetooth.
4. Turn "Visible" on.

After visibility has been turned on, on both robots, the robots need to be paired. Once they are paired, do not click connect in the menu that appears. The connection will be made when you run your programs, as described below.

1. In the bluetooth settings press "Start Scan" on both robots.
2. Wait for the search to find both robots and select the device you want to connect to.
3. Press "Pair" on the following screen after making sure it is the correct device, the same code should appear on both devices.
4. Confirm the pass key and press accept.

The robots are now connected.

### Calibrating two robots

When using two robots that are paired via bluetooth, one has to be a server and the other a client. When starting the program, click the up-button on one robot in order to make it a server. Then click down-button on the other robot in order to connect them. It is important to select the server before selecting the client. Also the server robot's name has to be 'ev3dev'.

The robots will then calibrate, it is important that the robots can move freely at this phase. At the end of the calibration phase the robots will play a tune in sync.

After the calibration it is time to set locations. The display will tell you what positions to set. Both robots will be prompted to set a shared location. The shared location is the location that the two robots have in common. Use the buttons (left, right, up, down) on one robot at a time to navigate to the chosen location, then press the middle button to store it. Follow the instructions on the screen to set positions. When calibrating the item colors, the server will pickup items from the set pickup location, while the client will pickup items from the shared location. The calibration of item colors is done in the same way as with one single robot as described above.

When both the server and client are calibrated, the main loop will begin.

### Running

#### One robot
After the setup phase the robot will enter the main loop. The program will repeat the following:
* Try to pickup an item at the pickup location.
* If there is an item at the pickup location, the robot will read the color of the item and determine the location that matches the color best. Then the robot will move to that location and drop off the item there. 
* If there is no item at the pickup location, the robot will wait for 3 seconds and then look for an item again.

#### Two robots
After the setup phase the robot will enter the main loop. The client robot will be in its resting position. The program will repeat the following:

* The server robot tries to pickup an item at the pickup location.
* If there is no item at the pickup location, the server robot will wait for 3 seconds and then look for an item again.
* If there is an item at the pickup location, the server robot will read its color and determine which location is closest to the color. 
  * If the location belongs to the client robot, the server robot will drop the item off at the shared position, then return to the pickup location and wait there, while the client robot picks up the item and places it at the given location. 
  * If the location belongs to the server robot, the server robot will drop off the item at the given location.


## Features

- [x] US01B:       As a customer, I want the robot to pick up items from a designated position.
- [x] US02B:       As a customer, I want the robot to drop items off at a designated position. 
- [x] US03: &nbsp; As a customer, I want the robot to be able to determine if an item is present at a given location.
- [x] US04: &nbsp; As a customer, I want the robot to tell me the color of an item.
- [x] US05: &nbsp; As a customer, I want the robot to drop items off at different locations based on the color of the item.
- [x] US06: &nbsp; As a customer, I want the robot to be able to pick up items from elevated positions.
- [x] US08B:       As a customer, I want to be able to calibrate items with three different colors and drop the items off at specific drop-off zones based on color.
- [x] US09: &nbsp; As a customer, I want the robot to check the pickup location periodically to see if a new item has arrived.
- [x] US10: &nbsp; As a customer, I want the robots to sort items at a specific time.
- [x] US11: &nbsp; As a customer, I want two robots to communicate and work together on items sorting without colliding with each other.
- [x] US12: &nbsp; As a customer, I want to be able to manually set the locations and heights of one pick-up zone and two drop-off zones.
