using BOW.ClientSDK;
using BOW.Common;
using BOW.Data;
using BOW.API;
using BOW.RobotProto;
using Emgu.CV;

class Program
{
    static private List<BowRobot> robotArray;
    private static Dictionary<string, string> _windowNames = new Dictionary<string, string>();
    private static int _numRobots = 2;
    
    static void ShowAllImages(ImageSamples imSamples)
    {
        for (int i = 0; i < imSamples.Samples.Count; i++)
        {
            var thisIm = imSamples.Samples[i];

            var imageWidth = (int)thisIm.DataShape[0];
            var imageHeigth = (int)thisIm.DataShape[1];
            
            if (thisIm.NewDataFlag)
            {
                if (thisIm.ImageType == ImageSample.Types.ImageTypeEnum.Rgb)
                {
                    var expectedSize = imageWidth * imageHeigth * 3 / 2;
                    if (thisIm.Data.Length < expectedSize)
                    {
                        continue;
                    }
                    
                    var rgbImage = new Mat();
                    var yuvImage = new Mat(imageHeigth*3/2, imageWidth, Emgu.CV.CvEnum.DepthType.Cv8U, 1);
                    yuvImage.SetTo(thisIm.Data.ToByteArray());
                    
                    CvInvoke.CvtColor(yuvImage, rgbImage, Emgu.CV.CvEnum.ColorConversion.Yuv2RgbIyuv);

                    if (!_windowNames.ContainsKey(thisIm.Source))
                    {
                        var windowName = $"RobotView{_windowNames.Count} - {thisIm.Source}";
                        Console.WriteLine(windowName);
                        _windowNames[thisIm.Source] = windowName;
                        CvInvoke.NamedWindow(windowName);
                        CvInvoke.WaitKey(1);
                    }
                    
                    CvInvoke.Imshow(_windowNames[thisIm.Source], rgbImage);
                    CvInvoke.WaitKey(1);
                } 
                else if (thisIm.ImageType == ImageSample.Types.ImageTypeEnum.Depth)
                {
                    var expectedSize = imageWidth * imageHeigth;
                    if (thisIm.Data.Length < expectedSize)
                    {
                        continue;
                    }
                    
                    var depthImage = new Mat(imageHeigth*3/2, imageWidth, Emgu.CV.CvEnum.DepthType.Cv16U, 1);
                    depthImage.SetTo(thisIm.Data.ToByteArray());

                    if (!_windowNames.ContainsKey(imSamples.Samples[i].Source))
                    {
                        var windowName = $"RobotView{_windowNames.Count} - {thisIm.Source}";
                        Console.WriteLine(windowName);
                        _windowNames[thisIm.Source] = windowName;
                        CvInvoke.NamedWindow(windowName);
                        CvInvoke.WaitKey(1);
                    }
                    
                    CvInvoke.Imshow(_windowNames[thisIm.Source], depthImage);
                    CvInvoke.WaitKey(1);
                }
                else
                {
                    Console.WriteLine("Unknown image type");
                }
            }
        }
    }

    static MotorSample KeyboardControl()
    {
        var mSamp = new MotorSample();
        mSamp.Locomotion = new VelocityTarget();
        mSamp.Locomotion.TranslationalVelocity = new Vector3();
        mSamp.Locomotion.RotationalVelocity = new Vector3();
        mSamp.GazeTarget = new GazeTarget();
        mSamp.GazeTarget.GazeVector = new Vector3();
        
        if (Console.KeyAvailable)
        {
            char decision;
            decision = Console.ReadKey(true).KeyChar;
            
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
            else if (decision == 'i')
            {
                Console.WriteLine("Look up");
                mSamp.GazeTarget.GazeVector.X = -0.2f;
            }
            else if (decision == 'k')
            {
                Console.WriteLine("Look down");
                mSamp.GazeTarget.GazeVector.X = 0.2f;
            }
            else if (decision == 'j')
            {
                Console.WriteLine("Look left");
                mSamp.GazeTarget.GazeVector.Y = 0.2f;
            }
            else if (decision == 'l')
            {
                Console.WriteLine("Look right");
                mSamp.GazeTarget.GazeVector.Y = -0.2f;
            }
            else if (decision == 'o')
            {
                Console.WriteLine("Tilt left");
                mSamp.GazeTarget.GazeVector.Z = -0.2f;
            }
            else if (decision == 'u')
            {
                Console.WriteLine("Tilt right");
                mSamp.GazeTarget.GazeVector.Z = 0.2f;
            }
        }

        return mSamp;
    }

