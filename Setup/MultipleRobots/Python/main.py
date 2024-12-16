#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (c) 2024, Bettering Our Worlds (BOW) Ltd.
# All Rights Reserved
# Author: George Bridges <george.bridges@bow.ltd>

import math
import time
import bow_client as bow
import bow_utils as utils
import sys
import logging

def SendObjective(robots, effectors, x, y, z):
    for i, robot in enumerate(robots):
        mSamp = utils.MotorSample()
        mSamp.IKSettings.Preset = utils.IKOptimiser.HIGH_ACCURACY

        objective_command = utils.ObjectiveCommand()
        objective_command.TargetEffector = effectors[i]
        objective_command.ControlMode = utils.ControllerEnum.POSITION_CONTROLLER
        objective_command.PoseTarget.Action = utils.ActionEnum.GOTO
        objective_command.PoseTarget.TargetType = utils.PoseTarget.TargetTypeEnum.TRANSFORM
        objective_command.PoseTarget.TargetScheduleType = utils.PoseTarget.SchedulerEnum.INSTANTANEOUS

        objective_command.PoseTarget.LocalObjectiveWeights.Position = 1
        objective_command.PoseTarget.LocalObjectiveWeights.Position = 0

        objective_command.PoseTarget.Transform.Position.X = x
        objective_command.PoseTarget.Transform.Position.Y = y
        objective_command.PoseTarget.Transform.Position.Z = z

        objective_command.Enabled = True
        mSamp.Objectives.append(objective_command)

        setResult = robot.set_modality("motor", mSamp)
        if not setResult.Success:
            log.info("Failed to set motor modality")

# Initialize the logger
log = utils.create_logger("BOW Tutorial", logging.INFO)

# Audio parameters
audio_params = utils.AudioParams(
    Backends=[""],
    SampleRate=16000,
    Channels=1,
    SizeInFrames=True,
    TransmitRate=20
)

# Setup the BOW Client
setup_result = bow.setup(audio_params, log.name, True)
if not setup_result.Success:
    sys.exit(-1)

# Login to BOW using systray login
login_result = bow.login_user("", "", True)
if login_result.Success:
    log.info("Logged in")
else:
    sys.exit(-1)

# Get robots
get_robots_result = bow.get_robots(True, True, False)
if not get_robots_result.localSearchError.Success:
    log.error(get_robots_result.localSearchError.Description)

if not get_robots_result.remoteSearchError.Success:
    log.error(get_robots_result.remoteSearchError.Description)

if len(get_robots_result.robots) == 0:
    log.info("No Robots found")
    bow.close_client_interface()
    sys.exit(-1)

# Filter out only the available robots
available_robots = [r for r in get_robots_result.robots if r.robot_state.available]

# Print out all found robots and whether they are available
print("Robots discovered:")
for i, robot in enumerate(available_robots):
    print(f"{i}: {robot.name}")

if len(available_robots) < 2:
    log.info("Not enough available robots to select two.")
    bow.close_client_interface()
    sys.exit(-1)

# Prompt user to select two robots by their index from the displayed list of available robots
def get_robot_selection(prompt):
    while True:
        try:
            idx = int(input(prompt))
            if 0 <= idx < len(get_robots_result.robots):
                return idx
            else:
                print("Invalid index. Please try again.")
        except ValueError:
            print("Invalid input. Please enter a valid integer index.")

robot_idx_1 = get_robot_selection("Enter the index of the first robot you would like to select: ")
robot_idx_2 = get_robot_selection("Enter the index of the second robot you would like to select: ")

if robot_idx_1 == robot_idx_2:
    print("You selected the same robot twice. Please restart and select two distinct robots.")
    bow.close_client_interface()
    sys.exit(-1)

selected_robots = [available_robots[robot_idx_1], available_robots[robot_idx_2]]

# Create BOW Robot instances
robots = [bow.Robot(r) for r in selected_robots]

# Connect to each robot and open target modalities
target_modalities = ["proprioception", "motor"]
for robot in robots:
    result = robot.connect()
    if not result.Success:
        print("Could not connect with robot {}".format(robot.robot_details.robot_id))
        bow.close_client_interface()
        sys.exit(-1)

    for modality in target_modalities:
        result = robot.open_modality(modality)
        if not result.Success:
            log.info("Failed to open " + modality + " modality: " + result.Description)
            bow.close_client_interface()
            sys.exit(-1)

# Identify the first effector for each robot
effectors = []
for robot in robots:
    prop_sample = None
    while prop_sample is None:
        prop_sample, error = robot.get_modality("proprioception", True)
        if not error.Success:
            continue
        if len(prop_sample.Effectors) == 0:
            continue
        effectors.append(prop_sample.Effectors[0].EffectorLinkName)
        break

## ACT ##
circle_radius = 0.2
circleHeight = 0.3
stepSize = 0.05

while True:
    angle = 0.0
    while angle <= 2 * math.pi:
        x = circle_radius * math.cos(angle)
        y = circle_radius * math.sin(angle)
        z = circleHeight

        SendObjective(robots, effectors, x, y, z)

        angle += stepSize
        time.sleep(0.2)
