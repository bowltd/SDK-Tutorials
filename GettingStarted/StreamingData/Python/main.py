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

stopFlag = False
window_names = dict()
windows_created = False

def show_all_images(images_list):
    global windows_created, window_names

    if not windows_created:
        for i in range(len(images_list)):
            window_name = f"RobotView{i} - {images_list[i].Source}"
            window_names[images_list[i].Source] = window_name
            cv2.namedWindow(window_name)
        windows_created = True

    for i, img_data in enumerate(images_list):
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



print(bow_api.version())

myrobot, error = bow_api.quick_connect(app_name="BOW Streaming Data", modalities=["vision"])
if not error.Success:
    print("Failed to connect to robot", error)
    sys.exit()

try:
    while True:
        # Sense
        image_samples, err = myrobot.vision.get(True)
        if not err.Success:
            print(err.Description)
            continue

        if len(image_samples) == 0:
            continue
        show_all_images(image_samples)

        j = cv2.waitKeyEx(1)
        if j == 27:
            break

except KeyboardInterrupt or SystemExit:
    cv2.destroyAllWindows()
    print("Closing down")
    stopFlag = True

cv2.destroyAllWindows()
myrobot.disconnect()
bow_api.close_client_interface()
