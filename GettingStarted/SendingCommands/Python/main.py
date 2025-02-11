#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (c) 2023, Bettering Our Worlds (BOW) Ltd.
# All Rights Reserved
# Author: Daniel Camilleri <daniel.camilleri@bow.ltd>

import bow_api
import bow_data
import sys
import cv2
import numpy as np
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

    for i, img_data in enumerate(images_list.Samples):
        show_image = None
        if img_data.NewDataFlag:
            image_width = int(img_data.DataShape[0])
            image_height = int(img_data.DataShape[1])

            if img_data.ImageType == bow_data.ImageSample.ImageTypeEnum.RGB:
                expected_size = image_width * image_height * 3 // 2
                if len(img_data.Data) < expected_size:
                    continue

                yuv_image = np.frombuffer(img_data.Data, np.uint8).reshape(
                    [int(img_data.DataShape[1] * 3 // 2), img_data.DataShape[0]])
                show_image = cv2.cvtColor(yuv_image, cv2.COLOR_YUV2RGB_IYUV)

            elif img_data.ImageType == bow_data.ImageSample.ImageTypeEnum.DEPTH:
                expected_size = image_width * image_height
                if len(img_data.Data) < expected_size:
                    continue

                depth_image = np.frombuffer(img_data.Data, np.uint16).reshape(
                    [img_data.DataShape[1], img_data.DataShape[0]])
                normalized_depth = cv2.normalize(depth_image, None, 0, 255, cv2.NORM_MINMAX, dtype=cv2.CV_8UC1)
                show_image = cv2.applyColorMap(normalized_depth, cv2.COLORMAP_JET)

            else:
                print("Unknown image type")

        if show_image is not None:
            if img_data.Source not in window_names.keys():
                window_name = f"RobotView{len(window_names)} - {img_data.Source}"
                print(window_name)
                window_names[img_data.Source] = window_name
                cv2.namedWindow(window_name)
                cv2.waitKey(1)

            cv2.imshow(window_names[img_data.Source], show_image)
            cv2.waitKey(1)


def keyboard_control():
    motorSample = bow_data.MotorSample()
    motorSample.Locomotion.TranslationalVelocity.X = 0
    motorSample.Locomotion.TranslationalVelocity.Y = 0
    motorSample.Locomotion.TranslationalVelocity.Z = 0
    motorSample.Locomotion.RotationalVelocity.X = 0
    motorSample.Locomotion.RotationalVelocity.Y = 0
    motorSample.Locomotion.RotationalVelocity.Z = 0
    motorSample.GazeTarget.GazeVector.X = 0
    motorSample.GazeTarget.GazeVector.Y = 0
    motorSample.GazeTarget.GazeVector.Z = 0

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
    if 'i' in pressed_keys:
        print("Look up")
        motorSample.GazeTarget.GazeVector.X = -0.2
    if 'k' in pressed_keys:
        print("Look down")
        motorSample.GazeTarget.GazeVector.X = 0.2
    if 'j' in pressed_keys:
        print("Look left")
        motorSample.GazeTarget.GazeVector.Y = 0.2
    if 'l' in pressed_keys:
        print("Look right")
        motorSample.GazeTarget.GazeVector.Y = -0.2
    if 'o' in pressed_keys:
        print("Tilt left")
        motorSample.GazeTarget.GazeVector.Z = -0.2
    if 'u' in pressed_keys:
        print("Tilt right")
        motorSample.GazeTarget.GazeVector.Z = 0.2
    return motorSample

print(bow_api.version())

myrobot, error = bow_api.quick_connect(app_name="BOW Sending Commands", channels=["vision", "motor"])
if not error.Success:
    print("Failed to connect to robot", error)
    sys.exit()

try:
    while True:
        # Sense
        image_samples, err = myrobot.vision.get(True)
        if not err.Success:
            continue

        if len(image_samples.Samples) == 0:
            continue

        show_all_images(image_samples)

        # Decide
        motorSample = keyboard_control()

        # Act
        myrobot.motor.set(motorSample)

        # Allow for cv2 window operations and refresh rate
        cv2.waitKey(1)

except KeyboardInterrupt or SystemExit:
    cv2.destroyAllWindows()
    print("Closing down")
    stopFlag = True

cv2.destroyAllWindows()
myrobot.disconnect()
bow_api.close_client_interface()
