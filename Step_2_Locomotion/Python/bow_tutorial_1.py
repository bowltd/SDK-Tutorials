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

log = bow_utils.create_logger("Bow Tutorial 1", logging.INFO)
log.info(bow.version())

myrobot, error = bow.quick_connect(pylog=log, modalities=["vision", "motor"])

window_names = []
try:
    windows_created = False
    while True:
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
