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

Before trying these tutorials make sure you have followed the instructions from Step_0_Dependencies to set up the development environment for your chosen programming language.

These tutorials also assume you have installed the BOW Hub available for download from https://bow.software and that you have registered for a Standard Subscription or using the 30 day free trial which is required to simulate robots.

Go ahead and open a simulated robot of your choice. For this tutorial we recommend:
- a quadruped like the DEEP Robotics - Lite 3 
- a humanoid like the Softbank Robotics - Nao.

You can still try connecting to one of the industrial robots if only to check the SDK's behaviour when the vision modality is not available. However, if you do want to get a video stream from the robot select a robot that has a vision modality.