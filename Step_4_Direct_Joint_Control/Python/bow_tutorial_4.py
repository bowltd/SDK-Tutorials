#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (c) 2023, Bettering Our Worlds (BOW) Ltd.
# All Rights Reserved
# Author: Daniel Camilleri <daniel.camilleri@bow.ltd>

import bow_client as bow
import bow_utils
import sys
import logging
import threading
import time
import tkinter as tk
from tkinter import ttk
import math


class RobotControlApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Robot Controller")
        self.log = bow_utils.create_logger("Robot Controller Tutorial 4", logging.INFO)

        # Setup connection button
        self.connect_button = ttk.Button(self.root, text="Connect to Robot", command=self.connect_to_robot)
        self.connect_button.pack(pady=20)

        # Quit Button
        self.quit_button = ttk.Button(self.root, text="Quit", command=self.quit_app)
        self.quit_button.pack(pady=10)

        self.reset_button = ttk.Button(self.root, text="Reset Angles", command=self.reset_all_joints)
        self.reset_button.pack(pady=10)

        # Frame to hold the dynamically created sliders and labels
        self.sliders_frame = ttk.Frame(self.root)
        self.sliders_frame.pack(fill='both', expand=True)

        # Placeholder for joint information
        self.joints = []
        self.RealRobot = None
        self.SimRobot = None
        self.stop_threads = False
        self.slider_vars = {}  # For interactive slider variables
        self.current_vars = {}  # For non-interactive current position indicators

    def connect_to_robot(self):
        modalities = ["proprioception", "motor"]
        audio_params = bow_utils.AudioParams(
                                                Backends=[""],
                                                SampleRate=16000,
                                                Channels=1,
                                                SizeInFrames=True,
                                                TransmitRate=30)
        setup_result = bow.setup(audio_params, self.log.name, True)
        if not setup_result.Success:
            return None, setup_result

        login_result = bow.login_user("", "", True)
        if login_result.Success:
            self.log.info("Logged in")
        else:
            return None, login_result

        get_robots_result = bow.get_robots(False, True, False)
        if not get_robots_result.localSearchError.Success:
            self.log.error(get_robots_result.localSearchError.Description)

        if not get_robots_result.remoteSearchError.Success:
            self.log.error(get_robots_result.remoteSearchError.Description)

        if len(get_robots_result.robots) == 0:
            self.log.info("No Robots found")
            bow.close_client_interface()
            return None, bow_utils.Error(Success=False, Code=62, Description="No Robots Found")

        realRobotDetails = None
        simRobotDetails = None
        for robot in get_robots_result.robots:
            if robot.name == "leArm Sim":
                realRobotDetails = robot

            if robot.name == "RealArm":
                simRobotDetails = robot



        self.RealRobot = bow.Robot(realRobotDetails)
        connected_result = self.RealRobot.connect()
        if not connected_result.Success:
            self.log.error("Could not connect with robot {}".format(self.RealRobot.robot_details.robot_id))
            bow.close_client_interface()
            return None, connected_result

        all_robot_modalities = (list(realRobotDetails.robot_config.input_modalities)
                                + list(realRobotDetails.robot_config.output_modalities))
        print(all_robot_modalities)
        for modality in modalities:
            if modality in all_robot_modalities:
                open_result = self.RealRobot.open_modality(modality)
                if not open_result.Success:
                    self.log.error(f"Failed to open {modality} modality: {open_result.Description}")
            else:
                self.log.warning(f"{modality} modality is not available for the chosen robot. Modality ignored")

        self.SimRobot = bow.Robot(simRobotDetails)
        connected_result = self.SimRobot.connect()
        if not connected_result.Success:
            self.log.error("Could not connect with robot {}".format(self.SimRobot.robot_details.robot_id))
            bow.close_client_interface()
            return None, connected_result

        all_robot_modalities = (list(simRobotDetails.robot_config.input_modalities)
                                + list(simRobotDetails.robot_config.output_modalities))
        print(all_robot_modalities)
        for modality in modalities:
            if modality in all_robot_modalities:
                open_result = self.SimRobot.open_modality(modality)
                if not open_result.Success:
                    self.log.error(f"Failed to open {modality} modality: {open_result.Description}")
            else:
                self.log.warning(f"{modality} modality is not available for the chosen robot. Modality ignored")

        # Initialize the slider frames once connection is established
        self.initialize_sliders()

        # Start the sampling and command sending threads
        self.start_sampling()

    def initialize_sliders(self):
        while True:
            prop_msg, err = self.SimRobot.get_modality("proprioception", True)
            if err.Success and len(prop_msg.RawJoints) > 0:
                for joint in prop_msg.RawJoints:
                    if joint.Type == bow_utils.Joint.FIXED:
                        continue

                    joint_name = joint.Name
                    min_deg = round(math.degrees(joint.Min), 2)
                    max_deg = round(math.degrees(joint.Max), 2)
                    current_deg = round(math.degrees(joint.Position), 2)

                    joint_frame = ttk.Frame(self.sliders_frame)
                    joint_frame.pack(fill='x', padx=10, pady=5)

                    # Current position label
                    current_var = tk.DoubleVar(value=current_deg)
                    self.current_vars[joint_name] = current_var
                    joint_label = ttk.Label(joint_frame, text=f"{joint_name}: Current: {current_deg}°")
                    joint_label.pack()

                    if not hasattr(self, 'current_labels'):
                        self.current_labels = {}
                    self.current_labels[joint_name] = joint_label

                    # Interactive slider
                    slider_var = tk.DoubleVar(value=current_deg)
                    self.slider_vars[joint_name] = slider_var
                    slider = ttk.Scale(joint_frame, from_=min_deg, to=max_deg, variable=slider_var, orient='horizontal')
                    slider.pack(fill='x', expand=True)

                    desired_label = ttk.Label(joint_frame, text=f"Desired: {current_deg}°")
                    desired_label.pack()

                    slider_var.trace("w", lambda name, index, mode, sv=slider_var, dl=desired_label: dl.configure(
                        text=f"Desired: {float(sv.get()):.2f}°"))

                    # Min and Max labels
                    ttk.Label(joint_frame, text=f"Min: {min_deg}°").pack(side='left')
                    ttk.Label(joint_frame, text=f"Max: {max_deg}°").pack(side='right')
                break

    def start_sampling(self):
        threading.Thread(target=self.update_proprioception, daemon=True).start()
        threading.Thread(target=self.send_joint_commands, daemon=True).start()

    def update_proprioception(self):
        while not self.stop_threads:
            prop_msg, err = self.SimRobot.get_modality("proprioception", True)
            if err.Success and len(prop_msg.RawJoints) > 0:
                for joint in prop_msg.RawJoints:
                    if joint.Type == bow_utils.Joint.FIXED:
                        continue

                    joint_name = joint.Name
                    position_deg = round(math.degrees(joint.Position), 2)
                    self.current_vars[joint_name].set(position_deg)
                    self.current_labels[joint_name].config(text=f"{joint_name}: Current: {position_deg}°")
            time.sleep(0.1)  # Sample rate control

    def send_joint_commands(self):
        while not self.stop_threads:
            joint_commands = {name: math.radians(var.get()) for name, var in self.slider_vars.items()}
            motorSample = bow_utils.MotorSample()
            motorSample.ControlMode = bow_utils.MotorSample.USE_DIRECT_JOINTS
            for k, v in joint_commands.items():
                motorSample.RawJoints.append(bow_utils.Joint(Name=k, Position=v))
            self.SimRobot.set_modality("motor", motorSample)
            self.RealRobot.set_modality("motor", motorSample)
            time.sleep(0.03)

    def reset_all_joints(self):
        # Set all sliders to zero
        for var in self.slider_vars.values():
            var.set(0)

    def quit_app(self):
        self.stop_threads = True
        if self.SimRobot:
            self.SimRobot.disconnect()  # Disconnect from the robot
            self.log.info("Sim Robot disconnected")
        if self.RealRobot:
            self.RealRobot.disconnect()  # Disconnect from the robot
            self.log.info("Real Robot disconnected")
        self.log.info("Application quitting")
        self.root.quit()  # Quit the Tkinter GUI

# Create the main window and pass it to the RobotControlApp class
root = tk.Tk()
app = RobotControlApp(root)
root.mainloop()


#         # Act
#         motorSample = bow_utils.MotorSample()
#         if decision > 0:
#             if decision == ord('w'):
#                 print("Moving forward")
#                 motorSample.Locomotion.TranslationalVelocity.X = 1
#             elif decision == ord('s'):
#                 print("Moving backward")
#                 motorSample.Locomotion.TranslationalVelocity.X = -1
#             elif decision == ord('d'):
#                 print("Rotate right")
#                 motorSample.Locomotion.RotationalVelocity.Z = -1
#             elif decision == ord('a'):
#                 print("Rotate left")
#                 motorSample.Locomotion.RotationalVelocity.Z = 1
#             elif decision == ord('e'):
#                 print("Strafe right")
#                 motorSample.Locomotion.TranslationalVelocity.Y = -1
#             elif decision == ord('q'):
#                 print("Strafe left")
#                 motorSample.Locomotion.TranslationalVelocity.Y = 1
#         myrobot.set_modality("motor", motorSample)
#
