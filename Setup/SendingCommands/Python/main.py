#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (c) 2023, Bettering Our Worlds (BOW) Ltd.
# All Rights Reserved
# Author: Daniel Camilleri <daniel.camilleri@bow.ltd>
import time

import bow_client as bow
import bow_utils
import sys
import logging
import cv2
from pynput import keyboard

stopFlag = False
window_names = dict()
windows_created = False

# A set to keep track of the pressed keys
pressed_keys = set()

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
    global windows_created, window_names

    if not windows_created:
        for i in range(len(images_list)):
            window_name = f"RobotView{i} - {images_list[i].source}"
            window_names[images_list[i].source] = window_name
            cv2.namedWindow(window_name)
        windows_created = True

    for i, img_data in enumerate(images_list):
        myim = img_data.image
        if img_data.new_data_flag:
            cv2.imshow(window_names[img_data.source], myim)


log = bow_utils.create_logger("Bow Tutorial 2", logging.INFO)
log.info(bow.version())

myrobot, error = bow.quick_connect(pylog=log, modalities=["vision", "motor"])
if not error.Success:
    log.error("Failed to connect to robot", error)
    sys.exit()

try:
    while True:
        # Sense
        image_list, err = myrobot.get_modality("vision", True)
        if not err.Success:
            continue

        if len(image_list) == 0:
            continue

        show_all_images(image_list)

        # Decide
        motorSample = bow_utils.MotorSample()
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
            # reset_locomotion(motorSample)
            motorSample.GazeTarget.GazeVector.Y = -0.2
        if 'k' in pressed_keys:
            print("Look down")
            # reset_locomotion(motorSample)
            motorSample.GazeTarget.GazeVector.Y = 0.2
        if 'j' in pressed_keys:
            print("Look left")
            # reset_locomotion(motorSample)
            motorSample.GazeTarget.GazeVector.X = -0.2
        if 'l' in pressed_keys:
            print("Look right")
            # reset_locomotion(motorSample)
            motorSample.GazeTarget.GazeVector.X = 0.2
        if 'o' in pressed_keys:
            print("Tilt left")
            # reset_locomotion(motorSample)
            motorSample.GazeTarget.GazeVector.Z = -0.2
        if 'u' in pressed_keys:
            print("Tilt right")
            # reset_locomotion(motorSample)
            motorSample.GazeTarget.GazeVector.Z = 0.2

        # Act
        myrobot.set_modality("motor", motorSample)

        # Allow for cv2 window operations and refresh rate
        cv2.waitKey(1)

except KeyboardInterrupt or SystemExit:
    cv2.destroyAllWindows()
    log.info("Closing down")
    stopFlag = True

cv2.destroyAllWindows()
myrobot.disconnect()
bow.close_client_interface()
