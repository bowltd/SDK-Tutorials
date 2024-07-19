import json
import tkinter

from openai import OpenAI
from openai.types.beta.threads import Message, Text
from typing_extensions import override
from openai import AssistantEventHandler

assistant_id = "asst_BF4jtnh3Mt0lAA2p4Uyvzm9f"

class EventHandler(AssistantEventHandler):
    @override
    def __init__(self, gui, brain, robot):
        super().__init__()
        self.gui = gui
        self.brain = brain
        self.robot = robot

    @override
    def on_text_created(self, text) -> None:
        print("\n", end="", flush=True)

    @override
    def on_text_delta(self, delta, snapshot):
        self.gui.output_text.insert(tkinter.END, delta.value)
        self.gui.output_text.see(tkinter.END)
        self.gui.master.update()
        print(delta.value, end="", flush=True)

    @override
    def on_message_created(self, message: Message) -> None:
        self.gui.output_text.insert(tkinter.END, "\n")
        self.gui.output_text.see(tkinter.END)
        self.gui.master.update()
        print("Message Created", message.content)

    @override
    def on_message_done(self, message: Message) -> None:
        # This method is called when the message stream is complete
        self.gui.output_text.insert(tkinter.END, "\n")
        self.gui.output_text.see(tkinter.END)
        self.gui.master.update()
        full_message = message.content
        self.robot.set_modality("speech", full_message[0].text.value)


    @override
    def on_event(self, event):
        # Retrieve events that are denoted with 'requires_action'
        # since these will have our tool_calls
        if event.event == 'thread.run.requires_action':
            run_id = event.data.id  # Retrieve the run ID from the event data
            self.handle_requires_action(event.data, run_id)

    def handle_requires_action(self, data, run_id):
        # Iterate through tool calls and create list of required outputs
        tool_outputs = []
        for tool_call in data.required_action.submit_tool_outputs.tool_calls:
            if tool_call.function.name == "retrieveItems":
                output = self.brain.robot_controller.retrieve_items()
                tool_outputs.append({"tool_call_id": tool_call.id, "output": output})

            elif tool_call.function.name == "search":
                parsed_data = json.loads(tool_call.function.arguments)
                target = parsed_data['target']
                direction = parsed_data['direction']
                output = self.brain.robot_controller.startSearch(target, direction)
                tool_outputs.append({"tool_call_id": tool_call.id, "output": str(output)})

            elif tool_call.function.name == "stop":
                output = self.brain.robot_controller.stop()
                tool_outputs.append({"tool_call_id": tool_call.id, "output": str(output)})

            elif tool_call.function.name == "getRunning":
                output = self.brain.robot_controller.get_running()
                tool_outputs.append({"tool_call_id": tool_call.id, "output": output})

        # Submit all tool_outputs at the same time
        self.submit_tool_outputs(tool_outputs)

    def submit_tool_outputs(self, tool_outputs):
        with self.brain.client.beta.threads.runs.submit_tool_outputs_stream(
                thread_id=self.current_run.thread_id,
                run_id=self.current_run.id,
                tool_outputs=tool_outputs,
                event_handler=EventHandler(self.gui, self.brain, self.robot),
        ) as self.brain.stream_tool:
            self.brain.stream_tool.until_done()


class Brain:
    def __init__(self, controller):
        self.client = OpenAI()
        self.thread = self.client.beta.threads.create()
        self.tool_outputs = []
        self.robot_controller = controller
        self.stream = None

    # Append message to thread and execute
    def request(self, message_content, role, gui):

        message = self.client.beta.threads.messages.create(
            thread_id=self.thread.id,
            role=role,
            content=message_content
        )

        with self.client.beta.threads.runs.stream(
                thread_id=self.thread.id,
                assistant_id=assistant_id,
                event_handler=EventHandler(gui, self, self.robot_controller.robot),
        ) as self.stream:
            self.stream.until_done()