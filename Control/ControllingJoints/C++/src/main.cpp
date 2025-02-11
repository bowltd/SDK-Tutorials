#include <vector>
#include "display.h"
#include "bow_api.h"

using namespace bow;

class myDisplay : public Display {
public:
    bow::bow_robot* Robot;
    myDisplay(bow::bow_robot* robot){
        Robot = robot;
    }

    void SetCurrentJoint(){
        auto motorSample = new bow::data::MotorSample();
        motorSample->set_controlmode(bow::data::MotorSample_ControlModeEnum_USE_DIRECT_JOINTS);
        DisplayInfo joint = list[listIndex];
        motorSample->add_rawjoints();
        motorSample->mutable_rawjoints(0)->set_name(joint.Name);
        motorSample->mutable_rawjoints(0)->set_position(joint.Value);
        Robot->motor->set(motorSample);
    }
};

std::chrono::nanoseconds rateToTimerDelay(double hertz) {
    double delayInSeconds = 1 / hertz;
    double delayInNanoseconds = delayInSeconds * 1e9;
    return std::chrono::nanoseconds(static_cast<long>(delayInNanoseconds));
}

int main(int argc, char *argv[]) {

    std::vector<std::string> channels = {"proprioception", "motor"};                                                            // Chosen modalities
    std::unique_ptr<bow::common::Error> connect_result = std::make_unique<bow::common::Error>();
    bow::bow_robot* myRobot= bow_api::quickConnect(
        "BOW_Example",
        channels,
        false,
        nullptr,
        connect_result.get()
    );

    if (!connect_result->success() || !myRobot) {
        cout << connect_result->description() << endl;
        return -1;
    }

    // Populate list of display items (one per joint) from info in first proprioception sample received
    std::vector<DisplayInfo> jointList = {};
    while(true) {
        try{
            auto propSample = myRobot->proprioception->get(true);
            if (propSample.has_value()) {
                for (auto joint : propSample.value()->rawjoints()) {
                    if (joint.type() == bow::data::Joint::JointTypeEnum::Joint_JointTypeEnum_FIXED || joint.mimic()){
                        continue;
                    }
                    jointList.push_back(DisplayInfo(joint.name(),joint.min(),joint.max(),joint.position()));
                }
                break;
            }
        } catch (...) {
            std::cout<<"Exception occured"<<std::endl;
            auto delay = rateToTimerDelay(250);
        }
    }

    // Launch the display
    myDisplay display = myDisplay(myRobot);
    display.list = jointList;
    display.Run();

}
