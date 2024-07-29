from openai import OpenAI

# asst_BF4jtnh3Mt0lAA2p4Uyvzm9f
client = OpenAI()

assistant = client.beta.assistants.create(
    name="BOW >< OpenAI Brain",
    instructions="You are Bowie, my robot helper, you are here to help me around the home with tasks such as finding"
                 "things and alerting other people if I need help."
                 
                 "Engage with me personably, be friendly and call me by name which is 'George'."
                 
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

print(assistant)
