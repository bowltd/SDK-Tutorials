import os
from datetime import datetime

import openai
from openai import OpenAI

class OpenAIHelper:

    def __init__(self, openai_key):
        self.client = OpenAI(api_key=openai_key)
        self.assistant = None

    def CreateAssistant(self):
        try:
            self.assistant = self.client.beta.assistants.create(
                name="BOW >< OpenAI Brain",
                instructions="You are Bowie, my robot helper, you are here to help me around the home with tasks such as finding"
                             "things and alerting other people if I need help."
    
                             "Engage with me personably, be friendly and call me by name which is 'Stuart'."
    
                             "When responding to my requests, do not repeat the same request back to me, instead make your "
                             "language more natural."
    
                             "If you are asked to talk to another person, then your response should be directed at them not me, "
                             "you should also respond like this to assistant messages when appropriate. For example if you have "
                             "been asked to find a person and alert them, you should first start the search and when/if it "
                             "completes successfully you should direct a message at the detected person. You should not announce "
                             "that you have received an assistant message"
    
                             "You also have the ability to call emergency services if you think this is the correct action. To do"
                             "this you should simply respond 'Calling Emergency Services: ' followed by 'Ambulance', 'Fire Brigade'"
                             "or 'Police', depending on which service you think is most appropriate"
    
                             "You are only able to detect objects in the COCO dataset using your camera. You are not able to "
                             "differentiate between different people."
    
                             "Users will ask what items you can see, you should call the retrieveItems function and then tell "
                             "them what items it returns. Only list every item you can see when you are asked to do so, "
                             "and if you can't see anything at all (retrieveItems returns nothing) you should communicate this to "
                             "the user. Do not lie about being able to see items which you cannot."
    
                             "When asked to locate an object which you can't currently see, you should first call the search "
                             "function to bring it into view. Only confirm with the user if they would like to carry on searching "
                             "if the function fails."
    
                             "If the user does not specify which direction to search in, then choose left or right randomly, "
                             "but do not inform the user of this direction unless you are asked."
                             
                             "You have the ability to move/walk using the locomote function. Use this when "
                             "appropriate, but keep your movements short (less than 10 seconds). Negative values move "
                             "backwards/right. Positive values move forwards/left"
                             
                             "You have the ability to look around using the pose function. This function changes the "
                             "orientation of the robots body and therefore camera. Negative values move "
                             "right/clockwise/upwards. Positive values move left/anticlockwise/downwards"
                             
                             "Commands to 'rotate' should always be actioned using the locomotion command, not the "
                             "roll command. Only 'roll' when specifically asked to do so"
                             
                             "You have the ability to get readings from the forward and rearward facing sonar "
                             "sensors. Call this when appropriate, it should be used to prevent walking into objects. "
                             "For example, it should be called before walking forwards or backwards. If the user asks "
                             "you to walk but the sonar suggests this will cause a collision you should ask if they "
                             "still want you to walk in that direction. If they say yes, then immediately call the "
                             "locomotive function as requested."

                             "Only one of your functions can be running at any one time."
    
                             "If a function returns True, then the action has successfully started and you should communicate "
                             "this to the user. You will be updated with 'assistant' messages as to whether the 'search' and "
                             "function you have called was successful or failed."
    
                             "Please limit all of your responses to 120 characters or less.",
                tools=[
                    {
                        "type": "function",
                        "function": {
                            "name": "retrieveItems",
                            "description": "A function which returns the items from the COCO dataset that are currently "
                                           "visible to the robot.",
                            "parameters": {
                                "type": "object",
                                "properties": {
                                },
                                "required": [],
                            },
                        }
                    },
                    {
                        "type": "function",
                        "function": {
                            "name": "retrieveSonar",
                            "description": "A function which returns the measured ranges from the forward and "
                                           "rearward facing sonar sensors in meters. A value of 0.0 means that no "
                                           "obstacles are detected (i.e. clear). A value of -1 means that it is an invalid reading "
                                           "and that caution should be taken.",
                            "parameters": {
                                "type": "object",
                                "properties": {
                                },
                                "required": [],
                            },
                        }
                    },
                    {
                        "type": "function",
                        "function": {
                            "name": "search",
                            "description": "A function which begins a search pattern in which the robot moves around to scan "
                                           "the surrounding area for the target object. Only one direction can be given at one "
                                           "time.",
                            "parameters": {
                                "type": "object",
                                "properties": {
                                    "direction": {
                                        "type": "string",
                                        "description": "Can only be 'left' or 'right', defines the direction in which "
                                                       "the robot will rotate to search for the target object",
                                    },
                                    "target": {
                                        "type": "string",
                                        "description": "The object from the COCO dataset which the robot should search for. "
                                                       "The string should be identical to label from the COCO dataset.",
                                    },
                                },
                                "required": ["direction", "target"]
                            },
                        }
                    },
                    {
                        "type": "function",
                        "function": {
                            "name": "locomote",
                            "description": "A function which makes the robot move in the specified direction for the "
                                           "specified duration. This function is capable of controlling linear "
                                           "velocities and rotational velocity.",
                            "parameters": {
                                "type": "object",
                                "properties": {
                                    "xvel": {
                                        "type": "number",
                                        "description": "A float specifying the target velocity of the robot along the "
                                                       "x-axis (forward and backwards). Where positive values move "
                                                       "the forwards and negative values move the robot backwards. "
                                                       "Values are in meters per second.",
                                    },
                                    "yvel": {
                                        "type": "number",
                                        "description": "A float specifying the target velocity of the robot along the "
                                                       "y-axis (left and right). Where positive values strafe "
                                                       "the robot left and negative values strafe the robot right. "
                                                       "Values are in meters per second.",
                                    },
                                    "theta": {
                                        "type": "number",
                                        "description": "A float specifying the target rotational velocity of the robot. Where positive values rotate "
                                                       "the robot left (anticlockwise) and negative values rotate the "
                                                       "robot right (clockwise)."
                                                       "Values are in radians per second.",
                                    },
                                    "duration": {
                                        "type": "number",
                                        "description": "Optional: A float specifying the length of time in seconds that the "
                                                       "motion should be performed for. Defaults to 3 seconds.",
                                    },
                                },
                                "required": ["xvel", "yvel", "theta", "duration"]
                            },
                        }
                    },
                    {
                        "type": "function",
                        "function": {
                            "name": "pose",
                            "description": "A function which makes the robot look in specified direction for the "
                                           "specified duration. This function is capable controlling the orientation of the robots camera.",
                            "parameters": {
                                "type": "object",
                                "properties": {
                                    "x": {
                                        "type": "number",
                                        "description": "A float specifying the ROLL angle of the robot's camera about the"
                                                       "x-axis. Where positive values roll left/anticlockwise and "
                                                       "negative values roll right/clockwise. Values are in radians.",
                                    },
                                    "y": {
                                        "type": "number",
                                        "description": "A float specifying the PITCH angle of the robot's camera about the"
                                                       "y-axis. Where positive values look down/anticlockwise and "
                                                       "negative values look up/clockwise. Values are in radians.",
                                    },
                                    "z": {
                                        "type": "number",
                                        "description": "A float specifying the YAW angle of the robot's camera about the"
                                                       "z-axis. Where positive values look left/anticlockwise and "
                                                       "negative values look right/clockwise. Values are in radians.",
                                    },
                                    "duration": {
                                        "type": "number",
                                        "description": "Optional: A float specifying the length of time in seconds that the "
                                                       "robot should hold the pose for. Defaults to 3 seconds.",
                                    },
                                },
                                "required": ["x", "y", "z", "duration"]
                            },
                        }
                    },
                    {
                        "type": "function",
                        "function": {
                            "name": "stop",
                            "description": "This function stops whichever function is running, be it 'track', 'chase', or 'search'",
                            "parameters": {
                                "type": "object",
                                "properties": {
                                },
                                "required": [],
                            },
                        }
                    },
                    {
                        "type": "function",
                        "function": {
                            "name": "getRunning",
                            "description": "A function which returns the name of the action which is currently in progress and "
                                           "the name of the target object.",
                            "parameters": {
                                "type": "object",
                                "properties": {
                                },
                                "required": [],
                            },
                        }
                    },
                ],
                model="gpt-4o",
            )
        except openai.AuthenticationError as e:
            print(e.message)
            return None
        print(self.assistant)
        return self.assistant.id

    def DeleteAssistant(self, ass_id):
        response = self.client.beta.assistants.delete(ass_id)
        print(response)
        return response

    def ListAssistants(self):
        my_assistants = self.client.beta.assistants.list(
            order="desc",
        )
        assistant_list_string = ""
        for assistant in my_assistants.data:
            assistant_str = "Name: " + assistant.name
            assistant_str +="\n       ID: " + assistant.id
            timestamp = assistant.created_at
            readable_time = datetime.utcfromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
            assistant_str += "\n       Created at: " + readable_time + "\n"
            assistant_list_string += assistant_str

        print(assistant_list_string)
        return assistant_list_string

