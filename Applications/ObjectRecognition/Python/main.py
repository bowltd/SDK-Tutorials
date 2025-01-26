#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (c) 2023, Bettering Our Worlds (BOW) Ltd.
# All Rights Reserved
# Author: George Bridges <george.bridges@bow.ltd>

# Imports
import bow_api
import bow_data

import logging
import numpy as np
import sys
import cv2
from ultralytics import YOLO

# Create a logger for our robot connection and print version info
print(bow_api.version())

# Connect to the robot selected in BOW Hub
myrobot, error = bow_api.quick_connect(app_name="Vision - Object Detection", channels=["vision"])
if not error.Success:
    print("Failed to connect to robot", error)
    sys.exit()

# Create a flag so we can exit our main loop
stopFlag = False

# Create our YOLO object detection model
model = YOLO('yolov8n.pt')  # load an official detection model

# Define a colour for our image annotations
colour = (61, 201, 151)

try:
    while not stopFlag:
        # Sense

        # Retrieve all images from the robot using the vision modality
        image_list, err = myrobot.vision.get(True)
        # Test for failures
        if not err.Success or len(image_list.Samples) == 0:
            continue

        # For this example we will always use the first camera in the list
        img_data = image_list.Samples[0]

        # Test for new and valid data
        if img_data is not None and img_data.NewDataFlag:

            # Extract OpenCV image
            if img_data.ImageType == bow_data.ImageSample.ImageTypeEnum.RGB:
                npimage = np.frombuffer(img_data.Data, np.uint8).reshape(
                    [int(img_data.DataShape[1] * 3 / 2), img_data.DataShape[0]])
                myIm = cv2.cvtColor(npimage, cv2.COLOR_YUV2RGB_I420)
            elif img_data.ImageType == bow_data.ImageSample.ImageTypeEnum.DEPTH:
                myIm = np.frombuffer(img_data.Data, np.uint16).reshape(
                    [img_data.DataShape[1], img_data.DataShape[0]])
            else:
                continue

            # Pass image into the yolo model for object detection
            results = model.predict(source=myIm, show=False, stream_buffer=False, verbose=False)

            # Iterate though detected objects and draw them on the image
            if len(results) > 0:
                for box in results[0].boxes.cpu():
                    # Extract data from results in a useful form
                    corners = box.xyxy.numpy()[0] # Corners of the detected objects bounding box
                    classification = model.names[int(box.data[0][-1])] # models predicted object classification

                    # Draw the bounding box onto the image in our chosen colour
                    myIm = cv2.rectangle(myIm, (int(corners[0]), int(corners[1])), (int(corners[2]), int(corners[3])),
                                         colour, thickness=3)

                    # Set the label position
                    label_x = int(corners[0])
                    label_y = int(corners[1]) - 10  # Position above the box by default
                    # Check if the label is going off-screen
                    if label_y < 10:
                        label_y = int(corners[3]) + 20  # Position below the box

                    # Draw the label onto the image in our chosen colour
                    cv2.putText(myIm, classification, (label_x, label_y),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.7, colour, 1)

            # Display the image
            cv2.imshow(img_data.Source, myIm)

        # Check for keyboard escape
        j = cv2.waitKeyEx(1)
        if j == 27:
            break

# Kill on ctrl-c or closure
except KeyboardInterrupt or SystemExit:
    cv2.destroyAllWindows()
    print("Closing down")
    stopFlag = True

# Handle disconnect of robot on exit
cv2.destroyAllWindows()
myrobot.disconnect()
bow_api.close_client_interface()
