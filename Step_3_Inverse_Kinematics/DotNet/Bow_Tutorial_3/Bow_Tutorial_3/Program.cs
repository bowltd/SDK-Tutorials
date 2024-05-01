﻿using BOW.Common;
using BOW.Data;
using BOW.SDK.Core;
using BOW.Structs;

class Program
{
    static void Main(string[] args)
    {
        //Sense (Hard coded)
        
        var hoverDistance = 0.20f;
        var touchDistance = 0.15f;
        var startObjective = new System.Numerics.Vector3(0.02f, -0.18f, 0f);
        
        List<System.Numerics.Vector3> positionObjectives = new List<System.Numerics.Vector3>();
        
        //Move to straight up
        positionObjectives.Add(new System.Numerics.Vector3(0, 0,1));
        //Move to max and min X
        positionObjectives.Add(new System.Numerics.Vector3(0.3f, 0,0.2f));
        positionObjectives.Add(new System.Numerics.Vector3(0.3f, 0,0.2f));
        //Move to max and min Y
        positionObjectives.Add(new System.Numerics.Vector3(0, 0.3f,0.2f));
        positionObjectives.Add(new System.Numerics.Vector3(0, -0.3f,0.2f));
        
        //Move to position staying above bolt
        startObjective.Z = hoverDistance;
        positionObjectives.Add(startObjective);
        
        // Touch bolt
        startObjective.Z = touchDistance;
        positionObjectives.Add(startObjective);
        
        // Move back to hover
        startObjective.Z = hoverDistance;
        positionObjectives.Add(startObjective);
        
        //Back to neutral position
        positionObjectives.Add(new System.Numerics.Vector3(0, 0,1));
        
        // Connect to Robot
        Console.WriteLine(BowClient.Version());

        List<string> modalities = new List<string>() { "proprioception", "motor" };
        Error quickConnectError;
        var myRobot = BowClient.QuickConnect("Tutorial 3 Dotnet", modalities, out quickConnectError);
        
        if (myRobot == null)
        {
            Console.WriteLine($"Failed to set up robot: {quickConnectError.Description}");
        }

        var listOfEffectors = new List<string>();
        // We will wait until we have successfully received a proprioception message in order to get a list of effectors
        while (true)
        {
            try
            {
                var getMsg = myRobot.GetModality("proprioception", true);
                if (getMsg.Error.Success)
                {
                    if (getMsg.Data is ProprioceptionSample propSample)
                    {
                        if (propSample.Effectors.Count == 0)
                        {
                            continue;
                        }
                        
                        foreach (var eff in propSample.Effectors)
                        {
                            //only get controllable effectors
                            if (eff.IsControllable)
                            {
                                listOfEffectors.Add(eff.EffectorLinkName);
                            }
                        }
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
        
        //Decide
        var selectedEffector = "";
        while (true)
        {
            Console.WriteLine("Please select an option:");
            for (int i = 0; i < listOfEffectors.Count; i++)
            {
                Console.WriteLine($"{i + 1}. {listOfEffectors[i]}");
            }
        
            // Get user input
            Console.Write("Enter your choice (number): ");
            int userInput = Convert.ToInt32(Console.ReadLine());
        
            // Check if the input is valid
            
            if (userInput > 0 && userInput <= listOfEffectors.Count)
            {
                selectedEffector = listOfEffectors[userInput - 1];
                Console.WriteLine($"You selected: {selectedEffector}");
                break;
            }
            
            Console.WriteLine("Invalid choice. Please run the program again and select a valid number.");
        }
        
        //Act
        foreach (var obj in positionObjectives)
        { 
            Console.WriteLine($"Sending objective: {obj.X}, {obj.Y}, {obj.Z}");
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
                        Transform = new Transform
                        {
                            Position = new Vector3
                            {
                                X = obj.X,
                                Y = obj.Y,
                                Z = obj.Z
                            },
                            //Try experimenting with setting different target orientations for the movement
                            // EulerAngles = new Vector3
                            // {
                            //     X = -90,
                            //     Y = 0,
                            //     Z = 0
                            // }
                        },
                        OptimiserSettings = new IKOptimiser
                        {
                            Preset = IKOptimiser.Types.OptimiserPreset.HighAccuracy,
                        },
                    },
                    Enabled = true,
                });
                
                var setError = myRobot.SetModality("motor", (int)DataMessage.Types.DataType.Motor, mSamp);
                if (!setError.Success)
                {
                    Console.WriteLine($"Error calling setModality motor: {setError.Description}");
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine("Exception occurred: " + ex.Message);
                break;
            }
            Thread.Sleep(2000);   
        }
    }
}
