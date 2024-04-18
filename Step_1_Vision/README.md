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

If you are trying the C++ version of these tutorials make sure you have followed Step_0_Dependencies to set up your system 