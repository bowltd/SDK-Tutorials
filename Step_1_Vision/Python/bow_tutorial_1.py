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
