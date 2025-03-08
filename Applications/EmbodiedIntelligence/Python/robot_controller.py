import sys

import bow_api
import bow_data

import time
import logging


class RobotController:
    def __init__(self):
        self.log = bow_data.create_logger("BOW x OpenAI", logging.INFO)
        self.log.info(bow_api.version())
        self.audio_params = bow_data.AudioParams(
            Backends=["alsa"],
            SampleRate=16000,
            Channels=1,
            SizeInFrames=True,
            TransmitRate=30
        )

        # Camera params
        self.VFOV = None
        self.HFOV = None

        # Target Def
        self.prevTargetClass = None
        self.targetClass = None
        self.object_list = []

        # Search Configuration
        self.searchVelocity = 0.4  # The Angular velocity commanded during a search
        self.searchPeriod = 1  # The length of time in seconds the robot will rotate/pause for as it searches
        self.searchCounterLim = 10  # The number of search periods the robot will go through before aborting the search
        self.frameCountTarget = 3  # The number of consecutive frames containing the target object for search success

        # Search Init
        self.search = False
        self.pause = False
        self.startSearchTime = None
        self.prevTime = 0.0
        self.searchComplete = None
        self.periodCounter = 0
        self.frameCounter = 0

        # Rotate Init
        self.rotateStopTime = 0.0
        self.locoYaw = 0.0
        self.dir = 1
        self.safetyDelay = 0.5

        # Connect to robot
        self.robot, error = bow_api.quick_connect(app_name=self.log.name,
                                                  channels=["vision", "motor", "speech"],
                                                  verbose=False,
                                                  audio_params=self.audio_params)

        if error is not None and error.Success is False:
            self.log.error(error)
            sys.exit(1)

        print(self.robot.details.robot_config.input_modalities)
        print(self.robot.details.robot_config.output_modalities)

        # Initialise robot orientation (repeat until successful)
        while not self.resetLoco().Success:
            time.sleep(0.2)
            print("Trying Again...")

        # Wait for sim to stabilise?
        time.sleep(1)
        self.robot.speech.set("ChatGPT embodied successfully")

    def resetLoco(self):
        self.locoYaw = 0.0
        ret = self.update()
        return ret

    def update(self):
        # Update any ongoing motor actions
        if self.search:
            self.updateSearch()

        # Create New motor message
        motor_sample = bow_data.MotorSample()

        # Populate message with locomotion velocities
        motor_sample.Locomotion.RotationalVelocity.Z = self.locoYaw

        # Send Motor message to robot
        ret = self.robot.motor.set(motor_sample)
        if not ret.Success:
            print(ret)
        return ret

    def stop(self):
        print("Stop command received")
        self.search = False
        self.prevTargetClass = self.targetClass
        self.targetClass = None
        self.pause = False
        self.rotateStopTime = time.time()
        self.resetLoco()
        return True

    def startSearch(self, target, searchDir):
        print("Start search command received")

        # Reset State
        self.stop()
        time.sleep(2)

        # Initialise Search
        self.search = True
        self.targetClass = target
        self.pause = False
        self.searchComplete = None
        self.startSearchTime = time.time()
        self.rotateStopTime = time.time() + self.searchPeriod
        self.periodCounter = 0
        self.frameCounter = 0
        if searchDir == "right":
            self.dir = -1
        else:
            self.dir = 1
        return True

    def updateSearch(self):
        targetObj = None
        current_time = time.time() - self.startSearchTime
        step = current_time - self.prevTime

        # Check if search has exceeded length limit
        if self.periodCounter >= self.searchCounterLim:
            print(" Failed to locate " + self.targetClass + " after " + str(self.periodCounter) + " passes.")
            self.search = False
            self.searchComplete = "failure"
            self.stop()
            return

        # Only perform operations at 10Hz
        if step >= 0.1:
            self.prevTime = current_time

            # Look for target object in detections
            for obj in self.object_list:
                if obj.classification == self.targetClass:
                    targetObj = obj

            # Increment counter if object is in current detections and reset if not
            if targetObj is not None:
                self.frameCounter += 1
            else:
                self.frameCounter = 0

            # Test for search success condition
            if self.frameCounter >= self.frameCountTarget:
                print(targetObj.classification + " located!")
                self.search = False
                self.searchComplete = "success"
                self.stop()
                return

            if not self.pause:
                if time.time() < self.rotateStopTime:
                    self.locoYaw = self.dir * self.searchVelocity

                # Allow time for robot to stop moving
                elif self.rotateStopTime <= time.time() < self.rotateStopTime + self.safetyDelay:
                    self.locoYaw = 0.0

                # End Rotation, Begin Pause
                else:
                    self.locoYaw = 0
                    self.startSearchTime = time.time()
                    self.rotateStopTime = time.time() + self.searchPeriod
                    self.prevTime = 0
                    self.pause = True

            else:
                # End Pause, Begin Rotation
                if time.time() >= self.rotateStopTime:
                    self.pause = False
                    self.startSearchTime = time.time()
                    self.prevTime = 0
                    self.rotateStopTime = time.time() + self.searchPeriod
                    self.periodCounter += 1

    def retrieve_items(self):
        # Format list of current detections as string
        list_string = ""
        for obj in self.object_list:
            list_string += ", " + obj.classification
        return list_string

    def get_running(self):
        # Format list of currently running operations and targets as string
        running_function = ""
        if self.search:
            running_function = "search"

        if running_function != "":
            running_function += ", " + self.targetClass

        return running_function
