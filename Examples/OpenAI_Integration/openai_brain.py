import json
import os
import time
import tkinter

from openai import AsyncOpenAI
from openai.types.beta.threads import Message
from typing_extensions import override
from openai import AsyncAssistantEventHandler

class EventHandler(AsyncAssistantEventHandler):
    @override
    def __init__(self, gui, brain, robot):
        super().__init__()
        self.gui = gui
        self.brain = brain
        self.robot = robot

    @override
    async def on_text_created(self, text) -> None:
        print("\n", end="", flush=True)

    @override
    async def on_text_delta(self, delta, snapshot):
        self.gui.output_text.insert(tkinter.END, delta.value)
        self.gui.output_text.see(tkinter.END)
        self.gui.master.update()
        print(delta.value, end="", flush=True)

    @override
    async def on_message_created(self, message: Message) -> None:
        self.gui.output_text.insert(tkinter.END, "\n")
        self.gui.output_text.see(tkinter.END)
        self.gui.master.update()
        print("\n", "OpenAI Assistant - Message Created")

    @override
    async def on_message_done(self, message: Message) -> None:
        # This method is called when the message stream is complete
        self.gui.output_text.insert(tkinter.END, "\n")
        self.gui.output_text.see(tkinter.END)
        self.gui.master.update()
        full_message = message.content
        self.robot.set_modality("speech", full_message[0].text.value)
        print("\n", "OpenAI Assistant - Message Done")


    @override
    async def on_event(self, event):
        # Retrieve events that are denoted with 'requires_action'
        # since these will have our tool_calls
        if event.event == 'thread.run.requires_action':
            run_id = event.data.id  # Retrieve the run ID from the event data
            await self.handle_requires_action(event.data, run_id)
            print("\n", "OpenAI Assistant - Event Requires Action")

    async def handle_requires_action(self, data, run_id):
        # Iterate through tool calls and create list of required outputs
        tool_outputs = []
        for tool_call in data.required_action.submit_tool_outputs.tool_calls:
            if tool_call.function.name == "retrieveItems":
                output = self.brain.robot_controller.retrieve_items()
                tool_outputs.append({"tool_call_id": tool_call.id, "output": output})
                print("\n", "OpenAI Assistant - retrieveItems tool call requested: ", tool_call.id)

            elif tool_call.function.name == "retrieveSonar":
                output = self.brain.robot_controller.retrieve_sonar()
                tool_outputs.append({"tool_call_id": tool_call.id, "output": output})
                print("\n", "OpenAI Assistant - retrieveSonar tool call requested: ", tool_call.id)

            elif tool_call.function.name == "search":
                parsed_data = json.loads(tool_call.function.arguments)
                target = parsed_data['target']
                direction = parsed_data['direction']
                output = self.brain.robot_controller.startSearch(target, direction)
                tool_outputs.append({"tool_call_id": tool_call.id, "output": str(output)})
                print("\n", "OpenAI Assistant - search tool call requested: ", tool_call.id)

            elif tool_call.function.name == "locomote":
                parsed_data = json.loads(tool_call.function.arguments)
                xvel = float(parsed_data['xvel'])
                yvel = float(parsed_data['yvel'])
                theta = float(parsed_data['theta'])
                dur = float(parsed_data['duration'])
                if dur is None:
                    output = self.brain.robot_controller.start_locomotion(xvel, yvel, theta)
                else:
                    output = self.brain.robot_controller.start_locomotion(xvel, yvel, theta, dur)
                tool_outputs.append({"tool_call_id": tool_call.id, "output": str(output)})
                print("\n", "OpenAI Assistant - locomote tool call requested: ", tool_call.id)

            elif tool_call.function.name == "stop":
                output = self.brain.robot_controller.stop()
                tool_outputs.append({"tool_call_id": tool_call.id, "output": str(output)})
                print("\n", "OpenAI Assistant - stop tool call requested: ", tool_call.id)

            elif tool_call.function.name == "getRunning":
                output = self.brain.robot_controller.get_running()
                tool_outputs.append({"tool_call_id": tool_call.id, "output": output})
                print("\n", "OpenAI Assistant - getRunning tool call requested: ", tool_call.id)

        # Submit all tool_outputs at the same time
        await self.submit_tool_outputs(tool_outputs)

    async def submit_tool_outputs(self, tool_outputs):
        async with self.brain.client.beta.threads.runs.submit_tool_outputs_stream(
                thread_id=self.current_run.thread_id,
                run_id=self.current_run.id,
                tool_outputs=tool_outputs,
                event_handler=EventHandler(self.gui, self.brain, self.robot),
        ) as self.brain.stream_tool:
            await self.brain.stream_tool.until_done()

        print("\n", "OpenAI Assistant - Submit Tool Outputs Complete")


class Brain:
    def __init__(self, controller):
        self.assistant_id = None
        self.client = None
        self.thread = None
        self.tool_outputs = []
        self.robot_controller = controller
        self.stream = None

    async def start(self):
        self.client = AsyncOpenAI()
        print("OpenAI Client Created")
        self.assistant_id = os.getenv("ASSISTANT_ID")

    # Append message to thread and execute
    async def request(self, message_content, role, gui):
        if self.thread is None:
            self.thread = await self.client.beta.threads.create()
            print("OpenAI Thread Created")
        await self.client.beta.threads.messages.create(
            thread_id=self.thread.id,
            role=role,
            content=message_content
        )

        async with self.client.beta.threads.runs.stream(
                thread_id=self.thread.id,
                assistant_id=self.assistant_id,
                event_handler=EventHandler(gui, self, self.robot_controller.robot),
        ) as self.stream:
            await self.stream.until_done()

        print("OpenAI Message Sent")
