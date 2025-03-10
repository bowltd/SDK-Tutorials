#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (c) 2024, Bettering Our Worlds (BOW) Ltd.
# All Rights Reserved
# Author: Sam Piper <sam.piper@bow.ltd>
import os
import time
import sys
import logging
import threading
from queue import Queue
from typing import List, Dict

import bow_api
import bow_data
import cv2
import numpy as np
from pynput import keyboard
from tts import TTS  # Import the TTS class

# Constants for audio settings and control logic
SAMPLE_RATE = 24_000
NUM_CHANNELS = 1
COMPRESSION_FORMAT = bow_data.AudioSample.CompressionFormatEnum.RAW
AUDIO_BACKENDS = ["notinternal"]
AUDIO_TRANSMIT_RATE = 25
NUM_SAMPLES = SAMPLE_RATE // AUDIO_TRANSMIT_RATE
CHUNK_SIZE = NUM_CHANNELS * NUM_SAMPLES


SPEECH_RATE_LIMIT = 15  # 15 seconds
DEBOUNCE_TIME = 1  # 1 second debounce time for 'v' key

USE_OPENAI = os.getenv('USE_OPENAI', 'False')


class RobotController:
    def __init__(self):
        # Initialize logger for debugging and information
        print(bow_api.version())

        # Audio parameters for voice channel
        self.audio_params = bow_data.AudioParams(
            Backends=AUDIO_BACKENDS,
            SampleRate=SAMPLE_RATE,
            Channels=NUM_CHANNELS,
            SizeInFrames=True,
            TransmitRate=AUDIO_TRANSMIT_RATE
        )

        # Initialization flags and variables
        self.stop_flag = False
        self.window_names: Dict[str, str] = {}
        self.windows_created = False
        self.pressed_keys = set()

        # Initialize speech timing and actions
        self.last_speech_time = 0
        self.last_action = None
        self.last_spoken_action = None
        self.last_v_press_time = 0

        # Queue for speech commands
        self.speech_queue = Queue()


        # Connect to the robot
        self.robot, error = bow_api.quick_connect(
            app_name="Text to Speech",
            channels=["voice", "vision", "motor"],
            verbose=True,
            audio_params=self.audio_params
        )
        if not error.Success:
            print("Failed to connect to robot", error)
            sys.exit()

        # Print robot input and output channels for debugging
        print(self.robot.robot_details.robot_config.input_modalities)
        print(self.robot.robot_details.robot_config.output_modalities)

        # Start keyboard listener for capturing key presses and releases
        self.listener = keyboard.Listener(on_press=self.on_press, on_release=self.on_release)
        self.listener.start()

        # Start the speech processing thread
        self.speech_thread = threading.Thread(target=self.process_speech_queue)
        self.speech_thread.daemon = True
        self.speech_thread.start()

    def on_press(self, key: keyboard.Key):
        """Handle key press events."""
        try:
            self.pressed_keys.add(key.char)
        except AttributeError:
            pass

    def on_release(self, key: keyboard.Key):
        """Handle key release events."""
        try:
            self.pressed_keys.discard(key.char)
        except AttributeError:
            pass
        if key == keyboard.Key.esc:
            return False

    def show_all_images(self, images_list: List[bow_data.ImageSample]):
        """Display all images in the provided list."""
        if not self.windows_created:
            for i in range(len(images_list)):
                window_name = f"RobotView{i} - {images_list[i].Source}"
                self.window_names[images_list[i].Source] = window_name
                cv2.namedWindow(window_name)
            self.windows_created = True

        for i, img_data in enumerate(images_list):
            if len(img_data.Data) != 0:
                if img_data.NewDataFlag:
                    if img_data.ImageType == bow_data.ImageSample.ImageTypeEnum.RGB:
                        npimage = np.frombuffer(img_data.Data, np.uint8).reshape(
                            [int(img_data.DataShape[1] * 3 / 2), img_data.DataShape[0]])
                        npimage = cv2.cvtColor(npimage, cv2.COLOR_YUV2RGB_I420)
                        cv2.imshow(self.window_names[img_data.Source], npimage)
                    elif img_data.ImageType == bow_data.ImageSample.ImageTypeEnum.DEPTH:
                        npimage = np.frombuffer(img_data.Data, np.uint16).reshape(
                            [img_data.DataShape[1], img_data.DataShape[0]])
                        cv2.imshow(self.window_names[img_data.Source], npimage)
                    else:
                        print("Unhandled image type")

    def send_speech_command(self, text: str):
        # TODO open thread once and queue in speech to be processed.

        """Convert text to speech and stream to the robot in chunks."""
        # Use TTS service to convert text to speech

        if USE_OPENAI:
            tts_service = TTS(service='openai', model='tts-1', voice='alloy')
        else:
            tts_service = TTS(service='willow', format='wav', speaker='CLB')

        audio_segment = tts_service.stream_text_to_speech(text, playback=False)

        if audio_segment is None:
            print("Failed to retrieve audio segment.")
            return

        raw_audio = audio_segment.raw_data


        # Stream audio data in chunks to the robot
        for i in range(0, len(raw_audio), CHUNK_SIZE):
            print("sending chunk")
            chunk = raw_audio[i:i + CHUNK_SIZE]
            audio_sample = bow_data.AudioSample(
                Source="Client",
                Data=chunk,
                Channels=NUM_CHANNELS,
                SampleRate=SAMPLE_RATE,
                NumSamples=CHUNK_SIZE // NUM_CHANNELS,
                Compression=COMPRESSION_FORMAT
            )
            result = self.robot.voice.set(audio_sample)
            if not result.Success:
                print(result.Description, result.Code)
                print(f"Failed to send audio sample chunk {i // CHUNK_SIZE} to the robot.")
                break
            time.sleep(1 / (AUDIO_TRANSMIT_RATE * 2))

    def process_speech_queue(self):
        """Process the speech queue, sending commands to the robot."""
        while True:
            text = self.speech_queue.get()
            if text is None:  # Allows for graceful shutdown
                break
            self.send_speech_command(text)
            self.speech_queue.task_done()
            time.sleep(0.2) # 200 ms


    def control_loop(self):
        """Main control loop for handling vision, motor, and voice modalities."""
        try:
            while True:
                # Fetch and display images from the robot's vision channel
                image_list, err = self.robot.vision.get(True)
                if not err.Success or not image_list:
                    continue

                self.show_all_images(image_list)

                # Handle motor commands based on key presses
                motor_sample = bow_data.MotorSample()
                action = None
                if 'w' in self.pressed_keys:
                    action = "Moving forward"
                    motor_sample.Locomotion.TranslationalVelocity.X = 0.2
                elif 's' in self.pressed_keys:
                    action = "Moving backward"
                    motor_sample.Locomotion.TranslationalVelocity.X = -0.2
                elif 'd' in self.pressed_keys:
                    action = "Rotate right"
                    motor_sample.Locomotion.RotationalVelocity.Z = -1
                elif 'a' in self.pressed_keys:
                    action = "Rotate left"
                    motor_sample.Locomotion.RotationalVelocity.Z = 1
                elif 'e' in self.pressed_keys:
                    action = "Strafe right"
                    motor_sample.Locomotion.TranslationalVelocity.Y = -1
                elif 'q' in self.pressed_keys:
                    action = "Strafe left"
                    motor_sample.Locomotion.TranslationalVelocity.Y = 1

                # Send motor commands to the robot
                self.robot.motor.set(motor_sample)

                # Handle speech commands with rate limiting and debounce logic
                current_time = time.time()
                if 'v' in self.pressed_keys:
                    if current_time - self.last_v_press_time > DEBOUNCE_TIME:
                        # Speak the action if 'v' key is pressed and debounce time has passed
                        if action:
                            print(action)
                            self.speech_queue.put(action)
                        self.last_v_press_time = current_time
                elif (
                        current_time - self.last_speech_time > SPEECH_RATE_LIMIT) and action and action != self.last_spoken_action:
                    # Speak the action if rate limit has passed and it's a new action
                    print(action)
                    self.speech_queue.put(action)
                    self.last_speech_time = current_time
                    self.last_spoken_action = action

                self.last_action = action

                cv2.waitKey(1)

        except KeyboardInterrupt:
            pass
        finally:
            # Clean up and close resources on exit
            cv2.destroyAllWindows()
            print("Closing down")
            self.stop_flag = True
            self.robot.disconnect()
            bow_api.close_client_interface()

    def run(self):
        """Run the robot control loop."""
        self.control_loop()


if __name__ == "__main__":
    controller = RobotController()
    controller.run()
