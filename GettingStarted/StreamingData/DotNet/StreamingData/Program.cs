﻿using BOW.Common;
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
    
    static void Main(string[] args)
    {
        Console.WriteLine(Bow.Version());

        List<string> channels = new List<string>() { "vision"};
        _myRobot = Bow.QuickConnect("Streaming Data", channels, true, null, out var quickConnectError);
        
        if (_myRobot == null)
        {
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
                Console.WriteLine("Exception occurred: " + ex.Message);
                break;
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
