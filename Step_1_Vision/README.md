# Step 1 - Vision

Welcome to this tutorial series in robotics powered by the BOW SDK. This is Step 1 - Vision.

At BOW we encourage thinking about robotics problems in a very human way and to also 
solve them in a human way. Every real world task can be solved with the use of the same
three part control loop.
1. Sense the Environment
2. Using the sensations from the Environment, decide on the next actions to perform that achieve your current goal
3. Carry out the planned actions within the environment
4. Repeat from 1

The BOW SDK was specifically designed to greatly simplify the programming for Steps 1 and 3 and make the programming for these steps universal across different robots, languages and operating systems. 

Crucially we leave all the decision-making up to you or your AI models!

## Visual Sensing

The first step in any robotics journey is that of understanding your environment. This tutorial demonstrates how to perceive the visual environment around the robot by sampling the Vision Modality.

To achieve this we will:
- Connect to a robot by calling *QuickConnect*
- Get all the images sampled by the robot by calling *GetModality("vision")*
- Place the data for the returned images into OpenCV
- Visualise the OpenCV images

### Prerequisites
The key libraries are:
- **OpenCV** - a library of programming functions mainly for real-time computer vision

Before trying these tutorials make sure you have followed the instructions from Step_0_Dependencies to set up the development environment for your chosen programming language.

These tutorials also assume you have installed the BOW Hub available for download from https://bow.software and that you have registered for a Standard Subscription or using the 30 day free trial which is required to simulate robots.

Go ahead and open a simulated robot of your choice. For this tutorial we recommend:
- a quadruped like the DEEP Robotics - Lite 3 
- a humanoid like the Softbank Robotics - Nao.

You can still try connecting to one of the industrial robots if only to check the SDK's behaviour when the vision modality is not available. However, if you do want to get a video stream from the robot select a robot that has a vision modality.