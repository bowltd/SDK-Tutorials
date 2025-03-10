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
#include "bow_api.h"

using namespace bow;
using namespace cv;
using namespace std;

bow::data::MotorSample* keyboard_control(int keyID){
    auto motorSample = new bow::data::MotorSample();
    if (keyID == 'w') {
        motorSample->mutable_locomotion()->mutable_translationalvelocity()->set_x(1);
        std::cout << "Moving forward" << std::endl;
    } else if (keyID == 's') {
        motorSample->mutable_locomotion()->mutable_translationalvelocity()->set_x(-1);
        std::cout << "Moving backward" << std::endl;
    } else if (keyID == 'd') {
        motorSample->mutable_locomotion()->mutable_rotationalvelocity()->set_z(-1);
        std::cout << "Rotate right" << std::endl;
    } else if (keyID == 'a') {
        motorSample->mutable_locomotion()->mutable_rotationalvelocity()->set_z(1);
        std::cout << "Rotate left" << std::endl;
    } else if (keyID == 'e') {
        motorSample->mutable_locomotion()->mutable_translationalvelocity()->set_y(-1);
        std::cout << "Strafe right" << std::endl;
    } else if (keyID == 'q') {
        motorSample->mutable_locomotion()->mutable_translationalvelocity()->set_y(1);
        std::cout << "Strafe left" << std::endl;
    }
    return motorSample;
}

static std::map<std::string, std::string> window_names;
void show_all_images(bow::data::ImageSamples* images_list) {
    for (int i = 0; i < images_list->samples_size(); ++i)
    {
        const auto& img_data = images_list->samples(i);

        // We will store the image to display here
        cv::Mat show_image;

        if (img_data.newdataflag())
        {
            int image_width = img_data.datashape(0);
            int image_height = img_data.datashape(1);

            if (img_data.imagetype() == bow::data::ImageSample::ImageTypeEnum::ImageSample_ImageTypeEnum_RGB)
            {
                // Expecting YUV I420 data with size (width * height * 3/2)
                int expected_size = image_width * image_height * 3 / 2;
                if (static_cast<int>(img_data.data().size()) < expected_size)
                {
                    continue; // not enough data
                }

                // Create a cv::Mat pointing to the raw YUV buffer
                // The image layout is height*3/2 rows (Y then U, V), width columns, 1 channel
                cv::Mat yuv_image(image_height * 3 / 2, image_width, CV_8UC1, const_cast<char*>(img_data.data().data()));

                // Convert from I420 YUV to RGB
                cv::cvtColor(yuv_image, show_image, cv::COLOR_YUV2RGB_IYUV);
            }
            else if (img_data.imagetype() == bow::data::ImageSample::ImageTypeEnum::ImageSample_ImageTypeEnum_DEPTH)
            {
                // Expecting 16-bit unsigned depth data with size (width * height)
                // Each pixel is 2 bytes => total Data size = (width * height * 2)
                int expected_pixel_count = image_width * image_height;
                int expected_size_bytes = expected_pixel_count * static_cast<int>(sizeof(uint16_t));
                if (static_cast<int>(img_data.data().size()) < expected_size_bytes)
                {
                    continue; // not enough data
                }

                // Interpret Data as 16-bit depth
                cv::Mat depth_image(image_height, image_width, CV_16UC1,const_cast<char*>(img_data.data().data()));

                // Normalize depth range to 0-255 (8-bit) so we can visualize
                cv::Mat normalized_depth;
                cv::normalize(depth_image, normalized_depth, 0, 255, cv::NORM_MINMAX, CV_8UC1);

                // Apply a colormap for visualization
                cv::applyColorMap(normalized_depth, show_image, cv::COLORMAP_JET);
            }
            else
            {
                std::cout << "Unknown image type" << std::endl;
            }
        }

        //If we got a valid image to display, show it
        if (!show_image.empty())
        {
            // If we haven't seen this Source name before, create a new window
            if (window_names.find(img_data.source()) == window_names.end())
            {
                std::string window_name = "RobotView" + std::to_string(window_names.size())
                                          + " - " + img_data.source();
                std::cout << window_name << std::endl;

                window_names[img_data.source()] = window_name;

                // Create the window
                cv::namedWindow(window_name, cv::WINDOW_AUTOSIZE);
                // Just a small wait so the window can be created
                cv::waitKey(1);
            }

            // Show the image in the existing or new window
            cv::imshow(window_names[img_data.source()], show_image);
            // A minimal waitKey(1) ensures the image is actually updated
            cv::waitKey(1);
        }
    }
}


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

    std::vector<std::string> strArray = {"vision", "motor"};
    std::unique_ptr<bow::common::Error> setup_result = std::make_unique<bow::common::Error>();

    auto* myRobot= bow_api::quickConnect("CppBOWTutorial", strArray, true, nullptr, setup_result.get());

    if (!setup_result->success() || !myRobot) {
        std::cout << setup_result->description() << std::endl;
        return -1;
    }

    signal(SIGINT, handle_sigint);


    auto delay = rateToTimerDelay(30);
    while (!shutdownFlag.load()) {
        auto imageSamples = myRobot->vision->get(true);
        if (imageSamples.has_value()) {
            show_all_images(imageSamples.value());
        }
        imageSamples.reset();

        // Step 2 - Plan
        int keyID = cv::waitKey(1);
        if (keyID != -1) {
            std::cout << "Key pressed has ASCII value: " << keyID << std::endl;
        }

        bow::data::MotorSample* motorSample = keyboard_control(keyID);

        myRobot->motor->set(motorSample);
    }

    cv::destroyAllWindows();

    bow::common::Error* disconnect_result = myRobot->disconnect();
    if (!disconnect_result->success()) {
        std::cout << disconnect_result->description() << std::endl;
        delete myRobot; // Free allocated memory
        return -1;
    }

    bow_api::stopEngine();                                                                        //Close Client
    delete myRobot; // Free allocated memory
    return 0;
}