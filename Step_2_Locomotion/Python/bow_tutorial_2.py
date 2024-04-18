#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (c) 2023, Bettering Our Worlds (BOW) Ltd.
# All Rights Reserved
# Author: Daniel Camilleri <daniel.camilleri@bow.ltd>

import bow_client as bow
import bow_utils
import sys
import logging
import numpy as np
import random
import cv2
import time

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


log = bow_utils.create_logger("Bow Tutorial 1", logging.INFO)
log.info(bow.version())

myrobot, error = bow.quick_connect(pylog=log, modalities=["vision", "motor"])

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
        decision = cv2.waitKey(1)

        # Act
        motorSample = bow_utils.MotorSample()
        if decision > 0:
            if decision == ord('w'):
                print("Moving forward")
                motorSample.Locomotion.TranslationalVelocity.X = 1
            elif decision == ord('s'):
                print("Moving backward")
                motorSample.Locomotion.TranslationalVelocity.X = -1
            elif decision == ord('d'):
                print("Rotate right")
                motorSample.Locomotion.RotationalVelocity.Z = -1
            elif decision == ord('a'):
                print("Rotate left")
                motorSample.Locomotion.RotationalVelocity.Z = 1
            elif decision == ord('e'):
                print("Strafe right")
                motorSample.Locomotion.TranslationalVelocity.Y = -1
            elif decision == ord('q'):
                print("Strafe left")
                motorSample.Locomotion.TranslationalVelocity.Y = 1
        myrobot.set_modality("motor", motorSample)


except KeyboardInterrupt or SystemExit:
    cv2.destroyAllWindows()
    log.info("Closing down")
    stopFlag = True

cv2.destroyAllWindows()
myrobot.disconnect()
bow.close_client_interface()
