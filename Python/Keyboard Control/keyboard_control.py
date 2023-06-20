#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (c) 2023, Bettering Our Worlds (BOW) Ltd.
# All Rights Reserved
# Author: Daniel Camilleri <daniel.camilleri@bow.ltd>

import animus_client as animus
import animus_utils
import animus_utils as utils
import sys
import logging
import numpy as np
import random
import cv2
import time
from pynput import keyboard


def on_press(key):

    global angleArray, angleIndex
    motor_sample = utils.PyMotorSample()
    motor_sample.head = utils.AnimusVector3()
    motor_sample.head.x = 0
    motor_sample.head.y = 0
    motor_sample.head.z = 0
    motor_sample.locomotion = utils.Locomotion()
    motor_sample.locomotion.Position.x = 0
    motor_sample.locomotion.Position.y = 0
    motor_sample.locomotion.Position.z = 0
    motor_sample.locomotion.Rotation.x = 0
    motor_sample.locomotion.Rotation.y = 0
    motor_sample.locomotion.Rotation.z = 0
    motor_sample.end_effectors = [utils.EndEffector(), utils.EndEffector()]

    if key == keyboard.Key.up:
        print("Head Up")
        motor_sample.head.y = -20
    elif key == keyboard.Key.down:
        print("Head Down")
        motor_sample.head.y = 20
    elif key == keyboard.Key.left:
        print("Head Left")
        motor_sample.head.x = 20
    elif key == keyboard.Key.right:
        print("Head Right")
        motor_sample.head.x = -20

    elif key.char == "w":
        print("Locomotion Forward")
        motor_sample.locomotion.Position.x = 1
    elif key.char == "s":
        print("Locomotion Backward")
        motor_sample.locomotion.Position.x = -1
    elif key.char == "a":
        print("Locomotion Rotate Left")
        motor_sample.locomotion.Rotation.z = 2
    elif key.char == "d":
        print("Locomotion Rotate Right")
        motor_sample.locomotion.Rotation.z = -2

    elif key.char == "a":
        print("Locomotion Rotate Left")
        motor_sample.locomotion.Rotation.z = 2
    elif key.char == "d":
        print("Locomotion Rotate Right")
        motor_sample.locomotion.Rotation.z = -2

    elif key.char == "q":
        print("Locomotion Left")
        motor_sample.locomotion.Position.y = 1
    elif key.char == "e":
        print("Locomotion Right")
        motor_sample.locomotion.Position.y = -1

    elif key.char == "z":
        print("Locomotion Up")
        motor_sample.locomotion.Position.z = 1
    elif key.char == "c":
        print("Locomotion Down")
        motor_sample.locomotion.Position.z = -1

    elif key.char == "t":
        angleArray[angleIndex] += 0.2
    elif key.char == "g":
        angleArray[angleIndex] -= 0.2
    elif key.char == "r":
        angleIndex += 1
        if angleIndex > 6:
            angleIndex = 0
    else:
    	pass

    motor_sample.end_effectors[0].name = "Arm"
    motor_sample.end_effectors[0].enabled = True
    motor_sample.end_effectors[0].angles.extend(angleArray)
    motor_sample.end_effectors[0].angle_units = utils.RADIANS
    motor_sample.end_effectors[0].gripper.thumb = 0
    motor_sample.end_effectors[1].name = "Arm"
    motor_sample.end_effectors[1].enabled = True
    motor_sample.end_effectors[1].angles.extend(angleArray)
    motor_sample.end_effectors[1].angle_units = utils.RADIANS
    motor_sample.end_effectors[1].gripper.thumb = 0
    motor_sample.end_effectors[1].gripper.index = 0
    motor_sample.end_effectors[1].gripper.middle = 0
    motor_sample.end_effectors[1].gripper.ring = 0
    motor_sample.end_effectors[1].gripper.pinky = 0
    motor_sample.playback_flag = False

    ret = myrobot.set_modality("motor", motor_sample)

stopFlag = False

log = utils.create_logger("MyAnimusApp", logging.INFO)
log.info(animus.version())

audio_params = utils.AudioParams(
    Backends=["notinternal"],
    SampleRate=16000,
    Channels=1,
    SizeInFrames=True,
    TransmitRate=30
)

setup_result = animus.setup(audio_params, "Python3AnimusBasics", True)
if not setup_result.success:
    sys.exit(-1)

login_result = animus.login_user("", "", True)
if login_result.success:
    log.info("Logged in")
else:
    sys.exit(-1)

get_robots_result = animus.get_robots(True, True, True)
if not get_robots_result.localSearchError.success:
    log.error(get_robots_result.localSearchError.description)

if not get_robots_result.remoteSearchError.success:
    log.error(get_robots_result.remoteSearchError.description)

if len(get_robots_result.robots) == 0:
    log.info("No Robots found")
    animus.close_client_interface()
    sys.exit(-1)

chosen_robot_details = get_robots_result.robots[0]

myrobot = animus.Robot(chosen_robot_details)
connected_result = myrobot.connect()
if not connected_result.success:
    print("Could not connect with robot {}".format(myrobot.robot_details.robot_id))
    animus.close_client_interface()
    sys.exit(-1)


open_success = myrobot.open_modality("vision")
if not open_success:
    log.error("Could not open robot vision modality")
    sys.exit(-1)

open_success = myrobot.open_modality("motor")
if not open_success:
    log.error("Could not open robot motor modality")
    sys.exit(-1)

open_result = myrobot.open_modality("audition")
if not open_result.success:
    log.error("Could not open robot audition modality")
    sys.exit(-1)

open_result = myrobot.open_modality("voice")
if not open_result.success:
    log.error("Could not open robot audition modality")
    sys.exit(-1)

angleArray = [-1.1, 1.47, 2.71, 1.71, -1.57, 1.39, 0]
angleIndex = 0

# Create listener objects
listener = keyboard.Listener(on_press=on_press)

# Start the listener
listener.start()

cv2.namedWindow("RobotView")
try:
    while listener.is_alive():
        image_list, err = myrobot.get_modality("vision", True)
        if err.success:
            if len(image_list) > 0:
                myim = image_list[0].image
                cv2.cvtColor(myim, cv2.COLOR_RGB2BGR, myim)
                cv2.imshow("RobotView", myim)
                j = cv2.waitKeyEx(1)
                if j == 27:
                    break

except KeyboardInterrupt:
    cv2.destroyAllWindows()
    log.info("Closing down")
    stopFlag = True
except SystemExit:
    cv2.destroyAllWindows()
    log.info("Closing down")
    stopFlag = True

cv2.destroyAllWindows()
if stopFlag:
    myrobot.disconnect()
    animus.close_client_interface()
    sys.exit(-1)

myrobot.disconnect()
animus.close_client_interface()
