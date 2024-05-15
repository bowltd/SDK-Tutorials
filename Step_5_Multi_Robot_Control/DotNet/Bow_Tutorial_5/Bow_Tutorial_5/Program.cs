using BOW.ClientSDK;
using BOW.Common;
using BOW.Data;
using BOW.SDK.Core;
using BOW.Structs;

class Program
{
    static void Main(string[] args)
    {
        
        // Connect to Robot
        Console.WriteLine(BowClient.Version());

        List<string> modalities = new List<string>() { "proprioception", "motor" };
        
        Error error1 = BowClient.SetupClient("MultiRobot", (AudioParams) null, true, true);
        var connectError = error1;
        if (!error1.Success)
        {
            System.Environment.Exit(1);
        }
        
        Error error2 = BowClient.LoginUser("", "", true);
        connectError = error2;
        if (!error2.Success)
        {
            System.Environment.Exit(1);
        }
        
        
        Console.WriteLine("Logged in");
        GetRobotsProtoReply robots = BowClient.GetRobots(true, true, false);
        if (!robots.LocalSearchError.Success)
        {
            connectError = robots.LocalSearchError;
            Console.WriteLine(robots.LocalSearchError.Description);
        }
        
        if (!robots.RemoteSearchError.Success)
        {
            connectError = robots.RemoteSearchError;
            Console.WriteLine(robots.RemoteSearchError.Description);
        }
        
        if (robots.Robots.Count == 0)
        {
            connectError = new Error()
            {
                Success = false,
                Code = -1,
                Description = "No robots found"
            };
            BowClient.CloseClientInterface();
            System.Environment.Exit(1);
        }
        
        Console.WriteLine(robots.Robots.Count);

        List<BowRobot> robotArray = new List<BowRobot>();
        var robotNames = new List<string> { "leArm Sim", "mycobot_280_pi Sim" };
        
        foreach (var n in robotNames)
        {
            var found = false;
            foreach (var r in robots.Robots)
            {
                Console.WriteLine(r.Name);
                if (r.Name == n)
                {
                    found = true;
                    robotArray.Add(new BowRobot(r));
                }
            }
            
            if (!found)
            {
                Console.WriteLine($"Failed to find robot: {n}");
                System.Environment.Exit(1);
            }
        }
        
        foreach (var r in robotArray)
        {
            Error error3 = r.Connect();
            connectError = error3;
            if (!error3.Success)
            {
                Console.WriteLine("Could not connect with robot " + r.RobotDetails.RobotId);
                BowClient.CloseClientInterface();
                System.Environment.Exit(1);
            }
            
            foreach (string modality in modalities)
            {
                Error error4 = r.OpenModality(modality);
                if (!error4.Success)
                {
                    connectError = error3;
                    Console.WriteLine("Failed to open " + modality + " modality: " + error4.Description);
                }
            }
        }
        
        var robotEffectors = new List<string>();
        foreach (var r in robotArray)
        {
            var listOfEffectors = new List<string>();
            // We will wait until we have successfully received a proprioception message in order to get a list of effectors
            while (true)
            {
                try
                {
                    var getMsg = r.GetModality("proprioception", true);
                    if (getMsg.Error.Success)
                    {
                        if (getMsg.Data is ProprioceptionSample propSample)
                        {
                            if (propSample.Effectors.Count == 0)
                            {
                                continue;
                            }
                        
                            robotEffectors.Add(propSample.Effectors[0].EffectorLinkName);
                            break;
                        }
                    }
                }
                catch (Exception ex)
                {
                    Console.WriteLine("Exception occurred: " + ex.Message);
                    Thread.Sleep(250);
                }
            }
        }
        
        //Act
        var circleRadius = 0.2; // Radius of the circle
        var circleHeight = 0.3; // Z-axis height of the circle
        var stepSize = 0.05; // Step size in radians
        var repeatCount = 100; // Number of repetitions at the final angle

        double x = 0, y = 0, z = 0;
        while (true) // Loop continuously
        {
            for (double angle = 0; angle <= 2 * Math.PI; angle += stepSize)
            { 
                x = circleRadius * Math.Cos(angle);
                y = circleRadius * Math.Sin(angle);
                z = circleHeight;

                SendObjective(robotArray, robotEffectors, x, y, z);
                Thread.Sleep(200);
            }
        }
    }
    
    static void SendObjective(List<BowRobot> robotsArray, List<string> robotEffectors, double x, double y, double z)
    {
        for (int i = 0; i < robotsArray.Count; i++)
        {
            var thisRobot = robotsArray[i];
            Console.WriteLine($"Sending objective to {thisRobot.RobotDetails.Name}: {x}, {y}, {z}");
            try
            {
                var mSamp = new MotorSample();
                mSamp.Objectives.Clear();
                mSamp.Objectives.Add(new ObjectiveCommand
                {
                    TargetEffector = robotEffectors[i],
                    ControlMode = ControllerEnum.PositionController,
                    PoseTarget = new PoseTarget
                    {
                        Action = ActionEnum.Goto,
                        TargetType = PoseTarget.Types.TargetTypeEnum.Transform,
                        TargetScheduleType = PoseTarget.Types.SchedulerEnum.Instantaneous,
                        Transform = new Transform
                        {
                            Position = new Vector3
                            {
                                X = (float)x,
                                Y = (float)y,
                                Z = (float)z
                            }
                        },
                        OptimiserSettings = new IKOptimiser
                        {
                            Preset = IKOptimiser.Types.OptimiserPreset.HighAccuracy,
                        },
                    },
                    Enabled = true,
                });

                var setError = thisRobot.SetModality("motor", (int)DataMessage.Types.DataType.Motor, mSamp);
                if (!setError.Success)
                {
                    Console.WriteLine($"Error calling setModality motor {thisRobot.RobotDetails.Name}: {setError.Description}");
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Exception occurred {thisRobot.RobotDetails.Name}: { ex.Message}");
            }
        }
        
    }
}
