# Step 2 - Locomotion

Welcome to this tutorial series in robotics powered by the BOW SDK. This is Step 2 - Locomotion

Let's restate the control loop:

1. Sense the Environment
2. Using the sensations from the Environment, decide on the next actions to perform that achieve your current goal
3. Carry out the planned actions within the environment
4. Repeat from 1

In the previous step we learned how to sample the robot's visual modality. In this step, you will play the part of
the decision maker and control the robot's movement given video stream received from the robot.

## Locomotion

In this step we will tackle locomotion, or the act of moving around within the robot's world.

To achieve this we will have the following:

#### Sense
- Connect to a robot by calling *QuickConnect*
- Get all the images sampled by the robot by calling *GetModality("vision")*
- Place the data for the returned images into OpenCV
- Visualise the OpenCV images

#### Decide

- User decides where they want to move

#### Act
- User presses keys on the keyboard based on a decision made
- Read keypress events from the keyboard
- Send locomotion decision to robot by calling *SetModality("motor")*

### Prerequisites
The key libraries are:
- **OpenCV** - a library of programming functions mainly for real-time computer vision

If you are trying the C++ version of these tutorials make sure you have followed Step_0_Dependencies to set up your system 