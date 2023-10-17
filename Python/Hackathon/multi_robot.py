# -*- coding: utf-8 -*-
# Copyright (c) 2023, Bettering Our Worlds (BOW) Ltd.
# All Rights Reserved
# Author: Daniel Camilleri <daniel.camilleri@bow.ltd>

import bow_client as bow
import bow_utils as utils
import sys
import logging
import numpy as np
import random
from typing import cast, List
import cv2
import time

stopFlag = False

log = utils.create_logger("MyBOWApp", logging.INFO)
log.info(bow.version())

audio_params = utils.AudioParams(
            Backends=["notinternal"],
            SampleRate=16000,
            Channels=1,
            SizeInFrames=True,
            TransmitRate=30
        )

setup_result = bow.setup(audio_params, "Python3BowBasics", True)
if not setup_result.Success:
    sys.exit(-1)

login_result = bow.login_user("", "", True)
if login_result.Success:
    log.info("Logged in")
else:
    sys.exit(-1)

get_robots_result = bow.get_robots(True, True, False)
if not get_robots_result.localSearchError.Success:
    log.error(get_robots_result.localSearchError.Description)

if not get_robots_result.remoteSearchError.Success:
    log.error(get_robots_result.remoteSearchError.Description)

if len(get_robots_result.robots) == 0:
    log.info("No Robots found")
    bow.close_client_interface()
    sys.exit(-1)


# Select your robots from get_robots_result.robots by name
# Here we are just grabbing the first robot
chosen_robot1 = get_robots_result.robots[0]
chosen_robot2 = get_robots_result.robots[1]

robot1 = bow.Robot(chosen_robot1) # Miro 1 Robot
connected_result = robot1.connect()
if not connected_result.Success:
    print("Could not connect with robot {}".format(robot1.robot_details.robot_id))
    bow.close_client_interface()
    sys.exit(-1)
open_result = robot1.open_modality("audition")
if not open_result.Success:
    log.error("Could not open robot audition modality")
    sys.exit(-1)

open_result = robot1.open_modality("voice")
if not open_result.Success:
    log.error("Could not open robot voice modality")
    sys.exit(-1)

robot2 = bow.Robot(chosen_robot2) # Miro 1 Robot
connected_result = robot2.connect()
if not connected_result.Success:
    print("Could not connect with robot {}".format(robot2.robot_details.robot_id))
    bow.close_client_interface()
    sys.exit(-1)
open_result = robot2.open_modality("audition")
if not open_result.Success:
    log.error("Could not open robot audition modality")
    sys.exit(-1)

open_result = robot2.open_modality("voice")
if not open_result.Success:
    log.error("Could not open robot voice modality")
    sys.exit(-1)

try:
    while True:
        audio_data, error = robot1.get_modality("audition")
        robot2.set_modality("voice", audio_data)

        audio_data2, error = robot2.get_modality("audition")
        robot1.set_modality("voice", audio_data)
except KeyboardInterrupt:
    log.info("Closing down")
    stopFlag = True
except SystemExit:
    log.info("Closing down")
    stopFlag = True

if stopFlag:
    robot1.disconnect()
    robot2.disconnect()
    bow.close_client_interface()
    sys.exit(-1)

robot1.disconnect()
robot2.disconnect()
bow.close_client_interface()
