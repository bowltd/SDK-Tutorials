import bow_client as bow
import bow_utils
import logging
import sys
import math
import time
import display


modalities = ["proprioception", "motor"]
audio_params = bow_utils.AudioParams(Backends=[""],
										SampleRate=16000,
										Channels=1,
										SizeInFrames=True,
										TransmitRate=30)

# Disable logging once connection established (so we can see the display)
log = bow_utils.create_logger("BOW Tutorial", logging.INFO)
log.info(bow.version())
for handler in log.handlers[:]:  # Iterate over a copy of the list
    if isinstance(handler, logging.StreamHandler):
        log.removeHandler(handler)

Robot, error = bow.quick_connect(pylog=log, verbose=False, modalities=["motor", "proprioception"])
if not error.Success:
	log.error("Failed to connect to robot", error)
	sys.exit()

# Populate list of display items from first proprioception sample
jointList = []
while(True):
	prop_msg, err = Robot.get_modality("proprioception", True)
	if err.Success and len(prop_msg.RawJoints) > 0:
		for joint in prop_msg.RawJoints:
			if joint.Type == bow_utils.Joint.FIXED:
				continue
			jointList.append(display.DisplayInfo(joint.Name,joint.Min,joint.Max,joint.Position))
		break			
	time.sleep(0.1)  # Sample rate control


# Derived class so we can see here how to contruct a motor message
class myDisplay(display.Display):
	def SetCurrentJoint(self):
		motorSample = bow_utils.MotorSample()
		motorSample.ControlMode = bow_utils.MotorSample.USE_DIRECT_JOINTS
		joint = self.list[self.listIndex]
		motorSample.RawJoints.append(bow_utils.Joint(Name=joint.Name, Position=joint.Value))
		Robot.set_modality("motor", motorSample)
		time.sleep(0.03)

# Launch the ncurses display
display = myDisplay()
display.list = jointList
display.Run()