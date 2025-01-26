#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (c) 2023, Bettering Our Worlds (BOW) Ltd.
# All Rights Reserved
# Author: George Bridges <george.bridges@bow.ltd>
import time

# Imports
import bow_api
import bow_data

import sys
import logging
import cv2
import numpy as np

stopFlag = False
window_names = dict()
windows_created = False
rate = 10


def show_all_images(images_list):
    global windows_created, window_names

    if not windows_created:
        for i in range(len(images_list.Samples)):
            window_name = f"RobotView{i} - {images_list.Samples[i].Source}"
            window_names[images_list.Samples[i].Source] = window_name
            cv2.namedWindow(window_name)
        windows_created = True

    for i, img_data in enumerate(images_list.Samples):
        if len(img_data.Data) != 0:
            if img_data.NewDataFlag:
                if img_data.ImageType == bow_data.ImageSample.ImageTypeEnum.RGB:
                    npimage = np.frombuffer(img_data.Data, np.uint8).reshape(
                        [int(img_data.DataShape[1] * 3 / 2), img_data.DataShape[0]])
                    npimage = cv2.cvtColor(npimage, cv2.COLOR_YUV2RGB_I420)
                    cv2.imshow(window_names[img_data.Source], npimage)
                elif img_data.ImageType == bow_data.ImageSample.ImageTypeEnum.DEPTH:
                    npimage = np.frombuffer(img_data.Data, np.uint16).reshape(
                        [img_data.DataShape[1], img_data.DataShape[0]])
                    cv2.imshow(window_names[img_data.Source], npimage)
                else:
                    print("Unhandled image type")



def identify_front_sonar(range_sensors):
    # Iterate through all range sensors and identify the sonar sensors
    sonars = []
    for sensor in range_sensors:
        if sensor.OperationType == bow_data.Range.OperationTypeEnum.Ultrasound:
            sonars.append(sensor)

    # Iterate through the sonars and find the sensor with the largest X position (furthest forward)
    front_sonar_x_pos = -100.0
    front_sonar_name = None
    for sonar in sonars:
        if sonar.Transform.Position.X > front_sonar_x_pos:
            front_sonar_x_pos = sonar.Transform.Position.X
            front_sonar_name = sonar.Source

    # Return the name of the forward most sonar sensor
    return front_sonar_name

# Standard robot quick connection procedure
print(bow_api.version())

myrobot, error = bow_api.quick_connect(app_name="Obstacle Avoidance", channels=["vision", "motor", "exteroception"])
if not error.Success:
    print("Failed to connect to robot", error)
    sys.exit()

# Wait for a valid exteroception sample
ext_sample, err = myrobot.exteroception.get(True)
while not err.Success:
    ext_sample, err = myrobot.exteroception.get(True)
    time.sleep(0.1)

# Identify the forward most sonar sensor
front_sonar = identify_front_sonar(ext_sample.Range)

# Calculate delay needed for rate of loop execution
delay = 1/rate
delay_ms = int(delay * 1000)

# Main Loop
try:
    while not stopFlag:
        # SENSE
        ##### Vision #####
        # Get and display all images
        image_list, err = myrobot.vision.get(True)
        if not err.Success or len(image_list.Samples) == 0:
            continue
        show_all_images(image_list)

        ##### Exteroception #####
        # Get exteroception sample and check for valid result
        ext_sample, err = myrobot.exteroception.get(True)
        if not err.Success or ext_sample is None:
            continue

        # Iterate through range sensors until front sensor
        sonar = None
        for range_sensor in ext_sample.Range:
            if range_sensor.Source == front_sonar:
                sonar = range_sensor
                break

        # DECIDE

        # Create a motor message to populate
        motor_command = bow_data.MotorSample()

        # Base the velocity command on the sonar reading
        if sonar.Data == -1:
            print("Invalid Sonar Data: ", sonar.Data, " meters")
            motor_command.Locomotion.RotationalVelocity.Z = 0.5

        elif sonar.Data == 0:
            print("No obstruction in range: ", sonar.Data, " meters")
            motor_command.Locomotion.TranslationalVelocity.X = 0.2

        elif sonar.Min + 0.5 < sonar.Data < sonar.Min + 1.5:
            print("Obstruction approaching sensor minimum: ", sonar.Data, " meters")
            motor_command.Locomotion.RotationalVelocity.Z = 0.5

        elif sonar.Data < sonar.Min + 0.5:
            print("Obstruction too close to maneuver, reverse: ", sonar.Data, " meters")
            motor_command.Locomotion.RotationalVelocity.X = -0.2

        else:
            print("Obstruction detected at safe range", sonar.Data, " meters")
            motor_command.Locomotion.TranslationalVelocity.X = 0.2

        # ACT
        # Send the motor command
        myrobot.motor.set(motor_command)

        # Delay to control the rate of loop execution
        j = cv2.waitKeyEx(delay_ms)
        if j == 27:
            break

except KeyboardInterrupt or SystemExit:
    cv2.destroyAllWindows()
    print("Closing down")
    stopFlag = True

cv2.destroyAllWindows()
myrobot.disconnect()
bow_api.close_client_interface()
