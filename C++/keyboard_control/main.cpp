// System
#include <iostream>
#include <csignal>
#include <thread>

// OpenCV
#include <opencv2/highgui.hpp>
#include <opencv2/core.hpp>
#include <opencv2/imgproc.hpp>

// SFML for keyboard capture
#include <SFML/Graphics.hpp>

// BOW
#include "animus_structs.pb.h"
#include "bow_sdk.h"

// Namespaces
using namespace bow;  // BOW
using namespace animus; // BOW Other
using namespace sf; // SFML
using namespace cv; // OpenCV
using namespace std;

atomic<bool> shutdownFlag(false); // Flag to exit loop

// Handle Signal Interrupts
void handle_sigint(int sig) {
    cout << "Interrupt signal received. Closing program...\n";
    shutdownFlag.store(true); // Set the shutdown flag
}

// Main
int main() {

    // Create OpenCV Window to display vision output
    string window_name = "Robot view";
    cv::namedWindow(window_name, cv::WINDOW_NORMAL);

    // Mat to hold received image
    auto receivedRGB = new Mat();

    // BOW robot object
    auto* Robot = new bow_robot;

    // List of modalities to open
    vector<string> strArray = {"vision", "motor"};

    // Quick connect to selected robot
    common::Error* setup_result = bow::client_sdk::QuickConnect(Robot, "CppBOWTutorial", strArray);
    if (!setup_result->success()) {
        cout << setup_result->description() << endl;
        return -1;
    }

    // Sleep for 3 seconds to allow connection to stabilise
//    this_thread::sleep_for(std::chrono::seconds(3));

    // Main Loop
    while (!shutdownFlag.load()) {
        signal(SIGINT, handle_sigint); // Handle Interrupts

        // Get sample from vision channel
        auto* sample = Robot->GetModality("vision", true);
        auto image_samples = new bow::data::ImageSamples();

        ////////// EXPLAIN MERGE FORM STRING? .//////////////////
        image_samples->MergeFromString(sample->mutable_sample()->data());
        try {
            // If image exists
            if (image_samples->samples_size() > 0) {

                // Convert image to displayable format
                auto s = image_samples->samples(0);
//                auto receivedYuv = new cv::Mat(s.datashape(1)*3/2, s.datashape(0), CV_8UC1, const_cast<char*>(s.data().data()));
                auto receivedYuv = new cv::Mat(s.datashape(1)*3/2, s.datashape(0), CV_8UC1, const_cast<char*>(s.data().data()));
                cout << "Convert Colour"<< endl;
//                this_thread::sleep_for(std::chrono::milliseconds(1000));
                cv::cvtColor(*receivedYuv, *receivedRGB, cv::COLOR_YUV2RGB_IYUV);

                // Display image in created window
                cv::imshow(window_name, *receivedRGB);
                cv::waitKey(1);
            }

        } catch (const exception& ex) {
            // Catch and handle the exception
            cerr << "Exception caught: " << ex.what() << endl;
        }

        //Create a motor sample
        auto motor = new bow::data::MotorSample();

        // Set locomotion mode to velocity
        motor->mutable_locomotion()->set_locomotionmode(bow::data::VELOCITY_MODE);

        if (Keyboard::isKeyPressed(Keyboard::W))
        {
            std::cout << "Move Forward" << std::endl;
            motor->mutable_locomotion()->mutable_position()->set_x(1);
        }
        else if (Keyboard::isKeyPressed(Keyboard::S))
        {
            std::cout << "Move Backward" << std::endl;
            motor->mutable_locomotion()->mutable_position()->set_x(-1);
        }

        if (Keyboard::isKeyPressed(Keyboard::A))
        {
            std::cout << "Rotate Left" << std::endl;
            motor->mutable_locomotion()->mutable_rotation()->set_z(5);
        }
        else if (Keyboard::isKeyPressed(Keyboard::D))
        {
            std::cout << "Rotate Right" << std::endl;
            motor->mutable_locomotion()->mutable_rotation()->set_z(-5);
        }

        if (Keyboard::isKeyPressed(Keyboard::Q))
        {
            std::cout << "Move Left" << std::endl;
            motor->mutable_locomotion()->mutable_position()->set_y(1);
        }
        else if (Keyboard::isKeyPressed(Keyboard::E))
        {
            std::cout << "Move Right" << std::endl;
            motor->mutable_locomotion()->mutable_position()->set_y(-1);
        }

        // Get keyboard state and apply to motor data message
        if (Keyboard::isKeyPressed(Keyboard::Left))
        {
            std::cout << "Look left" << std::endl;
            motor->mutable_head()->set_x(20);
        }
        else if (Keyboard::isKeyPressed(Keyboard::Right))
        {
            std::cout << "Look right" << std::endl;
            motor->mutable_head()->set_x(-20);
        }

        if (Keyboard::isKeyPressed(Keyboard::Down))
        {
            std::cout << "Look down" << std::endl;
            motor->mutable_head()->set_y(20);
        }
        else if (Keyboard::isKeyPressed(Keyboard::Up))
        {
            std::cout << "Look up" << std::endl;
            motor->mutable_head()->set_y(-20);
        }

        if (Keyboard::isKeyPressed(Keyboard::Escape))
        {
            std::cout << "Escape key pressed. Exiting..." << std::endl;
            shutdownFlag.store(true); // Set the shutdown flag
        }

        // Send Motor Sample on motor modality channel
        Robot->SetModality("motor", animus::structs::DataMessage_DataType_MOTOR, motor);
    }

    destroyWindow(window_name);

    // Disconnect from the robot
    animus::common::Error* disconnect_result = Robot->Disconnect();
    if (!disconnect_result->success()) {
        cout << disconnect_result->description() << endl;
        return -1;
    }

    // Close the client application
    client_sdk::CloseClientInterface();
    return 0;
}
