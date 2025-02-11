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

def show_all_images(images_list):
    global window_names

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


print(bow_api.version())

myrobot, error = bow_api.quick_connect(app_name="BOW Streaming Data", channels=["vision"])
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

        if len(image_samples.Samples) == 0:
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
bow_api.stop_engine()
