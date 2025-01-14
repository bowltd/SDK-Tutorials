
class myDisplay : Display {
	new public void SetCurrentJoint(){
        /* BASED ON FOLLOWING PYTHON
        motorSample = bow_utils.MotorSample()
        motorSample.ControlMode = bow_utils.MotorSample.USE_DIRECT_JOINTS
        joint = self.list[self.listIndex]
        motorSample.RawJoints.append(bow_utils.Joint(Name=joint.Name, Position=joint.Value))
        Robot.set_modality("motor", motorSample)
        time.sleep(0.03)
        */
	}
}

class Program{
	static void Main(string[] args) {

		myDisplay display = new myDisplay();
		List<DisplayInfo> list = new List<DisplayInfo>();
		list.Add(new DisplayInfo("heads",0.0f,1.0f,0.5f));
	    list.Add(new DisplayInfo("shoulders",0.0f,1.0f,0.75f));
	    list.Add(new DisplayInfo("knees",0.0f,3.0f,0.75f));
	    list.Add(new DisplayInfo("and",1.0f,2.0f,1.5f));
	    list.Add(new DisplayInfo("toes",1.0f,2.0f,1.5f));
	    list.Add(new DisplayInfo("eyes",1.0f,2.0f,1.5f));
	    list.Add(new DisplayInfo("ears",1.0f,2.0f,1.5f));
	    list.Add(new DisplayInfo("mouth",1.0f,2.0f,1.5f));
	    list.Add(new DisplayInfo("and",1.0f,2.0f,1.5f));
	    list.Add(new DisplayInfo("nose",1.0f,2.0f,1.5f));

		display.list = list;
		display.Run();	
    }
}

