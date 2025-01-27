using BOW.Common;
using BOW.Data;
using BOW.API;
using OpenCvSharp;

class Program
{
    static Mat yuvImage = null;
    static Mat rgbImage = new Mat();
    static Window window = new Window("Display Image", WindowFlags.AutoSize);
    static BowRobot? myRobot;
    
    static void Main(string[] args)
    {
        Console.WriteLine(Bow.Version());

        List<string> channels = new List<string>() { "vision"};
        myRobot = Bow.QuickConnect("Streaming Data", channels, true, out var quickConnectError);
        
        if (myRobot == null)
        {
            Console.WriteLine($"Failed to set up robot: {quickConnectError.Description}");
            System.Environment.Exit(1);
        }
        
        int imgW, imgH;
        Console.CancelKeyPress += (sender, eventArgs) => { Cleanup(); };
        
        while (true)
        {
            try
            {
                //Sense
                var getModalitySample = myRobot.GetModality("vision", true);
                if (getModalitySample.Data is ImageSamples imageSamples && imageSamples.Samples[0].NewDataFlag)
                {
                    imgW = (int)imageSamples.Samples[0].DataShape[0];
                    imgH = (int)imageSamples.Samples[0].DataShape[1];
                    
                    if (imageSamples.Samples[0].Data.Length < (int)(imgW*imgH*1.5))
                    {
                        continue;
                    }
                    
                    if (yuvImage == null)
                    {
                        yuvImage = new Mat(
                            (int)imageSamples.Samples[0].DataShape[1]*3/2,
                            (int)(imageSamples.Samples[0].DataShape[0]),
                            MatType.CV_8UC1);
                    }
                    yuvImage.SetArray(imageSamples.Samples[0].Data.ToByteArray());
                    Cv2.CvtColor(yuvImage, rgbImage, ColorConversionCodes.YUV2RGB_IYUV);
                    window.ShowImage(rgbImage);
                    Cv2.WaitKey(1);
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
        yuvImage.Dispose();
        rgbImage.Dispose();
        myRobot?.Disconnect();
        Bow.CloseClientInterface();
    }
}
