using BOW.Common;
using BOW.Data;
using BOW.API;
using BOW.Structs;

class Program
{
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
        
        AppDomain.CurrentDomain.ProcessExit += (sender, eventArgs) => { Cleanup(); };
        Console.CancelKeyPress += (sender, eventArgs) => { Cleanup(); };

        // Connect to Robot
        Console.WriteLine(Bow.Version());

        List<string> channels = new List<string>() { "proprioception", "motor" };

        myRobot = Bow.QuickConnect("Inverse Kinematics", channels, true, null, out var quickConnectError);
        
        if (myRobot == null)
        {
            Console.WriteLine($"Failed to set up robot: {quickConnectError.Description}");
            System.Environment.Exit(1);
        }

        var listOfEffectors = new List<string>();
        var listOfReach = new List<float>();
        var listOfUpDown = new List<float>();
        var listOfParts = new List<string>();
        // We will wait until we have successfully received a proprioception message in order to get a list of effectors
        while (true)
        {
            try
            {
                var propSample = myRobot.Proprioception.Get(true);
                if (propSample != null)
                {
                    if (propSample.Effectors.Count == 0)
                    {
                        continue;
                    }

                    foreach (var b in propSample.Parts)
                    {
                        foreach (var eff in b.Effectors)
                        {
                            //only get controllable effectors. This removes all effectors that don't have moveable joints within their kinematic chain
                            if (!eff.IsControllable)
                            {
                                continue;
                            }

                            listOfParts.Add(eff.Type.ToString());
                            listOfEffectors.Add(eff.EffectorLinkName);
                            listOfReach.Add(eff.Reach);
                            if (eff.EndTransform.Position.Z > eff.RootTransform.Position.Z)
                            {
                                //Effector is by default higher than root hence height offset should be positive
                                listOfUpDown.Add(1f);
                            }
                            else
                            {
                                //Effector is by default lower than effector root hence height offset should be negative
                                listOfUpDown.Add(-1f);
                            }
                        }
                    }
                    break;
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine("Exception occurred: " + ex.Message);
                Thread.Sleep(250);
            }
        }
        
        //Decide
        var selectedEffector = "";
        var selectedReach = 0f;
        var selectedUpDown = 1f;
        while (true)
        {
            Console.WriteLine("Please select an option:");
            for (int i = 0; i < listOfEffectors.Count; i++)
            {
                Console.WriteLine($"{i + 1}. {listOfEffectors[i]} of type {listOfParts[i]} " +
                                  $"with reach of {listOfReach[i]}m and " +
                                  $"default direction {listOfUpDown[i]}");
            }
        
            // Get user input
            Console.Write("Enter your choice (number): ");
            int userInput = Convert.ToInt32(Console.ReadLine());
        
            // Check if the input is valid
            
            if (userInput > 0 && userInput <= listOfEffectors.Count)
            {
                selectedEffector = listOfEffectors[userInput - 1];
                selectedReach = listOfReach[userInput - 1];
                selectedUpDown = listOfUpDown[userInput - 1];
                Console.WriteLine($"You selected: {selectedEffector}");
                break;
            }
            
            Console.WriteLine("Invalid choice. Please run the program again and select a valid number.");
        }
        
        //Act
        var circleRadius = selectedReach * 0.25; // Radius of the circle
        var circleHeight = selectedReach * 0.3; // Z-axis height of the circle
        var wobbleAmplitude = selectedReach * 0.05f;
        var wobbleFreqMultiplier = 6f;
        var stepSize = 0.05; // Step size in radians
        var repeatCount = 100; // Number of repetitions at the final angle

        double x = 0, y = 0, z = 0;
        while (true) // Loop continuously
        {
            for (double angle = 0; angle <= 2 * Math.PI; angle += stepSize)
            { 
                x = circleRadius * Math.Cos(angle);
                y = circleRadius * Math.Sin(angle);
                z = selectedUpDown*(circleHeight + (wobbleAmplitude * Math.Cos(angle*wobbleFreqMultiplier))) ;

                SendObjective(myRobot, selectedEffector, x, y, z);
                Thread.Sleep(200);
            }
        }
        
        static void Cleanup()
        {
            Console.WriteLine("Closing down application");
            myRobot?.Disconnect();
            Bow.CloseClientInterface();
        }
    }
    
    static void SendObjective(BowRobot myRobot, string selectedEffector, double x, double y, double z)
    {
        Console.WriteLine($"Sending objective: {x}, {y}, {z}");
        try
        {
            var mSamp = new MotorSample();
            mSamp.Objectives.Clear();
            mSamp.Objectives.Add(new ObjectiveCommand
            {
                TargetEffector = selectedEffector,
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
                    LocalObjectiveWeights = new LocalObjectiveWeights
                    {
                        Position = 1,
                        Orientation = 0
                    }
                },
                Enabled = true,
            });
            mSamp.IKSettings = new IKOptimiser
            {
                Preset = IKOptimiser.Types.OptimiserPreset.HighAccuracy,
                GlobalObjectiveWeights = new GlobalObjectiveWeights
                {
                    Displacement = 1f
                }
            };

            var setError = myRobot.Motor.Set(mSamp);
            if (!setError.Success)
            {
                Console.WriteLine($"Error calling Motor.Set: {setError.Description}");
            }
        }
        catch (Exception ex)
        {
            Console.WriteLine("Exception occurred: " + ex.Message);
            return;
        }
    }
}
