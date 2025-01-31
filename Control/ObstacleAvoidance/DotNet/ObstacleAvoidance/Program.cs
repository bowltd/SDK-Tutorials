using BOW.API;
using BOW.Common;
using BOW.Data;
using Emgu.CV;
using Google.Protobuf.Collections;
using Range = BOW.Data.Range;

class Program {
    
    private static Dictionary<string, string> _windowNames = new Dictionary<string, string>();
    
    // Display images using CV
    static void ShowAllImages(ImageSamples imSamples) {
        for (int i = 0; i < imSamples.Samples.Count; i++) {
            var thisIm = imSamples.Samples[i];
            var imageWidth = (int)thisIm.DataShape[0];
            var imageHeigth = (int)thisIm.DataShape[1];
            
            if (thisIm.NewDataFlag) {
                if (thisIm.ImageType == ImageSample.Types.ImageTypeEnum.Rgb) {
                    var expectedSize = imageWidth * imageHeigth * 3 / 2;
                    if (thisIm.Data.Length < expectedSize) {
                        continue;
                    }
                    
                    var rgbImage = new Mat();
                    var yuvImage = new Mat(imageHeigth*3/2, imageWidth, Emgu.CV.CvEnum.DepthType.Cv8U, 1);
                    yuvImage.SetTo(thisIm.Data.ToByteArray());
                    
                    CvInvoke.CvtColor(yuvImage, rgbImage, Emgu.CV.CvEnum.ColorConversion.Yuv2RgbIyuv);

                    if (!_windowNames.ContainsKey(thisIm.Source)) {
                        var windowName = $"RobotView{_windowNames.Count} - {thisIm.Source}";
                        Console.WriteLine(windowName);
                        _windowNames[thisIm.Source] = windowName;
                        CvInvoke.NamedWindow(windowName);
                        CvInvoke.WaitKey(1);
                    }
                    
                    CvInvoke.Imshow(_windowNames[thisIm.Source], rgbImage);
                    CvInvoke.WaitKey(1);
                } 
                else if (thisIm.ImageType == ImageSample.Types.ImageTypeEnum.Depth) {
                    var expectedSize = imageWidth * imageHeigth;
                    if (thisIm.Data.Length < expectedSize) {
                        continue;
                    }
                    
                    var depthImage = new Mat(imageHeigth*3/2, imageWidth, Emgu.CV.CvEnum.DepthType.Cv16U, 1);
                    depthImage.SetTo(thisIm.Data.ToByteArray());

                    if (!_windowNames.ContainsKey(imSamples.Samples[i].Source)) {
                        var windowName = $"RobotView{_windowNames.Count} - {thisIm.Source}";
                        Console.WriteLine(windowName);
                        _windowNames[thisIm.Source] = windowName;
                        CvInvoke.NamedWindow(windowName);
                        CvInvoke.WaitKey(1);
                    }
                    
                    CvInvoke.Imshow(_windowNames[thisIm.Source], depthImage);
                    CvInvoke.WaitKey(1);
                } else {
                    Console.WriteLine("Unknown image type");
                }
            }
        }
    }

    // Identify the ultrasound that is furthest forward on the robot
    static string IdentifyFrontSonar(RepeatedField<BOW.Data.Range>? RangeSensors) {
        float front_sonar_x_pos = -100;
        string front_sonar_name = "";
        foreach (var Sensor in RangeSensors){
            if (Sensor.OperationType == Range.Types.OperationTypeEnum.Ultrasound) {
                if (Sensor.Transform.Position.X > front_sonar_x_pos) {
                    front_sonar_x_pos = Sensor.Transform.Position.X;
                    front_sonar_name = Sensor.Source;
                }
            }
        }
        return front_sonar_name;
    }
    
    
    static BowRobot? robot;
    
    static void Main() {
        
        try {
            var buildinfo = Emgu.CV.CvInvoke.BuildInformation;
        }
        catch (Exception ex) {
            Console.WriteLine("Failed to load Emgu OpenCV library. Check installed runtimes.");
            Console.WriteLine(ex);
        }
        AppDomain.CurrentDomain.ProcessExit += (sender, eventArgs) => { Cleanup(); };
    
        // Step 1: Quick Connect
        Error connectError;
        BowRobot? robot = Bow.QuickConnect(
            appName: "BOW_Example",
            channels: new List<string> { "vision", "motor", "exteroception"},
            verbose: true,
            audioParams: null,
            connectError: out connectError
        );
        
        if (!connectError.Success){
            Console.WriteLine($"Quick connect failed: {connectError.Description}");
            return;
        }

        // Step 2: Sample the exteroception channel to identify front-most ultrasound sensor
        var ExtSample = robot.Exteroception.Get(true);
        while (ExtSample == null) {
            ExtSample = robot.Exteroception.Get(true);
            Thread.Sleep(100);
        }
        string FrontSonar = IdentifyFrontSonar(ExtSample.Range);
        
        // Step 3: Begin closed loop control
        while (true) {
            
            // Step 4: get/show vision
            var ImageList = robot.Vision.Get(true);
            if (ImageList == null || ImageList.Samples.Count == 0) {
                continue;
            }
            ShowAllImages(ImageList);
            
            // Step 5: sample front-most ultrasound sensor
            ExtSample = robot.Exteroception.Get(true);
            if (ExtSample == null) {
                continue;
            }
            Range Sonar = null;
            foreach (var Sensor in ExtSample.Range) {
                if (Sensor.Source == FrontSonar) {
                    Sonar = Sensor;
                    break;
                }
            }
            
            // Step 6: construct motor message and implement decision-making logic
            var motorSample = new MotorSample();
            motorSample.Locomotion = new VelocityTarget();
            motorSample.Locomotion.TranslationalVelocity = new Vector3();
            motorSample.Locomotion.RotationalVelocity = new Vector3();
            
            if (Sonar.Data == -1) {
                Console.WriteLine($"Invalid Sonar Data: {Sonar.Data} meters");
                motorSample.Locomotion.RotationalVelocity.Z = 0.5f;
            } else if (Sonar.Data == 0) {
                Console.WriteLine($"No obstruction in range: {Sonar.Data} meters");
                motorSample.Locomotion.TranslationalVelocity.X = 0.2f;
            } else if ((Sonar.Min +0.5 < Sonar.Data) && (Sonar.Data <  Sonar.Min + 1.5)) {
                Console.WriteLine($"Obstruction approaching sensor minimum: {Sonar.Data} meters");
                motorSample.Locomotion.RotationalVelocity.Z = 0.5f;
            } else if (Sonar.Data <  Sonar.Min + 0.5) {
                Console.WriteLine($"Obstruction too close to maneuver, reverse: {Sonar.Data} meters");
                motorSample.Locomotion.RotationalVelocity.X = -0.2f;
            }else {
                Console.WriteLine($"Obstruction detected at safe range: {Sonar.Data} meters");
                motorSample.Locomotion.TranslationalVelocity.X = 0.2f;
            }

            // Step 7: Send the motor command
            robot.Motor.Set(motorSample);
        }

    }
    
    static void Cleanup() {
        Console.WriteLine("Closing down application");
        robot?.Disconnect();
        Bow.CloseClientInterface();
    }
    
}
