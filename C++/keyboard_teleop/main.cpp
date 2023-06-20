#include <iostream>
#include <unistd.h>
#include <csignal> // for signal handling
#include <chrono>
#include <thread>
#include <map>
#include <string>

#include <QApplication>
#include <QMainWindow>
#include <QDebug>
#include <QKeyEvent>

#include <opencv2/imgcodecs.hpp>
#include <opencv2/highgui.hpp>
#include <opencv2/core.hpp>
#include <opencv2/imgproc.hpp>

#include "animus_structs.pb.h"
#include "bow_sdk.h"


using namespace bow;
using namespace animus;
using namespace cv;
using namespace std;

std::vector<std::thread> threads;
std::atomic<bool> shutdownFlag(false);
std::map<int, std::string> keyMappings;
std::map<std::string, bool> movements;
std::vector<float> angles = {-1.1, 1.47, 2.71, 1.71, -1.57, 1.39, 0};
int angleIdx = 0;

std::chrono::nanoseconds rateToTimerDelay(double hertz) {
    double delayInSeconds = 1 / hertz;
    double delayInNanoseconds = delayInSeconds * 1e9;
    return std::chrono::nanoseconds(static_cast<long>(delayInNanoseconds));
}

void visionThread(double rate, bow_robot* Robot)
{
    auto delay = rateToTimerDelay(rate);
    string window_name = "Robot view";
    cv::namedWindow("Image", cv::WINDOW_NORMAL);
    auto receivedRGB = new Mat();

    while (!shutdownFlag.load()) {
        std::this_thread::sleep_for(delay);

        auto* sample = Robot->GetModality("vision", true);
        auto image_samples = new animus::data::ImageSamples();
        image_samples->MergeFromString(sample->mutable_sample()->data());
        try {
            if (image_samples->samples_size() > 0) {
                auto s = image_samples->samples(0);
//                if (s.newdataflag()) {
                    auto receivedYuv = new cv::Mat(s.data_shape(1)*3/2, s.data_shape(0), CV_8UC1, const_cast<char*>(s.data().data()));
                    cv::cvtColor(*receivedYuv, *receivedRGB, cv::COLOR_YUV2RGB_IYUV);
                    cv::imshow("Image", *receivedRGB);
                    cv::waitKey(1);
//                }
            }
        } catch (const std::exception& ex) {
            // Catch and handle the exception
            std::cerr << "Exception caught: " << ex.what() << std::endl;
        }
    }

    destroyWindow(window_name);
}

void speechThread(double rate, bow_robot* Robot)
{
    auto delay = rateToTimerDelay(rate);

    while (!shutdownFlag.load()) {
        std::this_thread::sleep_for(delay);
        auto speech = new animus::data::StringSample();
        speech->set_data("BOW SDK is the best");
        Robot->SetModality("speech", animus::data::DataMessage_DataType_STRING, speech);
    }
}

void motorThread(double rate, bow_robot *Robot) {
    auto delay = rateToTimerDelay(rate);
    bool latch = false;
    bool latch_increase = false;
    bool latch_decrease = false;

    while (!shutdownFlag.load()) {
        std::this_thread::sleep_for(delay);

        auto motor = new animus::data::MotorSample();
        motor->mutable_locomotion()->set_locomotionmode(animus::data::VELOCITY_MODE);

        if (movements.at("MoveForward")) {
//            std::cout << "Move forward" << std::endl;
            motor->mutable_locomotion()->mutable_position()->set_x(1);
        } else if (movements.at("MoveBack")) {
//            std::cout << "Move back" << std::endl;
            motor->mutable_locomotion()->mutable_position()->set_x(-1);
        } else {
            motor->mutable_locomotion()->mutable_position()->set_x(0);
        }

        if (movements.at("MoveLeft")) {
//            std::cout << "Move left" << std::endl;
            motor->mutable_locomotion()->mutable_position()->set_y(1);
        } else if (movements.at("MoveRight")) {
//            std::cout << "Move right" << std::endl;
            motor->mutable_locomotion()->mutable_position()->set_y(-1);
        } else {
            motor->mutable_locomotion()->mutable_position()->set_y(0);
        }

        if (movements.at("MoveUp")) {
//            std::cout << "Move up" << std::endl;
            motor->mutable_locomotion()->mutable_position()->set_z(1);
        } else if (movements.at("MoveDown")) {
//            std::cout << "Move down" << std::endl;
            motor->mutable_locomotion()->mutable_position()->set_z(-1);
        } else {
            motor->mutable_locomotion()->mutable_position()->set_z(0);
        }

        if (movements.at("RotateLeft")) {
//            std::cout << "Rotate left" << std::endl;
            motor->mutable_locomotion()->mutable_rotation()->set_z(5);
        } else if (movements.at("RotateRight")) {
//            std::cout << "Rotate right" << std::endl;
            motor->mutable_locomotion()->mutable_rotation()->set_z(-5);
        } else {
            motor->mutable_locomotion()->mutable_rotation()->set_z(0);
        }

        if (movements.at("LookLeft")) {
//            std::cout << "Look left" << std::endl;
            motor->mutable_head()->set_x(20);
        } else if (movements.at("LookRight")) {
//            std::cout << "Look right" << std::endl;
            motor->mutable_head()->set_x(-20);
        } else {
            motor->mutable_head()->set_x(0);
        }

        if (movements.at("LookUp")) {
//            std::cout << "Look up" << std::endl;
            motor->mutable_head()->set_y(-20);
        } else if (movements.at("LookDown")) {
//            std::cout << "Look down" << std::endl;
            motor->mutable_head()->set_y(20);
        } else {
            motor->mutable_head()->set_y(0);
        }

        if (movements.at("IncreaseJointAngle")) {
            if (!latch_increase) {
                angles[angleIdx] += 0.2;
                latch_increase = true;
            }
        } else {
            latch_increase = false;
        }

        if (movements.at("DecreaseJointAngle")) {
            if (!latch_decrease) {
                angles[angleIdx] -= 0.2;
                latch_decrease = true;
            }
        } else {
            latch_decrease = false;
        }

        if (movements.at("NextJoint")) {
            if (!latch) {
                latch = true;
                angleIdx ++;

                if (angleIdx > angles.size()-1) {
                    angleIdx = 0;
                }

//                cout << "Index " << angleIdx << endl;
            }
        } else {
            latch = false;
        }

//        for (const float& value : angles) {
//            std::cout << value << ' ';
//        }
//        std::cout << '\n';

        motor->add_endeffectors();
        motor->mutable_endeffectors(0)->set_name("LeftEndEffector");
        motor->mutable_endeffectors(0)->set_enabled(true);
        motor->mutable_endeffectors(0)->set_angle_units(animus::data::RADIANS);
        for (const float& value : angles) {
            motor->mutable_endeffectors(0)->add_angles(value);
        }
        motor->mutable_endeffectors(0)->mutable_gripper()->set_thumb(0);

        motor->add_endeffectors();
        motor->mutable_endeffectors(1)->set_name("RightEndEffector");
        motor->mutable_endeffectors(1)->set_enabled(true);
        motor->mutable_endeffectors(1)->set_angle_units(animus::data::RADIANS);
        for (const float& value : angles) {
            motor->mutable_endeffectors(1)->add_angles(value);
        }
        motor->mutable_endeffectors(1)->mutable_gripper()->set_thumb(0);
        motor->mutable_endeffectors(1)->mutable_gripper()->set_index(0);
        motor->mutable_endeffectors(1)->mutable_gripper()->set_middle(0);
        motor->mutable_endeffectors(1)->mutable_gripper()->set_ring(0);
        motor->mutable_endeffectors(1)->mutable_gripper()->set_pinky(0);

        Robot->SetModality("motor", animus::data::DataMessage_DataType_MOTOR, motor);
    }
}

