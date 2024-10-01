import asyncio
import math
import os
from pathlib import Path

import dotenv
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import cv2
import imutils
import openai

from openai_brain import Brain
from openai_helper import OpenAIHelper
from PIL import Image, ImageTk
import bow_client as bow
from ultralytics import YOLO
from robot_controller import RobotController

class GUI:
    def __init__(self, master, brain, controller):
        self.select_assistant_button = None
        self.create_assistant_button = None
        self.button_frame = None
        self.entry_frame = None
        self.api_frame = None
        self.master = master
        self.master.title("BOW >< OpenAI")
        self.master.geometry("1700x880")
        self.master.configure(bg="#656665")  # Updated background color to WHITE

        self.controller = controller

        self.firstCommand = True
        self.openai_helper = None
        self.api_key = None
        self.ass_id = None

        self.env_file = Path("keys.env")
        dotenv.load_dotenv(self.env_file)
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.ass_id = os.getenv("ASSISTANT_ID")

        if self.api_key is None or self.ass_id is None:
            # Create a frame for the API key entry and button
            self.api_frame = ttk.Frame(self.master, style="BW.TLabel")
            self.api_frame.pack(side=tk.TOP, pady=10, fill=tk.X)

            # Create a frame specifically for the button, and center it
            self.button_frame = ttk.Frame(self.api_frame)
            self.button_frame.pack(side=tk.TOP, pady=5)

            # Create the button and pack it to center
            self.list_assistants_button = ttk.Button(self.button_frame, text="List Assistants",
                                                      command=self.list_assistants, style="TButton")
            self.list_assistants_button.pack(side=tk.TOP, ipadx=25)

            # Create a frame specifically for the entry box, and center it
            self.entry_frame = ttk.Frame(self.api_frame)
            self.entry_frame.pack(side=tk.TOP, pady=5)

            # Create an entry box for the OpenAI API key and pack it to center
            if self.api_key is None:
                input_text = "Enter your OpenAI API key here..."
            else:
                input_text = "Enter Assistant ID here..."
            self.api_key_entry = ttk.Entry(self.entry_frame, font=("Arial", 10), width=80)
            self.api_key_entry.insert(0, input_text)
            self.api_key_entry.pack(side=tk.TOP, padx=5)

        # Define the style for the labels and buttons using the branding colors
        style = ttk.Style()
        style.configure("BW.TLabel", background="#656665", foreground="#000000")  # WHITE background, BLACK text

        # Create a frame for the OpenCV image
        self.image_frame = ttk.Frame(self.master, style="BW.TLabel")
        self.image_frame.pack(side=tk.LEFT, fill=tk.BOTH, padx=10, pady=10, expand=True)

        # Create a label for the image window
        self.image_label = ttk.Label(self.image_frame, style="BW.TLabel")
        self.image_label.pack(fill=tk.BOTH, expand=True)

        # Create the Stop button and place it under the image
        self.StopButton = ttk.Button(self.image_frame, text="STOP", command=self.StopButton_click, style="Stop.TButton")
        self.StopButton.pack(side=tk.TOP, pady=20)

        # Create a frame for text output
        self.text_frame = ttk.Frame(self.master, style="BW.TLabel")
        self.text_frame.pack(side=tk.LEFT, padx=10, pady=10, fill=tk.BOTH, expand=True)

        # Create a text output box
        self.output_text = tk.Text(self.text_frame, height=20, width=80, bg="#000000", fg="#FFFFFF",  # Light GREY background, BLACK text
                                   insertbackground="#000000", highlightbackground="#F0F0F0", highlightcolor="#EBE726",  # YELLOW cursor and highlights
                                   font=("Arial", 18), wrap=tk.WORD)
        self.output_text.pack(side=tk.TOP, pady=5, fill=tk.BOTH, expand=True)
        if self.api_key is not None and self.ass_id is None:
            self.output_text.insert(tk.END, "OpenAI Key found. ", "system")
            self.list_assistants()

        # Create a frame for text input and buttons
        self.input_button_frame = ttk.Frame(self.text_frame, style="BW.TLabel")
        self.input_button_frame.pack(side=tk.BOTTOM, pady=5, fill=tk.BOTH, expand=True)

        # Create a text input box with word wrapping
        self.input_text = tk.Text(self.input_button_frame, height=4, width=50, font=("Arial", 18), wrap=tk.WORD, bg="#FFFFFF", fg="#000000", highlightcolor="#EBE726")  # WHITE background, BLACK text
        self.input_text.pack(side=tk.TOP, pady=5, fill=tk.X)
        self.input_text.bind("<Return>", lambda event: self.SendButton.invoke())

        # Create the Send button and place it under the input text box
        self.SendButton = ttk.Button(self.input_button_frame, text="Send", command=self.SendButton_click, style="TButton")
        self.SendButton.pack(side=tk.TOP, pady=5)

        # Set button styles using branding colors
        self.style = ttk.Style()
        self.style.configure("TButton", foreground="#000000", background="#97C93D",  # GREEN button
                             font=("Proxima Nova Medium", 18), width=10)
        self.style.configure("Assistant.TButton", foreground="#000000", background="#97C93D",  # GREEN button
                             font=("Proxima Nova Medium", 10), width=12)
        self.style.configure("DelAssistant.TButton", foreground="#000000", background="#F36C24",  # GREEN button
                             font=("Proxima Nova Medium", 10), width=12)
        self.style.configure("Stop.TButton", foreground="#000000", background="#F36C24",  # YELLOW button
                             font=("Proxima Nova Bold", 18, "bold"), width=10)
        self.output_text.tag_config("user", foreground="#97C93D")  # GREEN text for user
        self.output_text.tag_config("system", foreground="#939799", font=("Arial", 12, "italic"))  # GREY text for system

        # Logic
        self.brain = brain

    async def generate_request(self, message):
        await self.brain.request(message, "user", self)

    def SendButton_click(self):

        if self.firstCommand:
            dotenv.load_dotenv(self.env_file)
            openai_api_key = os.getenv("OPENAI_API_KEY")
            if openai_api_key is None:
                self.input_text.delete("1.0", tk.END)
                self.output_text.insert(tk.END, "\n No OpenAI API Key present, please supply one and create or select an assistant \n"  , "system")
                self.output_text.see(tk.END)
                self.master.update()
                return

            assistant_id = os.getenv('ASSISTANT_ID')
            if assistant_id is None:
                self.input_text.delete("1.0", tk.END)
                self.output_text.insert(tk.END,
                                        "\n No Assistant Key present, please create or select an assistant \n",
                                        "system")
                self.output_text.see(tk.END)
                self.master.update()
                return

            asyncio.create_task(self.brain.start())
            self.firstCommand = False
            self.delete_assistant_buttons()

        # Get the text from the input box and then delete it
        message_content = self.input_text.get("1.0", tk.END).strip()
        self.input_text.delete("1.0", tk.END)

        # Add the message to the output text box and update gui
        self.output_text.insert(tk.END, "\n" + message_content + "\n", "user")
        self.output_text.see(tk.END)
        self.master.update()

        # Add a thinking message for feedback and update the GUI
        self.output_text.insert(tk.END, "thinking...", "system")
        self.output_text.see(tk.END)
        self.master.update()

        # Create a new thread for the API request
        asyncio.create_task(self.generate_request(message_content))

    def StopButton_click(self):
        self.controller.stop()
        self.output_text.insert(tk.END, "\nStopping\n")

    def create_assistant(self):
        self.ass_id = self.openai_helper.CreateAssistant()
        if self.ass_id is not None:
            self.env_file.touch(mode=0o600, exist_ok=True)
            dotenv.set_key(self.env_file, "OPENAI_API_KEY", self.api_key)
            dotenv.set_key(self.env_file, "ASSISTANT_ID", self.ass_id)
            dotenv.load_dotenv(self.env_file)
            print(f"File '{self.env_file}' created and populated.")
            self.output_text.insert(tk.END,
                                    "\n Assistant Created \n",
                                    "system")
            self.output_text.see(tk.END)
            self.master.update()
        else:
            self.output_text.insert(tk.END,
                                    "\n Please enter a valid OpenAI API Key \n",
                                    "system")
            self.output_text.see(tk.END)
            self.master.update()

    def list_assistants(self):
        print("Listing assistants...")
        # Get the API key from the entry box and process it
        if self.api_key is None:
            self.api_key = self.api_key_entry.get()
            self.env_file.touch(mode=0o600, exist_ok=True)
            dotenv.set_key(self.env_file, "OPENAI_API_KEY", self.api_key)
            dotenv.load_dotenv(self.env_file)
        self.openai_helper = OpenAIHelper(self.api_key)
        try:
            assistants = self.openai_helper.ListAssistants()
        except openai.AuthenticationError as e:
            print(e.message)
            self.output_text.insert(tk.END, e.message, "system")
            return

        # Reset text in input box
        self.api_key_entry.delete(0, tk.END)
        self.api_key_entry.insert(0, "Enter Assistant ID here...")

        if self.select_assistant_button is None:
            # Create a button to select an assistant, positioned next to the entry box
            self.select_assistant_button = ttk.Button(self.entry_frame, text="Select Assistant",
                                                      command=self.select_assistant, style="Assistant.TButton")
            self.select_assistant_button.pack(side=tk.LEFT, padx=5, ipadx=10)

            # Create a button to select an assistant, positioned next to the entry box
            self.create_assistant_button = ttk.Button(self.entry_frame, text="Create Assistant",
                                                      command=self.create_assistant, style="Assistant.TButton")
            self.create_assistant_button.pack(side=tk.LEFT, padx=5, ipadx=10)

            # Create a button to delete an assistant, positioned next to the select button
            self.delete_assistant_button = ttk.Button(self.entry_frame, text="Delete Assistant",
                                                      command=self.delete_assistant, style="DelAssistant.TButton")
            self.delete_assistant_button.pack(side=tk.LEFT, padx=5, ipadx=10)

        self.output_text.insert(tk.END, "Listing assistants...\n", "system")
        self.output_text.insert(tk.END, assistants, "system")

    def select_assistant(self):
        ass_id = self.api_key_entry.get()
        self.env_file.touch(mode=0o600, exist_ok=True)
        dotenv.set_key(dotenv_path=self.env_file, key_to_set="ASSISTANT_ID", value_to_set=ass_id)
        dotenv.load_dotenv(self.env_file)
        print(f"File '{self.env_file}' created and populated.")
        print("Assistant selected!")

    def delete_assistant(self):
        ass_id = self.api_key_entry.get()
        response = self.openai_helper.DeleteAssistant(ass_id)
        if response.deleted:
            print("Assistant deleted!")
            self.output_text.insert(tk.END, "Assistant deleted!", "system")
        else:
            print("Assistant deletion failed: " + response)
            self.output_text.insert(tk.END, "Assistant deletion failed: " + response, "system")

    def delete_assistant_buttons(self):
        # Destroy the frames which will also remove the widgets inside them
        self.output_text.delete('1.0', tk.END)
        if self.button_frame is not None: self.button_frame.destroy()  # Destroys the frame with the "List Assistants" button
        if self.entry_frame is not None: self.entry_frame.destroy()  # Destroys the frame with the input box and other buttons
        if self.entry_frame is not None: self.api_frame.destroy()  # Destroys the parent frame containing all child frames

    def update_image(self, cv_image):
        # Convert OpenCV image to PIL format
        if cv_image is not None:
            image = cv2.cvtColor(cv_image, cv2.COLOR_BGR2RGB)
            image = cv2.resize(image, (960, 720))
            image = Image.fromarray(image)
            image = ImageTk.PhotoImage(image)

            # Update the image label
            self.image_label.configure(image=image)
            self.image_label.image = image

