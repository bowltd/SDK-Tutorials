#include <iostream>
#include <unistd.h>
#include <csignal>
#include <chrono>
#include <thread>
#include <map>
#include <string>

#include <opencv2/imgcodecs.hpp>
#include <opencv2/highgui.hpp>
#include <opencv2/core.hpp>
#include <opencv2/imgproc.hpp>

#include <bow_structs.pb.h>
#include <bow_sdk.h>

using namespace bow;
using namespace cv;
using namespace std;

std::atomic<bool> shutdownFlag(false);

std::chrono::nanoseconds rateToTimerDelay(double hertz) {
    double delayInSeconds = 1 / hertz;
    double delayInNanoseconds = delayInSeconds * 1e9;
    return std::chrono::nanoseconds(static_cast<long>(delayInNanoseconds));
}

bool hasModality(const std::string& str, const std::vector<std::string>& vec) {
    return std::find(vec.begin(), vec.end(), str) != vec.end();
}

void handle_sigint(int sig) {
    std::cout << "Interrupt signal received. Closing program...\n";
    shutdownFlag.store(true); // Set the shutdown flag
}

int main(int argc, char *argv[]) {

    // Setup
    auto* Robot = new bow_sdk::bow_robot();
    std::vector<std::string> strArray = {"vision", "motor"};
    bow::common::Error* setup_result = bow_sdk::client_sdk::QuickConnect(Robot, "CppBOWTutorial", strArray, true);
    if (!setup_result->success()) {
        cout << setup_result->description() << endl;
        return -1;
    }

    auto delay = rateToTimerDelay(30);
    string window_name = "Robot view";
    cv::namedWindow("Image", cv::WINDOW_NORMAL);
    auto receivedRGB = new Mat();
    std::cout << "Select the 'Image' window to make it active and enable reading of key presses" << std::endl;

    int decision = 0;

    while (!shutdownFlag.load()) {
        auto* sample = Robot->GetModality("vision", false);
        auto image_samples = new bow::data::ImageSamples();
        image_samples->MergeFromString(sample->mutable_sample()->data());
        try {
            // Step 1 - Sense
            if (image_samples->samples_size() == 0) {
                continue;
            }

            auto s = image_samples->samples(0);
            int expectedSize = s.datashape(1) * s.datashape(0) * 3 / 2;

            if (s.data().size() != expectedSize) {
                continue;
            }

            if (!s.newdataflag()) {
                continue;
            }

            auto receivedYuv = new cv::Mat(s.datashape(1)*3/2, s.datashape(0), CV_8UC1, const_cast<char*>(s.data().data()));
            cv::cvtColor(*receivedYuv, *receivedRGB, cv::COLOR_YUV2RGB_IYUV);
        } catch (const std::exception& ex) {
            std::cerr << "Exception caught: " << ex.what() << std::endl;
        }

        cv::imshow("Image", *receivedRGB);

        // Step 2 - Plan
        decision = cv::waitKey(1);
        if (decision != -1) {
            std::cout << "Key pressed has ASCII value: " << decision << std::endl;
        }

        // Step 3 - Act
        auto motorSample = new bow::data::MotorSample();
        if (decision == 'w') {
            motorSample->mutable_locomotion()->mutable_translationalvelocity()->set_x(1);
            std::cout << "Moving forward" << std::endl;
        } else if (decision == 's') {
            motorSample->mutable_locomotion()->mutable_translationalvelocity()->set_x(-1);
            std::cout << "Moving backward" << std::endl;
        } else if (decision == 'd') {
            motorSample->mutable_locomotion()->mutable_rotationalvelocity()->set_z(-1);
            std::cout << "Rotate right" << std::endl;
        } else if (decision == 'a') {
            motorSample->mutable_locomotion()->mutable_rotationalvelocity()->set_z(1);
            std::cout << "Rotate left" << std::endl;
        } else if (decision == 'e') {
            motorSample->mutable_locomotion()->mutable_translationalvelocity()->set_y(-1);
            std::cout << "Strafe right" << std::endl;
        } else if (decision == 'q') {
            motorSample->mutable_locomotion()->mutable_translationalvelocity()->set_y(1);
            std::cout << "Strafe left" << std::endl;
        }
        Robot->SetModality("motor", bow::structs::DataMessage_DataType_MOTOR, motorSample);
    }

    cv::destroyWindow(window_name);

    bow::common::Error* disconnect_result = Robot->Disconnect();
    if (!disconnect_result->success()) {
        std::cout << disconnect_result->description() << std::endl;
        return -1;
    }

    bow_sdk::client_sdk::CloseClientInterface();
    return 0;
}
