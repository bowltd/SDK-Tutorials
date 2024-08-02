#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (c) 2023, Bettering Our Worlds (BOW) Ltd.
# All Rights Reserved
# Author: George Bridges <george.bridges@bow.ltd>
import time

# Imports
import bow_client as bow
import bow_utils
import sys
import logging
import cv2

stopFlag = False
window_names = dict()
windows_created = False
rate = 10


def show_all_images(images_list):
    global windows_created, window_names
    # Create a window to display images from each camera on first call
    if not windows_created:
        for i in range(len(images_list)):
            window_name = f"RobotView{i} - {images_list[i].source}"
            window_names[images_list[i].source] = window_name
            cv2.namedWindow(window_name)
        windows_created = True

    # display each image in its window
    for i, img_data in enumerate(images_list):
        myim = img_data.image
        if img_data.new_data_flag:
            cv2.imshow(window_names[img_data.source], myim)


def identify_front_sonar(range_sensors):
    # Iterate through all range sensors and identify the sonar sensors
    sonars = []
    for sensor in range_sensors:
        if sensor.OperationType == bow_utils.Range.OperationTypeEnum.Ultrasound:
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
log = bow_utils.create_logger("Exteroception - Sonar", logging.INFO)
log.info(bow.version())

myrobot, error = bow.quick_connect(pylog=log, modalities=["vision", "motor", "exteroception"])
if not error.Success:
    log.error("Failed to connect to robot", error)
    sys.exit()

# Wait for a valid exteroception sample
ext_sample, err = myrobot.get_modality("exteroception", True)
while not err.Success:
    ext_sample, err = myrobot.get_modality("exteroception", True)
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
        image_list, err = myrobot.get_modality("vision", True)
        if not err.Success or len(image_list) == 0:
            continue
        show_all_images(image_list)

        ##### Exteroception #####
        # Get exteroception sample and check for valid result
        ext_sample, err = myrobot.get_modality("exteroception", True)
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
        motor_command = bow_utils.MotorSample()

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
        myrobot.set_modality("motor", motor_command)

        # Delay to control the rate of loop execution
        j = cv2.waitKeyEx(delay_ms)
        if j == 27:
            break

except KeyboardInterrupt or SystemExit:
    cv2.destroyAllWindows()
    log.info("Closing down")
    stopFlag = True

cv2.destroyAllWindows()
myrobot.disconnect()
bow.close_client_interface()
