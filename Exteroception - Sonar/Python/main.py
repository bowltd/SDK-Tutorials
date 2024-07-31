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


def identify_front_sonar(range_sensors):
    sonars = []
    for sensor in range_sensors:
        if sensor.OperationType == bow_utils.Range.OperationTypeEnum.Ultrasound:
            sonars.append(sensor)

    front_sonar_x_pos = -100.0
    front_sonar_name = None
    for sonar in sonars:
        if sonar.Transform.Position.X > front_sonar_x_pos:
            front_sonar_x_pos = sonar.Transform.Position.X
            front_sonar_name = sonar.Source

    return front_sonar_name


log = bow_utils.create_logger("Bow Tutorial: Exteroception - Sonar", logging.INFO)
log.info(bow.version())

myrobot, error = bow.quick_connect(pylog=log, modalities=["vision", "motor", "exteroception"])
if not error.Success:
    log.error("Failed to connect to robot", error)
    sys.exit()

ext_sample, err = myrobot.get_modality("exteroception", True)
while not err.Success:
    ext_sample, err = myrobot.get_modality("exteroception", True)
    time.sleep(0.1)

print(ext_sample)
front_sonar = identify_front_sonar(ext_sample.Range)

try:
    while not stopFlag:
        # Sense
        # Vision
        image_list, err = myrobot.get_modality("vision", True)
        if not err.Success:
            continue

        if len(image_list) == 0:
            continue

        show_all_images(image_list)

        # Exteroception
        ext_sample, err = myrobot.get_modality("exteroception", True)
        if not err.Success or ext_sample is None:
            continue

        # Extract the Sonar sensor data
        sonar = None
        for range_sensor in ext_sample.Range:
            if range_sensor.Source == front_sonar:
                sonar = range_sensor

        motor_command = bow_utils.MotorSample()

        if sonar.Data == -1:
            print("Invalid Sonar Data")
            motor_command.Locomotion.RotationalVelocity.Z = 1

        elif sonar.Data == 0:
            print("No obstruction in range")
            motor_command.Locomotion.TranslationalVelocity.X = 1

        elif 0 < sonar.Data < sonar.Min + 1:
            print("Obstruction approaching sensor minimum")
            motor_command.Locomotion.RotationalVelocity.Z = 1

        else:
            print("Obstruction detected at safe range")
            motor_command.Locomotion.TranslationalVelocity.X = 1

        myrobot.set_modality("motor", motor_command)

        j = cv2.waitKeyEx(1)
        if j == 27:
            break

except KeyboardInterrupt or SystemExit:
    cv2.destroyAllWindows()
    log.info("Closing down")
    stopFlag = True

cv2.destroyAllWindows()
myrobot.disconnect()
bow.close_client_interface()
