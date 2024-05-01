# Step 2 - Locomotion

Welcome to this tutorial series in robotics powered by the BOW SDK. This is Step 3 - Inverse Kinematics

In the previous step we learned how to sample the robot's visual modality, make a decision as to where we want the 
robot to go and then press the corresponding button on the keyboard. This in turn tells the robot where to move to using velocity control.

In this step, we will now learn how to use the BOW SDK to tell a robot's effector to go to a specific point in 3D space.
Inverse kinematics answers the question: "What angles do I need to set all my motors at in order for an effector to go to a target 3D position?"

Effectors can be many things:
- it can be the foot of a quadruped which is deciding exactly where to place its feet to avoid obstacles or to avoid falling into a hole
- it can be the tool attached to an industrial arm where the tool must interact with the parts being manufactured in a specific trajectory
- it can be the arm of a humanoid robot performing a gesture or reaching out to grab an object from the table

All of these examples use inverse kinematics to generate a solution for how to move the motors to achieve the desired outcome.

Inverse kinematics is different from Locomotion in that Locomotion is about moving the whole body within the robot's environment whereas Inverse kinematics is about interacting with objects in the vicinity of the robot while the robot is (for the most part) static.

## Inverse Kinematics

To carry out Inverse Kinematics we will have the following:

#### Preparation
In this example, the sensing will be done manually. You will need to 
- decide on a list of 3d positions for the robot to move into. 

These positions can be related to objects within the scene or to a specific trajectory that you want your robot to carry out. Keep in mind the right-handed coordinate frame for BOW where +ve X is forward, +ve Y is left and +ve Z is up.

- Then input the target position and orientation for one of the robot's effectors by changing the list of effector targets within the code

If you select the LewanSoul - xArm robot simulation, the list of movements has been preselected for you and this demo will touch all the bolts within the scene that are accessible to the robot.


#### Sense 
- Connect to a robot by calling *QuickConnect*
- The sensing is hard coded in this example through the use of a list of objective positions

#### Decide
- Using the Proprioception modality we get the list of all the effectors available for the job and the user decides which one to use

#### Act
- After selecting the target effector, the robot will consecutively send objectives within the list at the rate of one per second to the robot to carry out
- The objectives are embedded into a Motor Sample and sent to the robot using *SetModality("motor")*

### Dependencies 
No dependencies

Before trying these tutorials make sure you have followed the instructions from Step_0_Dependencies to set up the development environment for your chosen programming language.

These tutorials also assume you have installed the BOW Hub available for download from https://bow.software and that you have registered for a Standard Subscription or using the 30 day free trial which is required to simulate robots.

Go ahead and open a simulated robot of your choice. For this tutorial we recommend:
- LewanSoul - xArm
