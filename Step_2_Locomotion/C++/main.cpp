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

    while (!shutdownFlag.load()) {
        std::this_thread::sleep_for(delay);

        auto* sample = Robot->GetModality("vision", true);
        auto image_samples = new bow::data::ImageSamples();
        image_samples->MergeFromString(sample->mutable_sample()->data());
        try {
            if (image_samples->samples_size() > 0) {
                auto s = image_samples->samples(0);
                if (s.newdataflag()) {
                    auto receivedYuv = new cv::Mat(s.datashape(1)*3/2, s.datashape(0), CV_8UC1, const_cast<char*>(s.data().data()));
                    cv::cvtColor(*receivedYuv, *receivedRGB, cv::COLOR_YUV2RGB_IYUV);
                    cv::imshow("Image", *receivedRGB);
                    int key = cv::waitKey(1);
                    if (key != -1) {
                        std::cout << "Key pressed has ASCII value: " << key << std::endl;
                    }
                }
            }
        } catch (const std::exception& ex) {
            std::cerr << "Exception caught: " << ex.what() << std::endl;
        }
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
