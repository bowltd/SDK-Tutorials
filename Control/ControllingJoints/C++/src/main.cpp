#include <bow_sdk.h>
#include <vector>
#include "display.h"

class myDisplay : public Display { 
public:
    bow_sdk::bow_robot Robot;

    myDisplay(bow_sdk::bow_robot robot){
        Robot = robot;
    }

    void SetCurrentJoint(){
        auto motorSample = new bow::data::MotorSample();
        motorSample->set_controlmode(bow::data::MotorSample_ControlModeEnum_USE_DIRECT_JOINTS);
        DisplayInfo joint = list[listIndex];
        motorSample->add_rawjoints();
        motorSample->mutable_rawjoints(0)->set_name(joint.Name); 
        motorSample->mutable_rawjoints(0)->set_position(joint.Value);
        Robot.SetModality("motor", bow::structs::DataMessage_DataType_MOTOR, motorSample);
    }
};

std::chrono::nanoseconds rateToTimerDelay(double hertz) {
    double delayInSeconds = 1 / hertz;
    double delayInNanoseconds = delayInSeconds * 1e9;
    return std::chrono::nanoseconds(static_cast<long>(delayInNanoseconds));
}

int main(int argc, char *argv[]) {

    auto* myRobot = new bow_sdk::bow_robot();
    std::vector<std::string> strArray = {"proprioception", "motor"};                                                            // Chosen modalities
    bow::common::Error* setup_result = bow_sdk::client_sdk::QuickConnect(myRobot, "BOW Tutorial", strArray, true);      // QuickConnect
    if (!setup_result->success()) {
        cout << setup_result->description() << endl;
        delete myRobot; // Free allocated memory
        return -1;
    }

    // Populate list of display items (one per joint) from info in first proprioception sample received
    std::vector<DisplayInfo> jointList;// = new List<DisplayInfo>();
    while(true){
        try {
            auto* getMsg = myRobot->GetModality("proprioception", true);
            if (getMsg->error().success()) {
                auto prop_sample = new bow::data::ProprioceptionSample();
                prop_sample->MergeFromString(getMsg->mutable_sample()->data());
                //std::cout<<prop_sample->rawjoints().size()<<std::endl;


                for (auto joint : prop_sample->rawjoints()) {
                    if (joint.type() == bow::data::Joint::JointTypeEnum::Joint_JointTypeEnum_FIXED){
                        continue;
                    }
                    jointList.push_back(DisplayInfo(joint.name(),joint.min(),joint.max(),joint.position()));
                    }
                    break;
            }

        }
        catch (...) {
            std::cout<<"Exception occured"<<std::endl;
            auto delay = rateToTimerDelay(250);
        }
    }

    // Launch the display
    myDisplay display = myDisplay(*myRobot);
    display.list = jointList;
    display.Run();    
}