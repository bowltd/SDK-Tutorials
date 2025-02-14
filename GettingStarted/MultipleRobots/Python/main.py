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

import bow_api
import bow_data

import sys
import cv2
import numpy as np
from pynput import keyboard

stopFlag = False
window_names = dict()

# A set to keep track of the pressed keys
pressed_keys = set()
num_robots = 2

def on_press(key):
    try:
        pressed_keys.add(key.char)
    except AttributeError:
        # Check for special keys (like spacebar)
        if key == keyboard.Key.space:
            pressed_keys.add("space")

def on_release(key):
    try:
        pressed_keys.discard(key.char)
    except AttributeError:
        # Check for special keys (like spacebar)
        if key == keyboard.Key.space:
            pressed_keys.discard("space")
    if key == keyboard.Key.esc:
        # Stop listener
        return False

def reset_locomotion(motorSample) :
    motorSample.Locomotion.TranslationalVelocity.Y = 0
    motorSample.Locomotion.TranslationalVelocity.X = 0
    motorSample.Locomotion.TranslationalVelocity.Z = 0
    motorSample.Locomotion.RotationalVelocity.X = 0
    motorSample.Locomotion.RotationalVelocity.Y = 0
    motorSample.Locomotion.RotationalVelocity.Z = 0

listener = keyboard.Listener(on_press=on_press, on_release=on_release)
listener.start()

def show_all_images(images_list):
    global window_names

    for i, img_data in enumerate(images_list):
        if len(img_data.Data) != 0:
            if img_data.NewDataFlag:
                if img_data.ImageType == bow_data.ImageSample.ImageTypeEnum.RGB:
                    npimage = np.frombuffer(img_data.Data, np.uint8).reshape(
                        [int(img_data.DataShape[1] * 3 / 2), img_data.DataShape[0]])
                    npimage = cv2.cvtColor(npimage, cv2.COLOR_YUV2RGB_I420)
                elif img_data.ImageType == bow_data.ImageSample.ImageTypeEnum.DEPTH:
                    npimage = np.frombuffer(img_data.Data, np.uint16).reshape(
                        [img_data.DataShape[1], img_data.DataShape[0]])
                else:
                    print("Unhandled image type")
                    continue

                if not window_names.__contains__(img_data.Source):
                    window_name = f"RobotView{len(window_names)} - {img_data.Source}"
                    window_names[img_data.Source] = window_name
                    cv2.namedWindow(window_name)

                cv2.imshow(window_names[img_data.Source], npimage)


def keyboard_control():
    motorSample = bow_data.MotorSample()
    if 'w' in pressed_keys:
        print("Moving forward")
        motorSample.Locomotion.TranslationalVelocity.X = 0.2
    if 's' in pressed_keys:
        print("Moving backward")
        motorSample.Locomotion.TranslationalVelocity.X = -0.2
    if 'd' in pressed_keys:
        print("Rotate right")
        motorSample.Locomotion.RotationalVelocity.Z = -1
    if 'a' in pressed_keys:
        print("Rotate left")
        motorSample.Locomotion.RotationalVelocity.Z = 1
    if 'e' in pressed_keys:
        print("Strafe right")
        motorSample.Locomotion.TranslationalVelocity.Y = -1
    if 'q' in pressed_keys:
        print("Strafe left")
        motorSample.Locomotion.TranslationalVelocity.Y = 1
    if 'space' in pressed_keys:
        print("Stop moving")
        reset_locomotion(motorSample)
    if 'i' in pressed_keys:
        print("Look up")
        motorSample.GazeTarget.GazeVector.Y = -0.2
    if 'k' in pressed_keys:
        print("Look down")
        motorSample.GazeTarget.GazeVector.Y = 0.2
    if 'j' in pressed_keys:
        print("Look left")
        motorSample.GazeTarget.GazeVector.X = -0.2
    if 'l' in pressed_keys:
        print("Look right")
        motorSample.GazeTarget.GazeVector.X = 0.2
    if 'o' in pressed_keys:
        print("Tilt left")
        motorSample.GazeTarget.GazeVector.Z = -0.2
    if 'u' in pressed_keys:
        print("Tilt right")
        motorSample.GazeTarget.GazeVector.Z = 0.2
    return motorSample

# Prompt user to select two robots by their index from the displayed list of available robots
def get_robot_selection(prompt, selected):
    while True:
        try:
            idx = int(input(prompt))
            if 0 <= idx < len(get_robots_result.robots):
                if idx in selected:
                    print("Cannot choose the same robot again")
                    continue
                return idx
            else:
                print("Invalid index. Please try again.")
        except ValueError:
            print("Invalid input. Please enter a valid integer index.")

print(bow_api.version())

# Setup the BOW Client
setup_result = bow_api.setup(app_name="Multiple Robots", verbose=True)
if not setup_result.Success:
    sys.exit(-1)

# Login to BOW using systray login
login_result = bow_api.login_user("", "", True)
if login_result.Success:
    print("Logged in")
else:
    sys.exit(-1)

# Get robots
get_robots_result = bow_api.get_robots(get_local=True, get_remote=True, get_bow_hub=False)
if not get_robots_result.localSearchError.Success:
   print(get_robots_result.localSearchError.Description)

if not get_robots_result.remoteSearchError.Success:
    print(get_robots_result.remoteSearchError.Description)

if len(get_robots_result.robots) == 0:
    print("No Robots found")
    bow_api.close_client_interface()
    sys.exit(-1)

# Filter out only the available robots
available_robots = [r for r in get_robots_result.robots if r.robot_state.available]

# Print out all found robots and whether they are available
print("Robots discovered:")
for i, robot in enumerate(available_robots):
    print(f"{i}: {robot.name}")

if len(available_robots) < num_robots:
    print(f"Not enough available robots. {num_robots} Expected.")
    bow_api.close_client_interface()
    sys.exit(-1)

robot_indices = []
for i in range(num_robots):
    robot_indices.append(get_robot_selection(f"Select robot {i+1} of {num_robots}: ", robot_indices))

# Create BOW Robot instances
robots = [bow_api.Robot(available_robots[ridx]) for ridx in robot_indices]

# Connect to each robot and open target modalities
target_channels = ["vision", "motor"]
for robot in robots:
    result = robot.connect()
    if not result.Success:
        print("Could not connect with robot {}".format(robot.robot_details.robot_id))
        bow_api.close_client_interface()
        sys.exit(-1)

    for channel in target_channels:
        result = robot.open_channel(channel)
        if not result.Success:
            print("Failed to open " + channel + " channel: " + result.Description)
            bow_api.close_client_interface()
            sys.exit(-1)

try:
    while True:
        # Sense
        all_images = []
        skip = False
        for robot in robots:
            robot_images, err = robot.vision.get(True)
            if err.Success and robot_images is not None:
                for image in robot_images.Samples:
                    image.Source = f"{robot.robot_details.name}_{image.Source}"
                    all_images.append(image)

        if len(all_images) > 0:
            show_all_images(all_images)

        # Decide
        motorSample = keyboard_control()

        # Act
        for r in robots:
            r.motor.set(motorSample)

        # Allow for cv2 window operations and refresh rate
        cv2.waitKey(1)

except KeyboardInterrupt or SystemExit:
    cv2.destroyAllWindows()
    print("Closing down")
    stopFlag = True

cv2.destroyAllWindows()
for r in robots:
    r.disconnect()
bow_api.stop_engine()
