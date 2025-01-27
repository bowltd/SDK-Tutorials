using BOW.ClientSDK;
using BOW.Common;
using BOW.Data;
using BOW.API;
using BOW.Structs;

class Program
{
    static private List<BowRobot> robotArray;
    
    static void Main(string[] args)
    {
        AppDomain.CurrentDomain.ProcessExit += (sender, eventArgs) => { Cleanup(); };
        
        // Connect to Robot
        Console.WriteLine(Bow.Version());

        List<string> modalities = new List<string>() { "proprioception", "motor" };
        
        Error error1 = Bow.SetupClient("MultiRobot", (AudioParams) null, true, true);
        var connectError = error1;
        if (!error1.Success)
        {
            System.Environment.Exit(1);
        }
        
        Error error2 = Bow.LoginUser("", "", true);
        connectError = error2;
        if (!error2.Success)
        {
            System.Environment.Exit(1);
        }
        
        Console.WriteLine("Logged in");
        GetRobotsProtoReply robots = Bow.GetRobots(false, true, false);
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
            Bow.CloseClientInterface();
            System.Environment.Exit(1);
        }
        
        Console.WriteLine(robots.Robots.Count);

        robotArray = new List<BowRobot>();
        var robotNames = new List<string> { "SID1 Sim", "Rhino Sim" };
        
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
                Bow.CloseClientInterface();
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

        char decision;
        Console.CancelKeyPress += (sender, eventArgs) => { Cleanup(); };

        while (true)
        {
            if (Console.KeyAvailable)
            {
                // Decide
                decision = Console.ReadKey(true).KeyChar;
                    
                //Act
                var mSamp = new MotorSample();
                mSamp.Locomotion = new VelocityTarget();
                mSamp.Locomotion.TranslationalVelocity = new Vector3();
                mSamp.Locomotion.RotationalVelocity = new Vector3();
                    
                if (decision == 'w')
                {
                    Console.WriteLine("Moving forward");
                    mSamp.Locomotion.TranslationalVelocity.X = 0.5f;
                }
                else if (decision == 's')
                {
                    Console.WriteLine("Moving backward");
                    mSamp.Locomotion.TranslationalVelocity.X = -0.5f;
                }
                else if (decision == 'd')
                {
                    Console.WriteLine("Rotate right");
                    mSamp.Locomotion.RotationalVelocity.Z = -1;
                }
                else if (decision == 'a')
                {
                    Console.WriteLine("Rotate left");
                    mSamp.Locomotion.RotationalVelocity.Z = 1;
                }
                else if (decision == 'e')
                {
                    Console.WriteLine("Strafe right");
                    mSamp.Locomotion.TranslationalVelocity.Y = -1;
                }
                else if (decision == 'q')
                {
                    Console.WriteLine("Strafe left");
                    mSamp.Locomotion.TranslationalVelocity.Y = 1;
                }

                foreach (var r in robotArray)
                {
                    r.SetModality("motor", (int)DataMessage.Types.DataType.Motor, mSamp);
                }
            }
        }
    }
    
    static void Cleanup()
    {
        Console.WriteLine("Closing down application");
        foreach (var r in robotArray)
        {
            r.Disconnect();
        }
        Bow.CloseClientInterface();
    }
}
