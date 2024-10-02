import math
import time
import bow_client as bow
import bow_utils as utils
import logging


class RobotController:
    def __init__(self):
        self.log = utils.create_logger("BOW x OpenAI", logging.INFO)
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
        self.safety_time = None
        self.look_up_time = None
        self.look_down_time = None
        self.safety_look_time = None
        self.loco2pose = False

        # Rotate Init
        self.rotateStopTime = 0.0
        self.locoYaw = 0.0
        self.dir = 1
        self.safetyDelay = 2

        # Pose Init
        self.pose = False
        self.upTime = 3
        self.downTime = 3
        self.poseStopTime = 0
        self.poseComplete = None
        self.poseY = 0
        self.poseX = 0
        self.poseZ = 0

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
        self.resetLoco()

        # Wait for sim to stabilise?
        time.sleep(1)
        self.robot.set_modality("speech", "ChatGPT embodied successfully")

        ext_sample, err = self.robot.get_modality("exteroception", True)
        while ext_sample is None:
            ext_sample, err = self.robot.get_modality("exteroception", True)
        self.front_sonar, self.rear_sonar = identify_sonars(ext_sample.Range)

    # Blocking function to force locomotion to 0
    def resetLoco(self):
        ret = utils.Error
        ret.Success = False
        while not ret.Success:
            print("Resetting Locomotion...")
            motor_sample = utils.MotorSample()
            motor_sample.Locomotion.RotationalVelocity.Z = 0
            motor_sample.Locomotion.TranslationalVelocity.X = 0
            motor_sample.Locomotion.TranslationalVelocity.Y = 0
            ret = self.robot.set_modality("motor", motor_sample)
            time.sleep(0.05)
        return ret.Success

    def update(self):

        # Get latest sonar readings
        self.update_sonar()

        # Update any ongoing motor actions
        if self.search: self.updateSearch()
        if self.locomote: self.update_locomotion()
        if self.pose: self.update_pose()

        # Create New motor message
        motor_sample = utils.MotorSample()

        # Populate message with locomotion velocities
        if self.locoX != 0 or self.locoY != 0 or self.locoYaw != 0:
            motor_sample.Locomotion.RotationalVelocity.Z = self.locoYaw
            motor_sample.Locomotion.TranslationalVelocity.X = self.locoX
            motor_sample.Locomotion.TranslationalVelocity.Y = self.locoY
            self.loco2pose = True

        elif self.poseX != 0 or self.poseY != 0 or self.poseZ != 0:
            if self.loco2pose:
                self.resetLoco()
                time.sleep(1)
                self.loco2pose = False
                return
            else:
                motor_sample.GazeTarget.GazeVector.X = self.poseX
                motor_sample.GazeTarget.GazeVector.Y = self.poseY
                motor_sample.GazeTarget.GazeVector.Z = self.poseZ
        else:
            motor_sample.Locomotion.RotationalVelocity.Z = 0
            motor_sample.Locomotion.TranslationalVelocity.X = 0
            motor_sample.Locomotion.TranslationalVelocity.Y = 0

        # Send Motor message to robot
        ret = self.robot.set_modality("motor", motor_sample)
        if not ret.Success:
            print("set_modality motor: ", ret)
        return ret

    def stop(self):
        print("Stop command received")
        self.search = False
        self.pose = False
        self.locomote = False
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
        self.safety_time = self.rotateStopTime + self.safetyDelay
        self.look_up_time = self.safety_time + self.upTime
        self.look_down_time = self.look_up_time + self.downTime
        self.safety_look_time = self.look_down_time + self.safetyDelay
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
                elif self.rotateStopTime <= time.time() < self.safety_time:
                    self.locoYaw = 0.0

                # Perform up-down search
                elif self.safety_time <= time.time() < self.look_up_time:
                    self.locoYaw = 0.0
                    self.poseY = 1

                elif self.look_up_time <= time.time() < self.look_down_time:
                    self.locoYaw = 0.0
                    self.poseY = -1

                elif self.look_down_time <= time.time() < self.safety_look_time:
                    self.locoYaw = 0.0
                    self.poseY = 0.0

                # End Rotation, Begin Pause
                else:
                    self.poseY = 0
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
                    self.safety_time = self.rotateStopTime + self.safetyDelay
                    self.look_up_time = self.safety_time + self.upTime
                    self.look_down_time = self.look_up_time + self.downTime
                    self.safety_look_time = self.look_down_time + self.safetyDelay
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

    def update_pose(self):
        if time.time() >= self.poseStopTime:
            self.pose = False
            self.poseComplete = "success"
            self.poseX = 0
            self.poseY = 0
            self.poseZ = 0

    def start_pose(self, x, y, z, duration=3):
        print("Pose Command Received")

        # Reset State
        self.stop()
        time.sleep(2)

        # Initialise
        self.pose = True
        self.poseComplete = None
        self.poseStopTime = time.time() + duration
        self.poseX = x
        self.poseY = y
        self.poseZ = z

    def update_sonar(self):
        ext_sample, err = self.robot.get_modality("exteroception", False)
        if not err.Success:
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
        if self.search: running_function = "search"
        elif self.locomote: running_function = "locomote"
        elif self.pose: running_function = "pose"

        if running_function == "search":
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
