using BOW.Common;
using BOW.Data;
using BOW.SDK.Core;
using BOW.Structs;

// Derive a Display class and override its dummy SetCurrentJoint method so we can see here how to contruct a motor message
class myDisplay : Display {
	public BowRobot Robot;
	public myDisplay(BowRobot robot) : base() {
		Robot = robot;
	}
	public override void SetCurrentJoint(){
		var joint = list[listIndex];
        var motorSample = new MotorSample(){
        	ControlMode = MotorSample.Types.ControlModeEnum.UseDirectJoints,
        };
        motorSample.RawJoints.Add(new BOW.Data.Joint{
        		Name=joint.Name, 
        		Position=joint.Value,
        	});
        Robot.SetModality("motor",(int)DataMessage.Types.DataType.Motor,motorSample);
        System.Threading.Thread.Sleep(30);
	}
}

class Program{
	static void Main(string[] args) {

        // Connect to Robot
        Console.WriteLine(BowClient.Version());
        List<string> modalities = new List<string>() { "proprioception", "motor" };
        Error quickConnectError;
        var myRobot = BowClient.QuickConnect("BOW Tutorial", modalities, false, out quickConnectError);
        if (myRobot == null){
            Console.WriteLine($"Failed to set up robot: {quickConnectError.Description}");
            System.Environment.Exit(1);
        }

        // Populate list of display items (one per joint) from info in first proprioception sample received
		List<DisplayInfo> jointList = new List<DisplayInfo>();
        while(true){
            try {
                var getMsg = myRobot.GetModality("proprioception", true);
                if (getMsg.Error.Success) {
                    if (getMsg.Data is ProprioceptionSample propSample) {
                        foreach (var joint in propSample.RawJoints) {
                        	if (joint.Type == BOW.Data.Joint.Types.JointTypeEnum.Fixed) {
                        		continue;
                        	}
                       		jointList.Add(new DisplayInfo(joint.Name,joint.Min,joint.Max,joint.Position));
                        }
                        break;
                    }
                }
            }
            catch (Exception ex) {
                Console.WriteLine("Exception occurred: " + ex.Message);
                Thread.Sleep(250);
            }
        }

        // Launch the display
		myDisplay display = new myDisplay(myRobot);
		display.list = jointList;

		// Start the sampling loop
		display.Run();	
    }
}