    static int GetRobotSelection(string prompt, int robotCount, List<int> selected)
    {
        while (true)
        {
            try
            {
                Console.Write(prompt);
                string input = Console.ReadLine();
                int idx = int.Parse(input);

                if (idx >= 0 && idx < robotCount)
                {
                    if (selected.Contains(idx))
                    {
                        Console.WriteLine("Cannot choose the same robot again");
                        continue;
                    }
                    return idx;
                }
                else
                {
                    Console.WriteLine("Invalid index. Please try again.");
                }
            }
            catch (FormatException)
            {
                Console.WriteLine("Invalid input. Please enter a valid integer index.");
            }
        }
    }
    
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
        
        Console.WriteLine(Bow.Version());

        List<string> channels = new List<string>() { "vision", "motor" };
        
        Error setupError = Bow.Setup("Multiple Robots",  true, true, null);
        if (!setupError.Success)
        {
            Console.WriteLine($"Setup failed: {setupError.Description}");
            System.Environment.Exit(1);
        }
        
        Error loginError = Bow.LoginUser("", "", true);
        if (!loginError.Success)
        {
            Console.WriteLine($"Login failed: {loginError.Description}");
            System.Environment.Exit(1);
        }
        Console.WriteLine("Logged in");
        
        GetRobotsProtoReply robots = Bow.GetRobots(false, true, false);
        if (!robots.LocalSearchError.Success)
        {
            Console.WriteLine(robots.LocalSearchError.Description);
        }
        
        if (!robots.RemoteSearchError.Success)
        {
            Console.WriteLine($"Get Robots failed: {robots.RemoteSearchError.Description}");
            System.Environment.Exit(1);
        }
        
        if (robots.Robots.Count == 0)
        {
            Console.WriteLine("No robots found");
            System.Environment.Exit(1);
        }

        var availableRobots = new List<Robot>();
        foreach (var robot in robots.Robots)
        {
            if (robot.RobotState.Available)
            {
                availableRobots.Add(robot);
            }
        }
        
        Console.WriteLine("Available Robots:");
        for (int i = 0; i < availableRobots.Count; i++)
        {
            Console.WriteLine($"{i}: {availableRobots[i].Name}");
        }


        if (availableRobots.Count < _numRobots)
        {
            Console.WriteLine($"Not enough available robots. {_numRobots} expected");
            System.Environment.Exit(1);
        }
        
        var robotIndices = new List<int>();
        for (int i = 0; i < _numRobots; i++)
        {
            robotIndices.Add(GetRobotSelection($"Select robot {i+1} of {_numRobots}: ", availableRobots.Count, robotIndices));
        }
        
        robotArray = new List<BowRobot>();
        foreach (var idx in robotIndices)
        {
            robotArray.Add(new BowRobot(availableRobots[idx]));
        }
        
        AppDomain.CurrentDomain.ProcessExit += (sender, eventArgs) => { Cleanup(); };
        Console.CancelKeyPress += (sender, eventArgs) => { Cleanup(); };
        
        foreach (var r in robotArray)
        {
            Error connectError = r.Connect();
            if (!connectError.Success)
            {
                Console.WriteLine("Could not connect with robot " + r.RobotDetails.RobotId);
                System.Environment.Exit(1);
            }
            
            foreach (string channel in channels)
            {
                Error openModError = r.OpenChannel(channel);
                if (!openModError.Success)
                {
                    Console.WriteLine("Failed to open " + channel + " channel: " + openModError.Description);
                }
            }
        }
        
        ImageSamples allImages = new ImageSamples();
        while (true)
        {
            allImages.Samples.Clear();
            foreach (var r in robotArray)
            {
                var rImages = r.Vision.Get(true);
                if (rImages != null)
                {
                    foreach (var rImage in rImages.Samples)
                    {
                        rImage.Source = $"{r.RobotDetails.Name}_{rImage.Source}";
                        allImages.Samples.Add(rImage);
                    }
                }
            }

            if (allImages.Samples.Count > 0)
            {
                ShowAllImages(allImages);
            }
            
            var mSamp = KeyboardControl();
            foreach (var r in robotArray)
            {
                r.Motor.Set(mSamp);
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
