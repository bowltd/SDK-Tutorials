#include <bow_api.h>
#include <vector>
#include "display.h"

using namespace bow;

class myDisplay : public Display { 
public:
    bow_robot* Robot;

    myDisplay(bow_robot* robot){
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
    std::cout << bow_api::version() << std::endl;

    // Setup
    std::vector<std::string> strArray = {"vision", "motor"};
    std::unique_ptr<bow::common::Error> setup_result = std::make_unique<bow::common::Error>();
    auto* Robot= bow_api::quickConnect("ControllingJoints", strArray, false, nullptr, setup_result.get());
    if (!setup_result->success() || !Robot) {
        std::cout << setup_result->description() << std::endl;
        return -1;
    }

    // Populate list of display items (one per joint) from info in first proprioception sample received
    std::vector<DisplayInfo> jointList;// = new List<DisplayInfo>();
    while(true){
        try {
            auto prop_sample = Robot->proprioception->get(true);
            if (prop_sample.has_value()) {
                for (auto joint: prop_sample.value()->rawjoints()) {
                    if (joint.type() == bow::data::Joint::JointTypeEnum::Joint_JointTypeEnum_FIXED) {
                        continue;
                    }
                    jointList.push_back(DisplayInfo(joint.name(), joint.min(), joint.max(), joint.position()));
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
    myDisplay display = myDisplay(Robot);
    display.list = jointList;
    display.Run();

//    bow_api::stopEngine();
//    delete Robot;
//    return 0;
}