void handle_sigint(int sig) {
    std::cout << "Interrupt signal received. Closing program...\n";
    shutdownFlag.store(true); // Set the shutdown flag
}

bool hasModality(const std::string& str, const std::vector<std::string>& vec) {
    return std::find(vec.begin(), vec.end(), str) != vec.end();
}

class MainWindow : public QMainWindow {
public:
    MainWindow() : QMainWindow() {}

protected:
    void keyPressEvent(QKeyEvent* event) override {
        auto it = keyMappings.find(event->key());
        if (it != keyMappings.end()) {
            movements[it->second] = true;
        }
    }

    void keyReleaseEvent(QKeyEvent* event) override {
        auto it = keyMappings.find(event->key());
        if (it != keyMappings.end()) {
            movements[it->second] = false;
        }
    }
};

int main(int argc, char *argv[]) {
    QApplication a(argc, argv);

    keyMappings[87] = "MoveForward";
    keyMappings[83] = "MoveBack";
    keyMappings[81] = "MoveLeft";
    keyMappings[69] = "MoveRight";
    keyMappings[65] = "RotateLeft";
    keyMappings[68] = "RotateRight";
    keyMappings[90] = "MoveUp";
    keyMappings[67] = "MoveDown";
    keyMappings[16777234] = "LookLeft";
    keyMappings[16777236] = "LookRight";
    keyMappings[16777235] = "LookUp";
    keyMappings[16777237] = "LookDown";
    keyMappings[82] = "NextJoint";
    keyMappings[84] = "IncreaseJointAngle";
    keyMappings[71] = "DecreaseJointAngle";

    movements["MoveLeft"]=false;
    movements["MoveRight"]=false;
    movements["MoveForward"]=false;
    movements["MoveBack"]=false;
    movements["RotateLeft"]=false;
    movements["RotateRight"]=false;
    movements["MoveUp"]=false;
    movements["MoveDown"]=false;
    movements["LookLeft"]=false;
    movements["LookRight"]=false;
    movements["LookUp"]=false;
    movements["LookDown"]=false;
    movements["NextJoint"]=false;
    movements["IncreaseJointAngle"]=false;
    movements["DecreaseJointAngle"]=false;

    MainWindow w;
    w.show();

    auto* Robot = new bow_robot;
    std::vector<std::string> strArray = {"vision", "motor"};
    common::Error* setup_result = robot_sdk::QuickConnect(Robot, "CppBOWTutorial", strArray);
    if (!setup_result->success()) {
        cout << setup_result->description() << endl;
        return -1;
    }
    signal(SIGINT, handle_sigint);

    std::this_thread::sleep_for(std::chrono::seconds(3));

    if (hasModality("vision", strArray)) {
        threads.emplace_back(visionThread, 30, Robot);
    }

    std::this_thread::sleep_for(std::chrono::seconds(1));
    if (hasModality("speech", strArray)) {
        threads.emplace_back(speechThread, 1, Robot);
    }

    std::this_thread::sleep_for(std::chrono::seconds(1));
    if (hasModality("motor", strArray)) {
        threads.emplace_back(motorThread, 50, Robot);
    }

    a.exec();
    for (auto& thread : threads) {
        thread.join();
    }

    animus::common::Error* disconnect_result = Robot->Disconnect();
    if (!disconnect_result->success()) {
        std::cout << disconnect_result->description() << std::endl;
        return -1;
    }

    bow::robot_sdk::CloseClientInterface();
    return 0;
}
