# Bettering Our Worlds (BOW) SDK Python Tutorial: Remote Controlling a Robot

Welcome to the Bettering Our Worlds (BOW) SDK Python tutorial. In this guide, we will walk through how to create a Python application that uses the BOW SDK to remotely control a robot. We'll show you how the BOW SDK can simplify the task of interacting with robotic systems, making it as easy as controlling an IO device.

**Prerequisites:**
1. Install Python3
2. Install the BOW SDK (including `animus_client`, `animus_utils`)
3. Install the `pynput` and `opencv-python` packages (for keyboard inputs and image processing respectively).

**Step 1: Importing necessary modules**

Our first step is to import all the necessary Python modules that our application will be using:

```python
import animus_client as animus
import animus_utils
import animus_utils as utils
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

**Step 3: Logging and Initializing Animus**

In the following block, we initialize the logging functionality, get the animus version, setup the Animus system, log into Animus, and search for available robots:

```python
log = utils.create_logger("MyAnimusApp", logging.INFO)
log.info(animus.version())
...
login_result = animus.login_user("", "", True)
...
get_robots_result = animus.get_robots(True, True, True)
...
```

**Step 4: Connecting to the Robot**

Next, we connect to a robot. We take the first robot we find from the previous step and attempt to connect to it:

```python
chosen_robot_details = get_robots_result.robots[0]
myrobot = animus.Robot(chosen_robot_details)
connected_result = myrobot.connect()
...
```

**Step 5: Opening the Modalities**

In this step, we open the modalities (channels of interaction) that we want to use with the robot. In this case, we open "vision", "motor", "audition" and "voice":

```python
open_success = myrobot.open_modality("vision")
...
open_success = myrobot.open_modality("motor")
...
open_result = myrobot.open_modality("audition")
...
open_result = myrobot.open_modality("voice")
...
```

**Step 6: Initializing the Keyboard Listener**

Next, we start a keyboard listener that will monitor for key presses:

```python
listener = keyboard.Listener(on_press=on_press)
listener.start()
```

**Step 7: Main Program Loop**

Finally, we enter a main loop where we continuously fetch images from the robot's vision modality and display them:

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
