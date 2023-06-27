# Bettering Our Worlds (BOW) SDK Python Tutorial: Remote Controlling a Robot

Welcome to the Bettering Our Worlds (BOW) SDK Python tutorial. In this guide, we will walk through how to create a Python application that uses the BOW SDK to remotely control a robot. We'll show you how the BOW SDK can simplify the task of interacting with robotic systems, making it as easy as controlling an IO device.

**Prerequisites:**
1. Install Python3
2. Install the BOW SDK (including `bow_client`, `bow_utils`)
3. Install the `pynput` and `opencv-python` packages (for keyboard inputs and image processing respectively).

**Step 1: Importing necessary modules**

Our first step is to import all the necessary Python modules that our application will be using:

```python
import bow_client as bow
import bow_utils as utils
import sys
import logging
import cv2
import time
from pynput import keyboard
```

**Step 2: Defining the Key Press Function**

Next, we define the function `on_press(key)`, which will be called every time a key is pressed. This function processes keyboard inputs to control the robot's movements and actions:

```python
def on_press(key):
    ...
```

**Step 3: Logging and Quick Connecting to a Systray chosen robot**

In the following block, we initialize the logging functionality, get the BOW version, and run a QuickConnect which takes in the log created and a list of channels to open. QuickConnect talks to the system tray application to login, get a list of robots, chonnect to the robot chosen via the system tray and open the requested channels returning a robot if successful or None otherwise.

```python
log = utils.create_logger("MyBOWApp", logging.INFO)
log.info(animus.version())
...
myrobot = bow.quick_connect(log, ["motor", "vision"])
if myrobot is None:
    sys.exit(-1)
...
```

**Step 6: Initializing the Keyboard Listener**

Next, we start a keyboard listener that will monitor for key presses. The commands are:
- Arrow Keys to control head position
- W: Move forward
- S: Move backward
- A: Rotate left
- D: Move right
- Q: Move sideways left (Nao/Pepper)
- E: Move sideways right (Nao/Pepper)
- Z: Extend torso up (Tiago)
- C: Extend torso down (Tiago)
- R: Select next joint
- T: Increase current joint angle
- G: Decrease current joint angle

```python
listener = keyboard.Listener(on_press=on_press)
listener.start()
```

**Step 7: Main Program Loop**

Finally, we enter a main loop where we continuously fetch images from the robot's vision modality and display them while reading command line inputs to control the robot's movement.

```python
cv2.namedWindow("RobotView")
try:
    while listener.is_alive():
        image_list, err = myrobot.get_modality("vision", True)
        ...
        cv2.imshow("RobotView", myim)
        ...
except KeyboardInterrupt:
    ...
```

**Step 8: Disconnecting and Cleaning Up**

At the end of the program, or if an error occurs, we disconnect from the robot and close the client interface:

```python
myrobot.disconnect()
animus.close_client_interface()
```

And that's it! You've created a Python application that uses the BOW SDK to remotely control a robot. You can now use

 this as a starting point to explore more functionalities and possibilities that the SDK offers. Happy coding!
