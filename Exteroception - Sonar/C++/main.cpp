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

string identify_front_sonar(const google::protobuf::RepeatedPtrField<data::Range>& range_sensors) {
    vector<bow::data::Range> sonars;
    for (const auto& sensor : range_sensors) {
        cout << sensor.source() << endl;
        if (sensor.operationtype() == bow::data::Range::OperationTypeEnum::Range_OperationTypeEnum_Ultrasound) {
            sonars.push_back(sensor);
        }
    }

    float front_sonar_x_pos = -100.0;
    string front_sonar_name;
    for (const auto& sonar : sonars) {
        if (sonar.transform().position().x() > front_sonar_x_pos) {
            front_sonar_x_pos = sonar.transform().position().x();
            front_sonar_name = sonar.source();
        }
    }
    return front_sonar_name;
}

int main(int argc, char *argv[]) {
    auto* Robot = new bow_sdk::bow_robot();
    std::vector<std::string> strArray = {"vision", "motor", "exteroception"};
    bow::common::Error* setup_result = bow_sdk::client_sdk::QuickConnect(Robot, "CppBOWTutorial", strArray, true);
    if (!setup_result->success()) {
        cout << setup_result->description() << endl;
        return -1;
    }

    auto* ext = Robot->GetModality("exteroception", true);
    auto ext_sample = new bow::data::ExteroceptionSample();
    ext_sample->MergeFromString(ext->mutable_sample()->data());
    while (ext_sample->range().empty()) {
        cout << "Range Sensors Empty" << endl;
        ext = Robot->GetModality("exteroception", true);
        ext_sample = new bow::data::ExteroceptionSample();
        ext_sample->MergeFromString(ext->mutable_sample()->data());
    }
    string front_sonar = identify_front_sonar(ext_sample->range());
    cout << front_sonar << endl;


    auto delay = rateToTimerDelay(10);
    string window_name = "Robot view";
    cv::namedWindow("Image", cv::WINDOW_NORMAL);
    auto receivedRGB = new Mat();

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
                    cv::waitKey(1);
                }
            }
        } catch (const std::exception& ex) {
            std::cerr << "Exception caught: " << ex.what() << std::endl;
        }

        // Exteroception
        ext = Robot->GetModality("exteroception", true);
        ext_sample = new bow::data::ExteroceptionSample();
        ext_sample->MergeFromString(ext->mutable_sample()->data());

        // Get front sonar
        bow::data::Range sonar;
        for (const auto& range_sensor : ext_sample->range()) {
            if (range_sensor.source() == front_sonar) {
                sonar = range_sensor;
            }
        }

        cout << sonar.data() << endl;
        auto* motor_command = new bow::data::MotorSample();
        if (sonar.data() == -1) {
            cout << "Invalid Sonar Data" << endl;
            motor_command->mutable_locomotion()->mutable_rotationalvelocity()->set_z(1);
        } else if (sonar.data() == 0) {
            cout << "No obstruction in range" << endl;
            motor_command->mutable_locomotion()->mutable_translationalvelocity()->set_x(1);
        } else if (sonar.min() + 0.5 < sonar.data() < sonar.min() + 1.5) {
            cout << "Obstruction approaching sensor minimum" << endl;
            motor_command->mutable_locomotion()->mutable_rotationalvelocity()->set_z(1);
        } else if (sonar.data() <sonar.min() + 0.5) {
            cout << "Obstruction too close to maneuver, reverse and turn" << endl;
//motor_command->mutable_locomotion()->mutable_rotationalvelocity()->set_z(1);
            motor_command->mutable_locomotion()->mutable_translationalvelocity()->set_x(-1);
        } else {
            cout << "Obstruction detected at safe range" << endl;
            motor_command->mutable_locomotion()->mutable_translationalvelocity()->set_x(1);
        }

        Robot->SetModality("motor", bow::structs::DataMessage_DataType_MOTOR, motor_command);
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
