using BOW.Data;
using BOW.API;

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

        Robot.Motor.Set(motorSample);
        Thread.Sleep(30);
	}
}

class Program{
	
	static BowRobot? myRobot;

	static void Main(string[] args) 
	{
		try
		{
			var buildinfo = Emgu.CV.CvInvoke.BuildInformation;
		}
		catch (Exception ex)
		{
			Console.WriteLine("Failed to load Emgu OpenCV library. Check installed runtimes.");
			Console.WriteLine(ex);
			System.Environment.Exit(-1);
		}
		
        // Connect to Robot
        AppDomain.CurrentDomain.ProcessExit += (sender, eventArgs) => { Cleanup(); };

        Console.WriteLine(Bow.Version());
        List<string> channels = new List<string>() { "proprioception", "motor" };

        myRobot = Bow.QuickConnect("Controlling Joints", channels, false, null, out var quickConnectError);
        if (myRobot == null){
            Console.WriteLine($"Failed to set up robot: {quickConnectError.Description}");
            System.Environment.Exit(1);
        }

        // Populate list of display items (one per joint) from info in first proprioception sample received
		List<DisplayInfo> jointList = new List<DisplayInfo>();
        while(true){
            try {
                var propSample = myRobot.Proprioception.Get(true);
                if (propSample != null) {
	                foreach (var joint in propSample.RawJoints) {
		                if (joint.Type == Joint.Types.JointTypeEnum.Fixed && !joint.Mimic) {
			                continue;
		                }
		                jointList.Add(new DisplayInfo(joint.Name,joint.Min,joint.Max,joint.Position));
	                }
	                break;
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
	
	static void Cleanup()
	{
		Console.WriteLine("Closing down application");
		myRobot?.Disconnect();
		Bow.CloseClientInterface();
	}
}

