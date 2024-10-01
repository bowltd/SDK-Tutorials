import math
import time
import bow_client as bow
import bow_utils as utils
import logging


class RobotController:
    def __init__(self):
        self.log = utils.create_logger("BOW >< OpenAI", logging.INFO)
        self.log.info(bow.version())
        self.audio_params = utils.AudioParams(
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
        self.searchVelocity = 0.15  # The Angular velocity commanded during a search
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

        self.upTime = 2
        self.downTime = 2
        self.headUpDown = 0

        # Locomote Init
        self.locomote = False
        self.locomoteComplete = None
        self.locomoteStopTime = 0
        self.locoX = 0
        self.locoY = 0
        self.linearVel = 0.2
        self.rotationVel = 0.5

        # Range info
        self.front_sonar = ""
        self.rear_sonar = ""
        self.sonar_data = [None, None]

        # Connect to robot
        self.robot, error = bow.quick_connect(pylog=self.log,
                                              modalities=["vision", "motor", "speech", "exteroception"],
                                              verbose=False,
                                              audio_params=self.audio_params)

        print(self.robot.robot_details.robot_config.input_modalities)
        print(self.robot.robot_details.robot_config.output_modalities)

        # Initialise robot orientation (repeat until successful)
        while not self.resetLoco().Success:
            time.sleep(0.2)
            print("Trying Again...")

        # Wait for sim to stabilise?
        time.sleep(1)
        self.robot.set_modality("speech", "Skynet embodied successfully, get to the chopper!")

        ext_sample, err = self.robot.get_modality("exteroception", True)
        while ext_sample is None:
            ext_sample, err = self.robot.get_modality("exteroception", True)
        self.front_sonar, self.rear_sonar = identify_sonars(ext_sample.Range)

    def resetLoco(self):
        self.locoYaw = 0.0
        self.locoX = 0.0
        self.locoY = 0.0
        ret = self.update()
        return ret

    def update(self):

        # Get latest sonar readings
        self.update_sonar()

        # Update any ongoing motor actions
        if self.search: self.updateSearch()
        if self.locomote: self.update_locomotion()

        # Create New motor message
        motor_sample = utils.MotorSample()

        # Populate message with locomotion velocities
        motor_sample.Locomotion.RotationalVelocity.Z = self.locoYaw
        motor_sample.Locomotion.TranslationalVelocity.X = self.locoX
        motor_sample.Locomotion.TranslationalVelocity.Y = self.locoY

        motor_sample.GazeTarget.GazeVector.X = self.headUpDown

        # Send Motor message to robot
        ret = self.robot.set_modality("motor", motor_sample)
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
        self.locomote = False
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

                # Perform up-down search
                elif self.rotateStopTime + self.safetyDelay <= time.time() < self.rotateStopTime + self.safetyDelay + self.upTime:
                    self.locoYaw = 0.0
                    self.headUpDown = 0.2

                elif self.rotateStopTime + self.safetyDelay + self.upTime <= time.time() < self.rotateStopTime + self.safetyDelay + self.upTime + self.downTime:
                    self.locoYaw = 0.0
                    self.headUpDown = -0.4

                elif self.rotateStopTime + self.safetyDelay + self.upTime + self.downTime <= time.time() < self.rotateStopTime + 2*self.safetyDelay + self.upTime + self.downTime:
                    self.locoYaw = 0.0
                    self.headUpDown = 0.0

                # End Rotation, Begin Pause
                else:
                    self.headUpDown = 0
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

    def start_locomotion(self, xvel, yvel, theta, duration=3):
        print("Locomote Command Received")

        # Reset State
        self.stop()
        time.sleep(2)

        # Initialise Search
        self.locomote = True
        self.locomoteComplete = None
        self.locomoteStopTime = time.time() + duration
        self.locoX = xvel
        self.locoY = yvel
        self.locoYaw = theta

    def update_locomotion(self):
        if time.time() >= self.locomoteStopTime:
            self.locomote = False
            self.locomoteComplete = "success"
            self.locoX = 0
            self.locoY = 0
            self.locoYaw = 0.0
        else:
            if self.locoX > 0: self.locoX = self.linearVel
            if self.locoX < 0: self.locoX = -self.linearVel
            if self.locoY > 0: self.locoY = self.linearVel
            if self.locoY < 0: self.locoY = -self.linearVel
            if self.locoYaw > 0: self.locoYaw = self.rotationVel
            if self.locoYaw < 0: self.locoYaw = -self.rotationVel

    def update_sonar(self):
        ext_sample, err = self.robot.get_modality("exteroception", True)
        if not err.Success:
            print(err)
            return
        for range_sensor in ext_sample.Range:
            if range_sensor.Source == self.front_sonar:
                self.sonar_data[0] = range_sensor.Data
            elif range_sensor.Source == self.rear_sonar:
                self.sonar_data[1] = range_sensor.Data

    def retrieve_sonar(self):
        # Format sonar data as string
        sonar_string = "Front: " + str(self.sonar_data[0]) + ", Rear: " + str(self.sonar_data[1])
        return sonar_string

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

def identify_sonars(range_sensors):
    # Iterate through all range sensors and identify the sonar sensors
    sonars = []
    for sensor in range_sensors:
        if sensor.OperationType == utils.Range.OperationTypeEnum.Ultrasound:
            sonars.append(sensor)

    # Iterate through the sonars and find the sensor with the largest X position (furthest forward)
    front_sonar_x_pos = -100.0
    rear_sonar_x_pos = 100.0
    front_sonar_name = None
    rear_sonar_name = None
    for sonar in sonars:
        if sonar.Transform.Position.X > front_sonar_x_pos:
            front_sonar_x_pos = sonar.Transform.Position.X
            front_sonar_name = sonar.Source
        if sonar.Transform.Position.X < rear_sonar_x_pos:
            rear_sonar_x_pos = sonar.Transform.Position.X
            rear_sonar_name = sonar.Source

    # Return the name of the forward most sonar sensor
    return front_sonar_name, rear_sonar_name
