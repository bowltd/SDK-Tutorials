import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import cv2

from openai_brain import Brain
from PIL import Image, ImageTk
import bow_client as bow
from ultralytics import YOLO
from robot_controller import RobotController

class GUI:
    def __init__(self, master, brain, controller):
        self.master = master
        self.master.title("BOW >< OpenAI")
        self.master.geometry("1700x830")
        self.master.configure(bg="#656665")  # Updated background color to WHITE

        self.controller = controller

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
        self.style.configure("Stop.TButton", foreground="#000000", background="#F36C24",  # YELLOW button
                             font=("Proxima Nova Bold", 18, "bold"), width=10)
        self.output_text.tag_config("user", foreground="#97C93D")  # GREEN text for user
        self.output_text.tag_config("system", foreground="#939799", font=("Arial", 12, "italic"))  # GREY text for system

        # Logic
        self.brain = brain

    def SendButton_click(self):
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

        # Pass message to OpenAI assistant
        self.brain.request(message_content, "user", self)

    def StopButton_click(self):
        self.controller.stop()
        self.output_text.insert(tk.END, "\nStopping\n")

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


def main():
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

        # Get camera images from BOW robot
        image_list, err = controller.robot.get_modality("vision", True)
        if err.Success:
            if len(image_list) > 0:
                img_data = image_list[0]
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

if __name__ == "__main__":
    main()
