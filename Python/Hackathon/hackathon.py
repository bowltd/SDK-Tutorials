#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (c) 2023, Bettering Our Worlds (BOW) Ltd.
# All Rights Reserved
# Author: Daniel Camilleri <daniel.camilleri@bow.ltd>

import bow_client as bow
import bow_utils
import bow_utils as utils
import sys
import logging
import numpy as np
import random
import cv2
import time
from pynput import keyboard


def on_press(key):

    cartesian_update = False
    global gripperState, cartesianTarget
    motor_sample = utils.MotorSample()
    motor_sample.Head.X = 0
    motor_sample.Head.Y = 0
    motor_sample.Head.Z = 0
    motor_sample.Locomotion.Position.X = 0
    motor_sample.Locomotion.Position.Y = 0
    motor_sample.Locomotion.Rotation.Z = 0
    motor_sample.EndEffectors.extend([utils.EndEffector(), utils.EndEffector()])

    if key == keyboard.Key.up:
        print("Head Up")
        motor_sample.Head.Y = -20
    elif key == keyboard.Key.down:
        print("Head Down")
        motor_sample.Head.Y = 20

    elif key == keyboard.Key.left:
        print("Head Left")
        motor_sample.Head.X = 20
    elif key == keyboard.Key.right:
        print("Head Right")
        motor_sample.Head.X = -20

    elif hasattr(key, 'char'):

        if key.char == "w":
            print("Locomotion Forward")
            motor_sample.Locomotion.Position.X = 1
        elif key.char == "s":
            print("Locomotion Backward")
            motor_sample.Locomotion.Position.X = -1

        elif key.char == "a":
            print("Locomotion Rotate Left")
            motor_sample.Locomotion.Rotation.Z = 0.5
        elif key.char == "d":
            print("Locomotion Rotate Right")
            motor_sample.Locomotion.Rotation.Z = -0.5

        elif key.char == "q":
            print("Locomotion Left")
            motor_sample.Locomotion.Position.Y = 1
        elif key.char == "e":
            print("Locomotion Right")
            motor_sample.Locomotion.Position.Y = -1

    if cartesian_update:
        log.info(f"{cartesianTarget.X} {cartesianTarget.Y} {cartesianTarget.Z}")

    motor_sample.EndEffectors[0].Name = "LeftArm"
    motor_sample.EndEffectors[0].Enabled = False
    motor_sample.EndEffectors[0].ControlMode = bow_utils.CUSTOM

    motor_sample.EndEffectors[1].Name = "RightArm"
    motor_sample.EndEffectors[1].Enabled = False
    motor_sample.EndEffectors[1].ControlMode = bow_utils.CUSTOM

    ret = myrobot.set_modality("motor", motor_sample)

stopFlag = False

log = utils.create_logger("MyBOWApp", logging.INFO)
log.info(bow.version())

myrobot, error = bow.quick_connect(pylog=log, modalities=["vision", "motor"])

# Create listener objects
listener = keyboard.Listener(on_press=on_press)

# Start the listener
listener.start()

window_names = []
try:
    windows_created = False
    while listener.is_alive():
        image_list, err = myrobot.get_modality("vision", True)
        if err.Success:
            if len(image_list) > 0:

                # Create windows only once
                if not windows_created:
                    for i in range(len(image_list)):
                        window_name = f"RobotView{i} - {image_list[i].source}"
                        window_names.append(window_name)
                        cv2.namedWindow(window_name)
                    windows_created = True  # Set the flag to true

                # Display images in created windows
                for i, img_data in enumerate(image_list):
                    myim = img_data.image
                    cv2.cvtColor(myim, cv2.COLOR_RGB2BGR, myim)
                    cv2.imshow(window_names[i], myim)

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
    bow.close_client_interface()
    sys.exit(-1)

myrobot.disconnect()
bow.close_client_interface()
