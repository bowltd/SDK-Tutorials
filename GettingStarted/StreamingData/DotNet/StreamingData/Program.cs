using BOW.Common;
using BOW.Data;
using BOW.API;
using Emgu.CV;
using Emgu.CV.CvEnum;

class Program
{
    private static BowRobot? _myRobot;
    private static bool _windowsCreated = false;
    private static Dictionary<string, string> _windowNames = new Dictionary<string, string>();
    
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
                    var yuvImage = new Mat(imageHeigth*3/2, imageWidth, DepthType.Cv8U, 1);
                    yuvImage.SetTo(thisIm.Data.ToByteArray());

                    CvInvoke.CvtColor(yuvImage, rgbImage, ColorConversion.Yuv2RgbIyuv);

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

                    var depthImage = new Mat(imageHeigth*3/2, imageWidth, DepthType.Cv16U, 1);
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

        List<string> channels = new List<string>() { "vision"};
        
        _myRobot = Bow.QuickConnect("StreamingData", channels, true, null, out var quickConnectError);
        
        if (_myRobot == null) {
             Console.WriteLine($"Failed to set up robot: {quickConnectError.Description}");
             System.Environment.Exit(1);
        }
        
        Console.CancelKeyPress += (sender, eventArgs) => { Cleanup(); };
        AppDomain.CurrentDomain.ProcessExit += (sender, eventArgs) => { Cleanup(); };
        
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
            }
            catch (Exception ex)
            {
                Console.WriteLine("Exception occurred: " + ex); 
                break;
            }
        }
    }
    
    static void Cleanup()
    {
        Console.WriteLine("Closing down application");
        _myRobot?.Disconnect();
        Bow.StopEngine();
        CvInvoke.DestroyAllWindows();
    }
}
