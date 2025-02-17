#include <iostream>
#include <string>
#include <memory>
#include <chrono>
#include <thread>
#include "bow_api.h"
using namespace bow;

void SendObjective(bow_robot *myRobot, std::string selectedEffector, float x, float y, float z) {
    std::cout << "Sending objective: " << x << " ," << y << ", " << z << std::endl;
    try {
        auto motor = new bow::data::MotorSample();
        motor->mutable_iksettings()->set_preset(bow::data::IKOptimiser_OptimiserPreset_HIGH_ACCURACY);
        motor->mutable_iksettings()->mutable_globalobjectiveweights()->set_displacement(1.0);

        motor->mutable_objectives()->Clear();
        auto objectiveCommand = motor->add_objectives();

        objectiveCommand->set_targeteffector(selectedEffector);
        objectiveCommand->set_controlmode(bow::data::POSITION_CONTROLLER);
        objectiveCommand->mutable_posetarget()->mutable_localobjectiveweights()->set_position(1.0);
        objectiveCommand->mutable_posetarget()->mutable_localobjectiveweights()->set_orientation(0.0);
        objectiveCommand->mutable_posetarget()->set_action(bow::data::GOTO);
        objectiveCommand->mutable_posetarget()->set_targettype(bow::data::PoseTarget_TargetTypeEnum_TRANSFORM);
        objectiveCommand->mutable_posetarget()->set_targetscheduletype(
            bow::data::PoseTarget_SchedulerEnum_INSTANTANEOUS);
        objectiveCommand->mutable_posetarget()->mutable_transform()->mutable_position()->set_x(x);
        objectiveCommand->mutable_posetarget()->mutable_transform()->mutable_position()->set_y(y);
        objectiveCommand->mutable_posetarget()->mutable_transform()->mutable_position()->set_z(z);
        objectiveCommand->set_enabled(true);

        bow::common::Error *setResult = myRobot->motor->set(motor);
        if (!setResult->success()) {
            std::cout << "Error calling motor set: " << setResult->description() << std::endl;
        }
    } catch (...) {
        std::cout << "Exception occured" << std::endl;
        return;
    }
}


std::chrono::nanoseconds rateToTimerDelay(double hertz) {
    double delayInSeconds = 1 / hertz;
    double delayInNanoseconds = delayInSeconds * 1e9;
    return std::chrono::nanoseconds(static_cast<long>(delayInNanoseconds));
}


int main(int argc, char *argv[]) {
    std::vector<std::string> channels = {"proprioception", "motor"}; // Chosen modalities
    std::unique_ptr<bow::common::Error> connect_result = std::make_unique<bow::common::Error>();
    bow::bow_robot *myRobot = bow_api::quickConnect(
        "BOW_Example",
        channels,
        false,
        nullptr,
        connect_result.get()
    );

    if (!connect_result->success() || !myRobot) {
        std::cout << connect_result->description() << std::endl;
        return -1;
    }


    std::vector<std::string> listOfParts(0);
    std::vector<std::string> listOfEffectors(0);
    std::vector<float> listOfReach(0);
    std::vector<float> listOfUpDown(0);


    // Populate list of display items (one per joint) from info in first proprioception sample received
    while (true) {
        try {
            auto propSample = myRobot->proprioception->get(true);
            if (propSample.has_value()) {
                if (propSample.value()->effectors().size() == 0) {
                    continue;
                }

                for (auto part: propSample.value()->parts()) {
                    for (auto eff: part.effectors()) {
                        if (!eff.iscontrollable()) {
                            continue;
                        }

                        listOfParts.push_back(part.name());
                        listOfEffectors.push_back(eff.effectorlinkname());
                        listOfReach.push_back(eff.reach());
                        if (eff.endtransform().position().z() > eff.roottransform().position().z()) {
                            //Effector is by default higher than root hence height offset should be positive
                            listOfUpDown.push_back(1.0);
                        } else {
                            //Effector is by default lower than effector root hence height offset should be negative
                            listOfUpDown.push_back(-1.0);
                        }
                    }
                }
                break;
            }
        } catch (...) {
            std::cout << "Exception occured" << std::endl;
            auto delay = rateToTimerDelay(250);
        }
    }


    //Decide
    std::string selectedEffector;
    float selectedReach = 0.0;
    float selectedUpDown = 1.0;
    while (true) {
        std::cout << "Please select an option:" << std::endl;
        for (int i = 0; i < listOfEffectors.size(); i++) {
            std::cout << i + 1 << ". " << listOfEffectors[i] << " of type " << listOfParts[i] << " with reach of " <<
                    listOfReach[i] << " and default direction " << listOfUpDown[i] << std::endl;
        }

        // Get user input
        std::cout << "Enter your choice (number): " << std::endl;

        std::string input;
        std::getline(std::cin, input);
        int userInput = stoi(input);

        // Check if the input is valid

        if (userInput > 0 && userInput <= listOfEffectors.size()) {
            selectedEffector = listOfEffectors[userInput - 1];
            selectedReach = listOfReach[userInput - 1];
            selectedUpDown = listOfUpDown[userInput - 1];
            std::cout << "You selected: " << selectedEffector << std::endl;
            break;
        }
        std::cout << "Invalid choice. Please run the program again and select a valid number." << std::endl;
    }

    //Act
    double circleRadius = selectedReach * 0.25; // Radius of the circle
    double circleHeight = selectedReach * 0.3; // Z-axis height of the circle
    double wobbleAmplitude = selectedReach * 0.05f;
    double wobbleFreqMultiplier = 6.0;
    double stepSize = 0.05; // Step size in radians

    double x = 0, y = 0, z = 0;
    while (true) {
        for (double angle = 0; angle <= 2 * M_PI; angle += stepSize) {
            x = circleRadius * cos(angle);
            y = circleRadius * sin(angle);
            z = selectedUpDown * (circleHeight + (wobbleAmplitude * cos(angle * wobbleFreqMultiplier)));
            SendObjective(myRobot, selectedEffector, x, y, z);
            sleep(0.2);
            std::this_thread::sleep_for(std::chrono::milliseconds(200));
        }
    }


    std::cout << "Closing down application" << std::endl;
    myRobot->disconnect();
    bow_api::stopEngine();
}
