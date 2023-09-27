# Protocol Documentation
<a name="top"></a>

## Table of Contents

- [bow_data.proto](#bow_data-proto)
    - [AudioSample](#bow-data-AudioSample)
    - [AudioSamples](#bow-data-AudioSamples)
    - [BlobSample](#bow-data-BlobSample)
    - [EndEffector](#bow-data-EndEffector)
    - [Float32Array](#bow-data-Float32Array)
    - [GPS](#bow-data-GPS)
    - [Gripper](#bow-data-Gripper)
    - [IMU](#bow-data-IMU)
    - [ImageSample](#bow-data-ImageSample)
    - [ImageSamples](#bow-data-ImageSamples)
    - [Int64Array](#bow-data-Int64Array)
    - [Locomotion](#bow-data-Locomotion)
    - [MotorArray](#bow-data-MotorArray)
    - [MotorSample](#bow-data-MotorSample)
    - [ProprioceptionSample](#bow-data-ProprioceptionSample)
    - [Quaternion](#bow-data-Quaternion)
    - [StringSample](#bow-data-StringSample)
    - [TactileSample](#bow-data-TactileSample)
    - [TactileSamples](#bow-data-TactileSamples)
    - [TimeSync](#bow-data-TimeSync)
    - [Transform](#bow-data-Transform)
    - [Vector3](#bow-data-Vector3)
  
    - [AngleTypeEnum](#bow-data-AngleTypeEnum)
    - [AudioSample.CompressionFormatEnum](#bow-data-AudioSample-CompressionFormatEnum)
    - [GripperModeEnum](#bow-data-GripperModeEnum)
    - [ImageSample.CompressionFormatEnum](#bow-data-ImageSample-CompressionFormatEnum)
    - [ImageSample.ImageTypeEnum](#bow-data-ImageSample-ImageTypeEnum)
    - [LocomotionModeEnum](#bow-data-LocomotionModeEnum)
    - [MotionGeneration](#bow-data-MotionGeneration)
    - [RelativeToEnum](#bow-data-RelativeToEnum)
    - [StereoDesignationEnum](#bow-data-StereoDesignationEnum)
    - [TactileSample.CompressionFormatEnum](#bow-data-TactileSample-CompressionFormatEnum)
    - [TactileSample.TactileTypeEnum](#bow-data-TactileSample-TactileTypeEnum)
    - [TorqueTypeEnum](#bow-data-TorqueTypeEnum)
  
- [Scalar Value Types](#scalar-value-types)



<a name="bow_data-proto"></a>
<p align="right"><a href="#top">Top</a></p>

## bow_data.proto



<a name="bow-data-AudioSample"></a>

### AudioSample
AudioSample contains a single packet of audio data from a single source


| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| Source | [string](#string) |  | Source indicates the origin of the audio data, such as a specific microphone. |
| Data | [bytes](#bytes) |  | Data contains the raw or compressed audio data. |
| Channels | [uint32](#uint32) |  | Channels specifies the number of audio channels. |
| SampleRate | [uint64](#uint64) |  | SampleRate indicates the number of samples per second. |
| NumSamples | [uint64](#uint64) |  | NumSamples provides the total number of audio samples in the Data field. |
| Compression | [AudioSample.CompressionFormatEnum](#bow-data-AudioSample-CompressionFormatEnum) |  | Compression specifies the audio compression format used. |
| Transform | [Transform](#bow-data-Transform) |  | Transform provides the spatial location of the audio source, if applicable. |
| Designation | [StereoDesignationEnum](#bow-data-StereoDesignationEnum) |  | Designation specifies whether the audio is intended for a specific channel in a stereo or multi-channel setup. |






<a name="bow-data-AudioSamples"></a>

### AudioSamples
AudioSamples contains multiple instances of audio data.


| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| Samples | [AudioSample](#bow-data-AudioSample) | repeated | Samples is an array of AudioSample messages, each containing a sample of audio data from different sources |






<a name="bow-data-BlobSample"></a>

### BlobSample
BlobSample provides flexible data type that can be used to define your own messages in a custom communication channel


| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| BytesArray | [bytes](#bytes) | repeated | BytesArray holds an array of bytes. |
| IntArray | [int64](#int64) | repeated | IntArray stores an array of integers. |
| FloatArray | [float](#float) | repeated | FloatArray contains an array of floating-point numbers. |
| String | [string](#string) |  | String stores a text string. |
| Transform | [Transform](#bow-data-Transform) |  | Transform specifies a spatial orientation and position in a 3D space. |






<a name="bow-data-EndEffector"></a>

### EndEffector
EndEffector defines an update to be sent to an articulated assembly, such as an arm or a leg


| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| Name | [string](#string) |  | Optional: Name of the end effector that this update is for. When not specified, position on array of EndEffectors is used to specify which command goes to which end effector |
| Transform | [Transform](#bow-data-Transform) |  | Optional: Transform specifies a target spatial orientation and position for the tip of the end effector relative to a provided reference frame. The required joint angles that result in the end effector going to the specified transform are calculated using built-in inverse kinematics. https://en.wikipedia.org/wiki/Inverse_kinematics This field is only used if UseTransform is set to true. |
| Enabled | [bool](#bool) |  | When Enabled is set to false, the update is not applied to the end effector. |
| Angles | [float](#float) | repeated | Angles contain the angular positions of each joint in the articulated assembly, ordered according to the robot&#39;s specification. This is to enable manual control of the robot&#39;s joints if needed but should be avoided under normal circumstances because code will not be robot agnostic in behaviour. WARNING: NOT ROBOT AGNOSTIC |
| EndEffectorTorque | [float](#float) | repeated | Optional: EndEffectorTorque lists the torque to be applied at each joint of an articulated assembly as part of the update. This is to enable manual control of the force applied by the robot but should be avoided under normal circumstances because code will not be robot agnostic in behaviour. This is adhered to when possible but not every robot allows this level of control WARNING: NOT ROBOT AGNOSTIC |
| AngleUnits | [AngleTypeEnum](#bow-data-AngleTypeEnum) |  | Optional: AngleUnits specifies the unit used for the joint angles if they are manually provided. |
| Gripper | [Gripper](#bow-data-Gripper) |  | Optional: Gripper specifies a command to be sent to a gripping mechanism connected to the tip of the end effector, if present. |
| MovementDurationMs | [float](#float) |  | Optional: MovementDurationMs defines the time allowed for the robot to move to its target transform or target joint angles in milliseconds. Ignored when robot does not support timing information on movements |
| ControlMode | [MotionGeneration](#bow-data-MotionGeneration) |  | Control mode specifies how the robot will be controlled. IK uses the Transform field together with Inverse Kinematics in order to calculate the required joint angles for a movement. Overwrites information in JointAngles and AngleUnits Custom uses the information in JointAngles and AngleUnits directly. WARNING: NOT ROBOT AGNOSTIC Other control modes specify additional functionality to be used alongside inverse kinematics such as self collision avoidance (Experimental) |






<a name="bow-data-Float32Array"></a>

### Float32Array
Float32Array is a container for an array of floating-point numbers.


| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| Data | [float](#float) | repeated | Data is an array of 32-bit floating-point numbers. |






<a name="bow-data-GPS"></a>

### GPS
GPS captures geographic positioning data.


| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| Latitude | [float](#float) |  | Latitude in decimal degrees |
| Longitude | [float](#float) |  | Longitude in decimal degrees |
| Elevation | [float](#float) |  | Elevation in meters above sea level |
| Time | [string](#string) |  | Timestamp of the GPS sample |






<a name="bow-data-Gripper"></a>

### Gripper
Gripper outlines the configuration of a hand-like gripper in terms of each finger&#39;s position.


| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| Thumb | [float](#float) |  | Thumb specifies the % closed for the thumb [0-1] or distance of thumb-tip to palm. |
| Index | [float](#float) |  | Index specifies the % closed for the index finger [0-1] or distance of index fingertip to palm. |
| Middle | [float](#float) |  | Middle specifies the % closed for the middle finger [0-1] or distance of middle fingertip to palm. |
| Ring | [float](#float) |  | Ring specifies the % closed for the ring finger [0-1] or distance of ring fingertip to palm. |
| Pinky | [float](#float) |  | Pinky specifies the % closed for the pinky finger [0-1] or distance of pinky fingertip to palm. |
| FingerAdduction | [float](#float) |  | FingerAddiction specifies the spread of the fingers as a % [0-1]. Not used in DISTANCE_IK mode. |
| ThumbOpposition | [float](#float) |  | ThumbOpposition specifies the opposition of the thumb as a % [0-1]. Not used in DISTANCE_IK mode. |
| CustomAngles | [float](#float) | repeated | CustomAngles allow for user-defined joint positions. WARNING: NOT ROBOT AGNOSTIC |
| JointNames | [string](#string) | repeated | JointNames names each joint corresponding to the CustomAngles. WARNING: NOT ROBOT AGNOSTIC |
| GripperMode | [GripperModeEnum](#bow-data-GripperModeEnum) |  | GripperMode indicates if custom angles should be applied. |






<a name="bow-data-IMU"></a>

### IMU
IMU (Inertial Measurement Unit) captures the sensor data needed to determine
an object&#39;s orientation, velocity, and gravitational forces.


| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| Gyro | [Vector3](#bow-data-Vector3) |  | Gyro represents angular velocity measured in radians per second along X, Y, and Z axes. |
| Acc | [Vector3](#bow-data-Vector3) |  | Acc signifies linear acceleration in meters per second squared along X, Y, and Z axes. |
| Transform | [Transform](#bow-data-Transform) |  | Transform provides a reference frame for the IMU data. |






<a name="bow-data-ImageSample"></a>

### ImageSample
ImageSample contains various information related to a single image or frame.


| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| Source | [string](#string) |  | Source identifies the origin of the image, such as a camera name or sensor ID. |
| Data | [bytes](#bytes) |  | Data holds the image information in bytes. |
| DataShape | [uint32](#uint32) | repeated | DataShape provides the dimensions of the Data array, useful for reshaping the byte array back into an image. |
| Compression | [ImageSample.CompressionFormatEnum](#bow-data-ImageSample-CompressionFormatEnum) |  | Compression indicates the algorithm used to compress the image. |
| ImageType | [ImageSample.ImageTypeEnum](#bow-data-ImageSample-ImageTypeEnum) |  | ImageType specifies the kind of image (RGB, Depth, etc.) |
| Transform | [Transform](#bow-data-Transform) |  | Transform represents the spatial positioning of the camera or sensor at the time the image was captured. |
| FrameNumber | [uint64](#uint64) |  | Optional: FrameNumber is a unique identifier for this frame. |
| Designation | [StereoDesignationEnum](#bow-data-StereoDesignationEnum) |  | Designation pertains to the role of the image in a stereo pair, if applicable. |
| HFOV | [float](#float) |  | Optional: HFOV is the horizontal field of view of the camera in degrees |
| VFOV | [float](#float) |  | Optional: VFOV is the vertical field of view of the camera in degrees. |
| NewDataFlag | [bool](#bool) |  | NewDataFlag indicates whether this sample contains new information since the last capture. |






<a name="bow-data-ImageSamples"></a>

### ImageSamples
ImageSamples holds an array of ImageSample objects, each capturing a specific image or frame at a given point in time and with a specific transform


| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| Samples | [ImageSample](#bow-data-ImageSample) | repeated | Samples is an array of ImageSample objects. |






<a name="bow-data-Int64Array"></a>

### Int64Array
Int64Array is a container for an array of 64-bit integers.


| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| Data | [int64](#int64) | repeated | Data is an array of 64-bit integers. |






<a name="bow-data-Locomotion"></a>

### Locomotion
Locomotion encapsulates information regarding the robot&#39;s movement and positioning.


| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| Position | [Vector3](#bow-data-Vector3) |  | Position defines the robot&#39;s spatial coordinates in Cartesian form. |
| Rotation | [Vector3](#bow-data-Vector3) |  | Rotation outlines the robot&#39;s orientation, described by a Vector3 of Euler angles. |
| LocomotionMode | [LocomotionModeEnum](#bow-data-LocomotionModeEnum) |  | LocomotionMode defines whether the robot&#39;s locomotion should be position-based or velocity-based. |
| RotationUnits | [AngleTypeEnum](#bow-data-AngleTypeEnum) |  | RotationUnits defines the units of the rotation vector. |






<a name="bow-data-MotorArray"></a>

### MotorArray
MotorArray is a collection of MotorSamples, each accompanied by a timestamp, providing a time-ordered set of robot states. This is the data type for a recording.


| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| Samples | [MotorSample](#bow-data-MotorSample) | repeated | Samples contains an array of MotorSamples, each capturing a unique state of the robot&#39;s motors. |
| Tstamp | [int64](#int64) | repeated | Tstamp holds an array of timestamps in milliseconds, each corresponding to a MotorSample in the Samples array. |






<a name="bow-data-MotorSample"></a>

### MotorSample
MotorSample combines all the parts of a motor update into a single message.


| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| Head | [Vector3](#bow-data-Vector3) |  | Head defines the orientation of the robot&#39;s head, if applicable in euler angles. X is yaw (look right when positive), Y is pitch (look up when positive) and Z is roll (lean head right when positive) |
| Locomotion | [Locomotion](#bow-data-Locomotion) |  | Locomotion provides an update for how the robot should move within its environment |
| EndEffectors | [EndEffector](#bow-data-EndEffector) | repeated | EndEffectors is an array that holds an array of updates for end effectors, such as arms or legs. |
| OperatingHeight | [float](#float) |  | OperatingHeight defines the robot&#39;s height in metres from a specified base, useful for robots with adjustable height. In the future, operating height and head will be considered as an end effector to generalise further |
| RecordFlag | [bool](#bool) |  | RecordFlag indicates whether the current motor sample should be recorded. |
| PlaybackFlag | [bool](#bool) |  | PlaybackFlag signals whether a previously recorded action should be replayed. |
| PlaybackActionName | [string](#string) |  | PlaybackActionName specifies the name of the action to be replayed, assuming PlaybackFlag is true. |






<a name="bow-data-ProprioceptionSample"></a>

### ProprioceptionSample
ProprioceptionSample contains all the information regarding the kinematic state of the robot and relating to the robot&#39;s environment


| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| JointNames | [string](#string) | repeated | JointNames lists the names of all joints in the robot, ordered according to the robot&#39;s specification. |
| JointAngles | [float](#float) | repeated | JointAngles holds the angular positions of each joint, ordered to correspond with JointNames. |
| AngleUnits | [AngleTypeEnum](#bow-data-AngleTypeEnum) |  | AngleUnits specifies the unit of measurement for the joint angles |
| JointVelocities | [float](#float) | repeated | Optional: JointVelocities contains the angular velocities of each joint ordered to align with JointNames. |
| JointTorques | [float](#float) | repeated | Optional: JointTorques lists the torques applied at each joint ordered to align with JointNames. |
| TorqueUnits | [TorqueTypeEnum](#bow-data-TorqueTypeEnum) |  | Optional: TorqueUnits indicates the unit of measurement for the joint torques. |
| SpatialOrientationEnabled | [bool](#bool) |  | Optional: SpatialOrientationEnabled flags whether spatial orientation data is included or not. |
| SpatialUnits | [AngleTypeEnum](#bow-data-AngleTypeEnum) |  | Optional: SpatialUnits indicates the unit of measurement for spatial resolution. |
| SpatialResolution | [float](#float) |  | Optional: SpatialResolution specifies the granularity of the spatial orientation data. |
| SpatialOrientation | [float](#float) | repeated | Optional: SpatialOrientation provides the distance to an obstacle within an angular segment of size defined by spatial resolution. |
| Imu | [IMU](#bow-data-IMU) | repeated | Optional: Imu provides the 3D acceleration, orientation, and gravitational forces experienced at different positions on a robot&#39;s body |
| Gps | [GPS](#bow-data-GPS) |  | Optional: Gps provides the global position of the robot, if available |






<a name="bow-data-Quaternion"></a>

### Quaternion
Quaternion contains the components of a normalised quaternion that can be used to describe a rotation.


| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| QuatX | [float](#float) |  | X component of the normalised quaternion |
| QuatY | [float](#float) |  | Y component of the normalised quaternion |
| QuatZ | [float](#float) |  | Z component of the normalised quaternion |
| QuatW | [float](#float) |  | W component of the normalised quaternion |






<a name="bow-data-StringSample"></a>

### StringSample
StringSample encapsulates a single string-based data sample.


| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| Data | [string](#string) |  | Data contains the string value of the sample. |






<a name="bow-data-TactileSample"></a>

### TactileSample
TactileSample captures data about a single tactile interaction or sensor reading.


| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| Source | [string](#string) |  | Source identifies the tactile sensor that provided the data. |
| LocationTag | [RelativeToEnum](#bow-data-RelativeToEnum) |  | LocationTag specifies the location on the robot where the sensor is mounted. |
| Data | [bytes](#bytes) |  | Data contains the raw tactile data. |
| DataShape | [uint32](#uint32) | repeated | DataShape provides the dimensions of the tactile data array. |
| TactileType | [TactileSample.TactileTypeEnum](#bow-data-TactileSample-TactileTypeEnum) |  | TactileType specifies the type of tactile interaction being captured. |
| Compression | [TactileSample.CompressionFormatEnum](#bow-data-TactileSample-CompressionFormatEnum) |  | Compression indicates the tactile data compression format. |
| ClassifiedTexture | [string](#string) |  | ClassifiedTexture offers a qualitative description of a detected texture. |
| FloatData | [float](#float) | repeated | FloatData can contain additional floating-point data related to the tactile sample. |
| Transform | [Transform](#bow-data-Transform) |  | Transform gives the spatial orientation and position of the sensor |
| NewDataFlag | [bool](#bool) |  | NewDataFlag indicates whether the data sample is new or not. |






<a name="bow-data-TactileSamples"></a>

### TactileSamples
TactileSamples is a container for multiple instances of tactile data samples.


| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| Samples | [TactileSample](#bow-data-TactileSample) | repeated | Samples is an array of TactileSample messages, each providing detailed information about different types of tactile experiences. |






<a name="bow-data-TimeSync"></a>

### TimeSync
TimeSync enables the synchronization of clocks between devices.


| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| TOrigin_0 | [int64](#int64) |  | TOrigin_0 is the time on the originating device when the sync request is first made |
| TReceiver | [int64](#int64) |  | TReceiver is the time on the receiving device when the sync request is received |
| TOrigin_1 | [int64](#int64) |  | TOrigin_1 is the time on the originating device when the sync response is received |
| ReturnTrip | [bool](#bool) |  | ReturnTrip signifies if the synchronization request has made a round trip |






<a name="bow-data-Transform"></a>

### Transform
Transform captures a spatial point and orientation in Cartesian coordinates.


| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| Position | [Vector3](#bow-data-Vector3) |  | Position utilises a Vector3 to define distances in metres from a designated reference point. X is positive to the right, Y is positive upwards, Z is positive forwards. |
| Quaternion | [Quaternion](#bow-data-Quaternion) |  | Quaternion contains a normalised quaternion to define the object&#39;s rotation. |
| EulerAngles | [Vector3](#bow-data-Vector3) |  | EulerAngles use a Vector3 to define rotation through specific angles, in units designated by AngleUnits. |
| AngleUnits | [AngleTypeEnum](#bow-data-AngleTypeEnum) |  | AngleUnits outlines the unit of measurement used in EulerAngles. |
| LocationTag | [RelativeToEnum](#bow-data-RelativeToEnum) |  | Optional: LocationTag identifies the origin point to which the transform is relative. |
| Name | [string](#string) |  | Name assigns a distinct identifier for the Transform. |






<a name="bow-data-Vector3"></a>

### Vector3
Vector3 contains three components expected for a vector in 3D cartesian space


| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| X | [float](#float) |  | X component of the vector |
| Y | [float](#float) |  | Y component of the vector |
| Z | [float](#float) |  | Z component of the vector |





 


<a name="bow-data-AngleTypeEnum"></a>

### AngleTypeEnum
AngleTypeEnum designates the measurement units for angles.

| Name | Number | Description |
| ---- | ------ | ----------- |
| UNKNOWN_ANGLE_UNITS | 0 | Default: Robot uses its default angle unit when not specified. |
| RADIANS | 1 | Angles are measured in radians. |
| DEGREES | 2 | Angles are measured in degrees. |



<a name="bow-data-AudioSample-CompressionFormatEnum"></a>

### AudioSample.CompressionFormatEnum
CompressionFormatEnum lists available audio compression formats.

| Name | Number | Description |
| ---- | ------ | ----------- |
| RAW | 0 | Default: No compression |
| SPEEX | 1 | Compressed in Speex formats |



<a name="bow-data-GripperModeEnum"></a>

### GripperModeEnum
GripperModeEnum specifies the type of control to be used by the gripper

| Name | Number | Description |
| ---- | ------ | ----------- |
| PERCENTAGE | 0 | Defult: Defines the use of a custom array of angles to be applied to a matching array of joint names to control the movement directly |
| DIRECT | 1 | Defines that the information stored for each digit is a float range of 0 (fully open) to 1 (fully closed) |
| DISTANCE_IK | 2 | Defines that the information stored for each digit is a distance from fingertip to palm. This information is used by IK to create a robot agnostic solution that can generate a solution independent of gripper joint configuration |



<a name="bow-data-ImageSample-CompressionFormatEnum"></a>

### ImageSample.CompressionFormatEnum
CompressionFormatEnum defines the compression currently in use for this image

| Name | Number | Description |
| ---- | ------ | ----------- |
| H264 | 0 | h264 compression |
| VP8 | 1 | Default: vp8 compression |
| VP9 | 2 | vp9 compression |
| JPG | 3 | jpeg compression |
| RAW | 4 | no compression |
| H265 | 5 | h265 compression |



<a name="bow-data-ImageSample-ImageTypeEnum"></a>

### ImageSample.ImageTypeEnum
ImageTypeEnum defines the type of image or sensory data.

| Name | Number | Description |
| ---- | ------ | ----------- |
| RGB | 0 | Default: Standard red-green-blue image in YUV422 format |
| DEPTH | 1 | Depth map |
| STEREO | 2 | Stereoscopic image |
| INFRARED | 3 | Infrared image |



<a name="bow-data-LocomotionModeEnum"></a>

### LocomotionModeEnum
LocomotionModeEnum categorises the robot&#39;s movement control methods.

| Name | Number | Description |
| ---- | ------ | ----------- |
| UNKNOWN_LOCOMOTION_MODE | 0 | Default: Robot uses its inherent default mode, either based on position or velocity. |
| POSITION_MODE | 1 | Defines the robot&#39;s target distance, specified in metres for translation and degrees / radians for rotation. |
| VELOCITY_MODE | 2 | Commands define the robot&#39;s target speed, specified in metres per second for translation or degrees per second / radians per second for rotation. |



<a name="bow-data-MotionGeneration"></a>

### MotionGeneration
GripperModeEnum specifies the type of control to be used by the gripper

| Name | Number | Description |
| ---- | ------ | ----------- |
| IK | 0 | Default: Defines the use of IK to generate robot movement |
| CUSTOM | 1 | Defines the use of custom angles to set robot joint angles |
| IK_WITH_SELF_COLLISION_AVOIDANCE | 2 | Experimental: Defines the use of self collision avoidance when generating a robot&#39;s movement. (Experimental) |



<a name="bow-data-RelativeToEnum"></a>

### RelativeToEnum
RelativeToEnum marks specific points on the robot for spatial reference.

| Name | Number | Description |
| ---- | ------ | ----------- |
| BASE | 0 | Default: Base indicates the robot&#39;s contact point with the floor. |
| HEAD | 1 | Head marks the robot&#39;s primary vision point, often where the main camera is located. |
| END_EFFECTOR | 2 | End_Effector identifies the terminal point of an articulated assembly. |
| END_EFFECTOR_LEFT | 3 | Identical to End_Effector but specifies the main articulated assembly on the left side of the robot. |
| END_EFFECTOR_RIGHT | 4 | Identical to End_Effector but specifies the main articulated assembly on the right side of the robot. |
| TORSO | 5 | Torso marks the robot&#39;s centre of mass. |



<a name="bow-data-StereoDesignationEnum"></a>

### StereoDesignationEnum
StereoDesignationEnum identifies the camera&#39;s role as part of a stereo pair or a microphone&#39;s role as part of a binaural pair. https://en.wikipedia.org/wiki/Stereo_camera

| Name | Number | Description |
| ---- | ------ | ----------- |
| NONE | 0 | Default: Camera functions independently, not as part of a stereo pair. |
| LEFT | 1 | Camera operates as the left component in a stereo pair. |
| RIGHT | 2 | Camera operates as the right component in a stereo pair. |



<a name="bow-data-TactileSample-CompressionFormatEnum"></a>

### TactileSample.CompressionFormatEnum
CompressionFormatEnum lists available formats for tactile data compression.

| Name | Number | Description |
| ---- | ------ | ----------- |
| RAW | 0 | Default: No compression |



<a name="bow-data-TactileSample-TactileTypeEnum"></a>

### TactileSample.TactileTypeEnum
TactileTypeEnum enumerates the types of tactile interactions that can be captured.

| Name | Number | Description |
| ---- | ------ | ----------- |
| UNDEFINED | 0 | Default: Undefined tactile type |
| PRESSURE | 1 | PRESSURE is a 1D float data type of range [0,1] with 1 item per sensor |
| VIBRATION | 2 | VIBRATION is a 1D float data type of range [0,1] with 1 item per sensor |
| TEXTURE | 3 | TEXTURE represents a classified texture provided as a string |
| FORCE_FEEDBACK | 4 | FORCE_FEEDBACK is a 1D float data type of range [0,1] with 1 item per sensor |
| TRIAXIAL | 5 | TRIAXIAL is a 3D float data type of range [0,1] with 3 items per sensor |



<a name="bow-data-TorqueTypeEnum"></a>

### TorqueTypeEnum
TorqueTypeEnum outlines the measurement units for torque.

| Name | Number | Description |
| ---- | ------ | ----------- |
| UNKNOWN_TORQUE_UNITS | 0 | Default: Robot uses its default torque unit when not specified. |
| CURRENT | 1 | Torque is quantified as electrical current in Amperes. This is not a direct measurement of torque but a good relative measure when one is not available |
| NEWTON_METRES | 2 | Torque is quantified in newton metres. |


 

 

 



## Scalar Value Types

| .proto Type | Notes | C++ | Java | Python | Go | C# | PHP | Ruby |
| ----------- | ----- | --- | ---- | ------ | -- | -- | --- | ---- |
| <a name="double" /> double |  | double | double | float | float64 | double | float | Float |
| <a name="float" /> float |  | float | float | float | float32 | float | float | Float |
| <a name="int32" /> int32 | Uses variable-length encoding. Inefficient for encoding negative numbers – if your field is likely to have negative values, use sint32 instead. | int32 | int | int | int32 | int | integer | Bignum or Fixnum (as required) |
| <a name="int64" /> int64 | Uses variable-length encoding. Inefficient for encoding negative numbers – if your field is likely to have negative values, use sint64 instead. | int64 | long | int/long | int64 | long | integer/string | Bignum |
| <a name="uint32" /> uint32 | Uses variable-length encoding. | uint32 | int | int/long | uint32 | uint | integer | Bignum or Fixnum (as required) |
| <a name="uint64" /> uint64 | Uses variable-length encoding. | uint64 | long | int/long | uint64 | ulong | integer/string | Bignum or Fixnum (as required) |
| <a name="sint32" /> sint32 | Uses variable-length encoding. Signed int value. These more efficiently encode negative numbers than regular int32s. | int32 | int | int | int32 | int | integer | Bignum or Fixnum (as required) |
| <a name="sint64" /> sint64 | Uses variable-length encoding. Signed int value. These more efficiently encode negative numbers than regular int64s. | int64 | long | int/long | int64 | long | integer/string | Bignum |
| <a name="fixed32" /> fixed32 | Always four bytes. More efficient than uint32 if values are often greater than 2^28. | uint32 | int | int | uint32 | uint | integer | Bignum or Fixnum (as required) |
| <a name="fixed64" /> fixed64 | Always eight bytes. More efficient than uint64 if values are often greater than 2^56. | uint64 | long | int/long | uint64 | ulong | integer/string | Bignum |
| <a name="sfixed32" /> sfixed32 | Always four bytes. | int32 | int | int | int32 | int | integer | Bignum or Fixnum (as required) |
| <a name="sfixed64" /> sfixed64 | Always eight bytes. | int64 | long | int/long | int64 | long | integer/string | Bignum |
| <a name="bool" /> bool |  | bool | boolean | boolean | bool | bool | boolean | TrueClass/FalseClass |
| <a name="string" /> string | A string must always contain UTF-8 encoded or 7-bit ASCII text. | string | String | str/unicode | string | string | string | String (UTF-8) |
| <a name="bytes" /> bytes | May contain any arbitrary sequence of bytes. | string | ByteString | str | []byte | ByteString | string | String (ASCII-8BIT) |

