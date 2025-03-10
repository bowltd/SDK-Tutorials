#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (c) 2024, Bettering Our Worlds (BOW) Ltd.
# All Rights Reserved
# Author: George Bridges <george.bridges@bow.ltd>

import bow_api
import bow_data

import math
import time
import sys

def SendObjective(robot, effector, x, y, z):

    print("Sending objective: "+str(x)+", "+str(y)+", "+str(z))
    mSamp = bow_data.MotorSample()
    mSamp.IKSettings.Preset = bow_data.IKOptimiser.HIGH_ACCURACY

    objective_command = bow_data.ObjectiveCommand()
    objective_command.TargetEffector = effector
    objective_command.ControlMode = bow_data.ControllerEnum.POSITION_CONTROLLER
    objective_command.PoseTarget.Action = bow_data.ActionEnum.GOTO
    objective_command.PoseTarget.TargetType = bow_data.PoseTarget.TargetTypeEnum.TRANSFORM
    objective_command.PoseTarget.TargetScheduleType = bow_data.PoseTarget.SchedulerEnum.INSTANTANEOUS

    objective_command.PoseTarget.LocalObjectiveWeights.Position = 1
    objective_command.PoseTarget.LocalObjectiveWeights.Orientation = 0

    objective_command.PoseTarget.Transform.Position.X = x
    objective_command.PoseTarget.Transform.Position.Y = y
    objective_command.PoseTarget.Transform.Position.Z = z

    objective_command.Enabled = True
    mSamp.Objectives.append(objective_command)

    set_result = myRobot.motor.set(mSamp)
    if not set_result.Success:
        print("Failed to set motor channel")

# Use quick_connect to connect to robot
myRobot, error = bow_api.quick_connect(app_name="Inverse Kinematics", channels=["proprioception", "motor"], verbose=False)

if not error.Success:
    print("Failed to connect to robot", error)
    sys.exit()

effectorsList = []
reachList = []
upDownList = []
partsList = []

# Wait for proprioception message so we can understand form of robot and get effectors
while True:
    propMsg, error = myRobot.proprioception.get(True)
    if not error.Success:
        continue

    if propMsg is None:
        continue

    if len(propMsg.Effectors) == 0:
        continue

    for part in propMsg.Parts:
        for effector in part.Effectors:
            # only get controllable effectors. This removes all effectors that don't have moveable joints within their kinematic chain
            if not effector.IsControllable:
                continue
                
            partsList.append(effector.Type)
            effectorsList.append(effector.EffectorLinkName)
            reachList.append(effector.Reach)
            
            # Effector is by default higher than root hence height offset should be positive
            if effector.EndTransform.Position.Z > effector.RootTransform.Position.Z:
                upDownList.append(1)

            # Effector is by default lower than effector root hence height offset should be negative
            else:
                upDownList.append(-1)
                
    break

## DECIDE ##

selectedEffector = ""
selectedReach = 0
selectedUpDown = 1

# Prompt user for the target end effector in the terminal
while True:
    print("Please select an option:")
    for i, effector in enumerate(effectorsList):
        print(f"{i + 1}. {effector} of type {partsList[i]} "
              f"with reach of {reachList[i]}m and default direction {upDownList[i]}")

    try:
        userInput = int(input("Enter your choice (number): "))
    except ValueError:
        print("Invalid input. Please enter a valid integer index.")
        continue

    if userInput > 0 and userInput <= len(effectorsList):
        selectedEffector = effectorsList[userInput - 1]
        selectedReach = reachList[userInput - 1]
        selectedUpDown = upDownList[userInput - 1]
        print(f"You selected: {selectedEffector}")
        break

    print("Invalid choice. Please run the program again and select a valid number.")

## ACT ##
# Movement Pattern Parameters
circleRadius = selectedReach * 0.25 # Radius of the circle
circleHeight = selectedReach * 0.3 # Z-Axis height of circle
wobbleAmplitude = selectedReach * 0.05
wobbleFreqMultiplier = 6
stepSize = 0.05
repeatCountLim = 10 # Number of repetitions of the loop

# Create and send movement coordinates
try:
    repeatCount = 0
    while repeatCount < repeatCountLim:
        angle = 0
        while angle <=2*math.pi:
            x = circleRadius * math.cos(angle)
            y = circleRadius * math.sin(angle)
            z = selectedUpDown*(circleHeight + (wobbleAmplitude * math.cos(angle*wobbleFreqMultiplier)))

            SendObjective(myRobot, selectedEffector, x, y, z)

            angle += stepSize
            time.sleep(stepSize)
        repeatCount += 1

except KeyboardInterrupt or SystemExit:
    print("Closing down")
    stopFlag = True

# Close the bow client
myRobot.disconnect()
bow_api.stop_engine()