# Basic class to hold detected object details
class DetectedObject:
    def __init__(self):
        self.classification = None
        self.confidence = None
        self.box = None
        self.center = [None, None]
        self.area = 0.0

def on_closing(window, robot):
    if messagebox.askokcancel("Quit", "Do you want to quit?"):
        window.destroy()
        robot.disconnect()
        bow.close_client_interface()

async def main():
    # Create a Tkinter window
    root = tk.Tk()

    # Create a robot controller and openai instance
    controller = RobotController()
    brain = Brain(controller)

    # Initialize the GUI
    gui = GUI(root, brain, controller)
    root.protocol("WM_DELETE_WINDOW", lambda window=root, robot=controller.robot: on_closing(root, controller.robot))

    #Initialise the object detection
    model = YOLO('yolov8n.pt')  # load an official detection model
    objects = []

    # Main loop
    while True:
        # Test for completed functions and relay results to openai assistant as "assistant" messages
        if controller.searchComplete is not None:
            if controller.searchComplete == "success":
                brain.request("Search Successful", "assistant", gui)
            elif controller.searchComplete == "failure":
                brain.request("Search Failed", "assistant", gui)
            controller.searchComplete = None

        if controller.locomoteComplete is not None:
            if controller.locomoteComplete == "success":
                brain.request("Locomote Complete", "assistant", gui)

        # Get camera images from BOW robot
        image_list, err = controller.robot.get_modality("vision", False)
        if err.Success:
            if len(image_list) > 0 and image_list[0].image is not None:
                img_data = image_list[0]
                img_data.image = imutils.rotate_bound(img_data.image, img_data.transform.EulerAngles.X * 180 / math.pi)
                # Set camera parameters on first instance
                if controller.VFOV is None:
                    if img_data.vfov == 0:
                        controller.VFOV = 40
                    else:
                        controller.VFOV = img_data.vfov

                    if img_data.hfov == 0:
                        controller.HFOV = 80
                    else:
                        controller.HFOV = img_data.hfov

                # Pass image into yolo model
                results = model.predict(source=img_data.image, show=False, stream_buffer=False,
                                        verbose=False)

                # Iterate though detected objects and populate objects list and details
                if len(results) > 0:
                    for box in results[0].boxes.cpu():
                        obj = DetectedObject()
                        obj.classification = model.names[int(box.data[0][-1])]
                        obj.confidence = box.conf.numpy()[0]
                        obj.box = box.xyxy.numpy()[0]
                        width = obj.box[2] - obj.box[0]
                        height = obj.box[3] - obj.box[1]
                        area = width * height
                        imgArea = img_data.shape[0] * img_data.shape[1]
                        obj.area = area / imgArea
                        center = (int(obj.box[0] + width / 2), int(obj.box[1] + height / 2))
                        obj.center[0] = center[0] * (1/img_data.shape[0])
                        obj.center[1] = 1-(center[1] * (1 / img_data.shape[1]))
                        objects.append(obj)

                # Draw detections on image
                annotated_img = img_data.image
                for obj in objects:
                    colour = (61, 201, 151)
                    if controller.targetClass is not None or controller.prevTargetClass is not None:
                        if obj.classification == controller.targetClass:
                            colour = (36, 108, 243)
                        if obj.classification == controller.prevTargetClass:
                            colour = (36, 108, 243)

                    annotated_img = cv2.rectangle(annotated_img, (int(obj.box[0]), int(obj.box[1])),
                                                  (int(obj.box[2]), int(obj.box[3])), colour, thickness=3)
                    # Set the label position
                    label_x = int(obj.box[0])
                    label_y = int(obj.box[1]) - 10  # Position above the box by default

                    # Check if the label is going off-screen
                    if label_y < 10:
                        label_y = int(obj.box[3]) + 20  # Position below the box

                    # Draw the label
                    cv2.putText(annotated_img, obj.classification, (label_x, label_y),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.7, colour, 1)

                # Pass objects list to robot controller
                controller.object_list = objects

                # Update gui image
                gui.update_image(annotated_img)

                # Update controller
                ret = controller.update()

            # Update the Tkinter window
            objects = []
            root.update_idletasks()
            root.update()
            await asyncio.sleep(0.01)

if __name__ == "__main__":
    asyncio.run(main())
