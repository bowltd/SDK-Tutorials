# Windows - Installing and using the BOW Python SDK

This tutorial assumes you have already installed the BOW System Tray application and simulator on your workstation. If not, follow this [tutorial](https://github.com/bowltd/SDK-Tutorials/blob/main/Windows%20-%20Setting%20up%20your%20BOW%20developer%20environment.md) to get your environment set up.

### Installing the Python SDK
1. The simplest way to install the BOW SDKs is using the Systray application. Simply click the "Install SDKs" drop down menu and then select "Python SDK".
<img src="Screenshots/windows-python-sdk/1-image.png" alt="drawing"/>

2. Follow the onscreen prompts and wait for the installation to complete.
    1. If you receive the following error, then you will first need to install Python.
    <img src="Screenshots/windows-python-sdk/2-image.png" alt="drawing"/>
       1. To install Python, simply search for "Python 3" in the microsoft store and install. At the time of writing Python 3.11 is the latest version (3.7 or greater is required).
       <img src="Screenshots/windows-python-sdk/3-image.png" alt="drawing"/>

   1. If you receive the following error, then you will need to install Visual Studio Build Tools for C++, which is required for the installation of the Python package.
   <img src="Screenshots/windows-python-sdk/4-image.png" alt="drawing"/>

      1. Visit the official [downloads](https://visualstudio.microsoft.com/downloads/?q=build+tools) page.
      2. Scroll down to "Build Tools for Visual Studio 2022" under the "Tools for Visual Studio" heading and click download.
      <img src="Screenshots/windows-python-sdk/5-image.png" alt="drawing"/>
      3. Run the downloaded installer
      4. When the installer opens, under the "Workloads" tab, check the box for "Desktop development with C++" and select install.
      <img src="Screenshots/windows-python-sdk/6-image.png" alt="drawing"/>

3. When the installation is complete a dialog box will appear asking you to confirm and the Python SDK will now appear under the "Installed SDKs" section in the systray.
4. To test the installation we can open a Python 3 terminal, either by searching for it under the start menu, or by running the command `python`. Then try importing the newly installed package, `bow_client`.
<img src="Screenshots/windows-python-sdk/7-image.png" alt="drawing"/>

4. If there are no errors as a result of this command then we know the package installed successfully, and you are ready develop!

### Testing with a simulated robot
Now lets run your first BOW enabled Python program to control a simulated robot.

1. Let's start by running the simulator, this can either be launched from the systray, "Launch Webots Simulator", or by running "Webots" from the start menu.
2. In Webots, select `File -> Open Sample World`. In the menu that appears, navigate to `BOW -> pal_robotics -> tiago++ -> tiago++.wbt` and click OK.
<img src="Screenshots/linux-setup/9-image.png" alt="drawing"/>

3. Once the project opens the BOW driver will start running automatically, after a short moment the simulated Tiago++ robot, named Buddy, will appear in the BOW systray under the "My Robots" heading. Select this robot, and it will appear under the "Current Selection" heading. You are now connected to Buddy.
<img src="Screenshots/windows-python-sdk/8-image.png" alt="drawing"/>

4. Before running our example project we need to install pynput, a python package which is used to get the keyboard input. Open a cmd or powershell window and use the command `pip install pynput`.
<img src="Screenshots/windows-python-sdk/9-image.png" alt="drawing"/>

5. Now let's navigate to an example project, by clicking on the installed SDK in the systray you will be taken to the tutorials directory (C:\Users\USER\\.bow\tutorials\Python\).
6. For this example we will use the Keyboard Control project, open the keyboard control directory and within a cmd or powershell window run the command

```bash
python '.\keyboard_control.py\'
```
<img src="Screenshots/windows-python-sdk/10-image.png" alt="drawing"/>

7. You will see a window open which displays the image stream from the camera of the Tiago++. You will also see some activity in the console of the Webots sim which indicates that the connection to the robot has been made.
<img src="Screenshots/windows-python-sdk/11-image.png" alt="drawing"/>

8. Try controlling the robot using your keyboard. W, A, S and D keys control forwards, backwards and rotate, Q and E control strafing, the arrow keys control head movements.
9. That's it, you have now tested your first BOW enabled robot using the Python SDK.

### Experiment
Why not take this test further, your robot doesn't need to be on the same local network as your Python program. Why not run the simulated robot on one workstation and run the keyboard controller from another workstation on a different network to experience simulated telepresence!
