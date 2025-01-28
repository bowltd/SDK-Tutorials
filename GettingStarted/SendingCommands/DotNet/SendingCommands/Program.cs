using BOW.Data;
using BOW.API;
using OpenCvSharp;

class Program
{
    private static BowRobot? _myRobot;
    private static bool _windowsCreated = false;
    private static Dictionary<string, string> _windowNames = new Dictionary<string, string>();
    
    static void ShowAllImages(ImageSamples imSamples)
    {
        if (!_windowsCreated)
        {   
            for (int i = 0; i < imSamples.Samples.Count; i++)
            {
                var windowName = $"RobotView{i} - {imSamples.Samples[i].Source}";
                Console.WriteLine(windowName);
                _windowNames[imSamples.Samples[i].Source] = windowName;
                Cv2.NamedWindow(windowName);
                Cv2.WaitKey(1);
            }
            _windowsCreated = true;
        }

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
                    var yuvImage = new Mat(imageHeigth*3/2, imageWidth, MatType.CV_8UC1);
                    yuvImage.SetArray(thisIm.Data.ToByteArray());
                    
                    Cv2.CvtColor(yuvImage, rgbImage, ColorConversionCodes.YUV2RGB_IYUV);
                    Cv2.ImShow(_windowNames[imSamples.Samples[i].Source], rgbImage);
                    Cv2.WaitKey(1);
                } 
                else if (thisIm.ImageType == ImageSample.Types.ImageTypeEnum.Depth)
                {
                    var expectedSize = imageWidth * imageHeigth;
                    if (thisIm.Data.Length < expectedSize)
                    {
                        continue;
                    }
                    
                    var depthImage = new Mat(imageHeigth*3/2, imageWidth, MatType.CV_16UC1);
                    depthImage.SetArray(thisIm.Data.ToByteArray());
                    Cv2.ImShow(_windowNames[imSamples.Samples[i].Source], depthImage);
                    Cv2.WaitKey(1);
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
    
    static void Main(string[] args)
    {
        Console.WriteLine(Bow.Version());

        List<string> channels = new List<string>() { "vision", "motor" };
        
        _myRobot = Bow.QuickConnect("Sending Commands", channels, true, null, out var quickConnectError);
        
        if (_myRobot == null)
        {
            Console.WriteLine($"Failed to set up robot: {quickConnectError.Description}");
            System.Environment.Exit(-1);
        }
        Console.CancelKeyPress += (sender, eventArgs) => { Cleanup(); };
        
        while (true)
        {
            try
            {
                //Sense
                var imageSamples = _myRobot.Vision.Get(true);
                if (imageSamples != null)
                {
                    ShowAllImages(imageSamples);
                }
                
                // Decide
                var mSamp = KeyboardControl();
                
                //Act
                _myRobot.Motor.Set(mSamp);
            }
            catch (Exception ex)
            {
                Console.WriteLine("Exception occurred: " + ex.Message);
            }
        }
    }

    static void Cleanup()
    {
        Console.WriteLine("Closing down application");
        _myRobot?.Disconnect();
        Bow.CloseClientInterface();
    }
}
