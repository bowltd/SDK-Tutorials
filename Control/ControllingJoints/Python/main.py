import bow_api
import bow_data

import logging
import sys
import time
import display

# Derive a Display class and override its dummy SetCurrentJoint method so we can see here how to contruct a motor message
class myDisplay(display.Display):
	def SetCurrentJoint(self):
		joint = self.list[self.listIndex]
		motorSample = bow_data.MotorSample()
		motorSample.ControlMode = bow_data.MotorSample.USE_DIRECT_JOINTS
		motorSample.RawJoints.append(bow_data.Joint(Name=joint.Name, Position=joint.Value))
		robot.motor.set(motorSample)
		time.sleep(0.03)

print(bow_api.version())

# Connect to a robot
robot, error = bow_api.quick_connect(app_name="Controlling Joints", channels=["motor", "proprioception"], verbose=False)
if not error.Success:
	print("Failed to connect to robot", error)
	sys.exit()

# Populate list of display items (one per joint) from info in first proprioception sample received
jointList = []
while True:
	prop_msg, err = robot.proprioception.get(True)
	if err.Success and len(prop_msg.RawJoints) > 0:
		for joint in prop_msg.RawJoints:
			if joint.Type == bow_data.Joint.FIXED:
				continue
			jointList.append(display.DisplayInfo(joint.Name,joint.Min,joint.Max,joint.Position))
		break			
	time.sleep(0.1)

# Launch the display
display = myDisplay()
display.list = jointList

# Start the sampling loop
try:
	display.Run()
except KeyboardInterrupt or SystemExit:
	print("Closing down")
	stopFlag = True

robot.disconnect()
bow_api.close_client_interface()