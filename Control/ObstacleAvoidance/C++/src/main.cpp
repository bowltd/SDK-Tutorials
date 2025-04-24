 #include <iostream>
#include <chrono>
#include <thread>
#include <map>
#include <string>
#include <csignal>

#include <opencv2/imgcodecs.hpp>
#include <opencv2/highgui.hpp>
#include <opencv2/core.hpp>
#include <opencv2/imgproc.hpp>

#include <bow_structs.pb.h>
#include <bow_api.h>

using namespace bow;
using namespace cv;
using namespace std;

static std::map<std::string, std::string> window_names;
void show_all_images(bow::data::ImageSamples* images_list)
{
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

string identify_front_sonar(const google::protobuf::RepeatedPtrField<data::Range>& range_sensors) {
    // Iterate through all range sensors and identify the sonar sensors
    vector<bow::data::Range> sonars;
    for (const auto& sensor : range_sensors) {
        if (sensor.operationtype() == bow::data::Range::OperationTypeEnum::Range_OperationTypeEnum_Ultrasound) {
            sonars.push_back(sensor);
        }
    }

    // Iterate through the sonars and find the sensor with the largest X position (furthest forward)
    float front_sonar_x_pos = -100.0;
    string front_sonar_name = "none";
    for (const auto& sonar : sonars) {
        if (sonar.transform().position().x() > front_sonar_x_pos) {
            front_sonar_x_pos = sonar.transform().position().x();
            front_sonar_name = sonar.source();
        }
    }

    cout << "front_sonar_name: " << front_sonar_name << endl;

    // Return the name of the forward most sonar sensor
    return front_sonar_name;
}


int main(int argc, char *argv[]) {
    std::cout << bow_api::version() << std::endl;

    signal(SIGINT, handle_sigint);

    // Step 1: Quick Connect
    std::vector<std::string> strArray = {"vision", "motor","exteroception"};
    std::unique_ptr<bow::common::Error> setup_result = std::make_unique<bow::common::Error>();
    auto* Robot= bow_api::quickConnect("BOW_Example", strArray, true, nullptr, setup_result.get());
    if (!setup_result->success() || !Robot) {
        std::cout << setup_result->description() << std::endl;
        return -1;
    }

    std::optional<bow::data::ExteroceptionSample*> exSample;
    while (true) {
        exSample = Robot->exteroception->get(true);
        if (exSample.has_value()) {
            break;
        }
    }

    // Step 2: Sample the exteroception channel to identify front-most ultrasound sensor
    string front_sonar = identify_front_sonar(exSample.value()->range());
    if (front_sonar == "none") {
        std::cout << "no sonar sensor found" << std::endl;
        exit(1);
    }

    // OpenCV Configuration
    cv::namedWindow("Image", cv::WINDOW_NORMAL);
    auto receivedRGB = new Mat();

    // Calculate delay needed for rate of loop execution
    auto delay = rateToTimerDelay(10);
    string window_name = "Robot view";

    // control variables for approach

    float target_distance = 0.2;
    float slowing_rate = 4.0;
    float max_speed = 0.5;

    // control variables for rotation
    float rotation_speed = 0.5;
    int min_rotation_steps = 50;
    int max_rotation_steps = 100;
    int rotation_steps = min_rotation_steps;
    int rotation_counter = 0;

    // Step 3: Begin closed loop control
    while (!shutdownFlag.load()) {

        // Step 4: get/show vision
        auto imageSamples = Robot->vision->get(true);
        if (imageSamples.has_value()) {
            show_all_images(imageSamples.value());
        }

        // Step 5: sample front-most ultrasound sensor
        exSample = Robot->exteroception->get(true);
        bow::data::Range sonar;
        for (const auto& range_sensor : exSample.value()->range()) {
            if (range_sensor.source() == front_sonar) {
                sonar = range_sensor;
                break;
            }
        }

        // Step 6: construct motor message and implement decision-making logic
        auto* motorSample = new bow::data::MotorSample();
        if (rotation_counter < rotation_steps) {
            // Rotating
            motorSample->mutable_locomotion()->mutable_rotationalvelocity()->set_z(rotation_speed);
        } else {
            if (sonar.data() <= sonar.min()) {
                // Obstruction below minimum range, so reverse
                motorSample->mutable_locomotion()->mutable_translationalvelocity()->set_x(-max_speed);
            } else if (sonar.data() >= sonar.max()) {
                // Obstruction beyond maximum range, so move forward quickly
                motorSample->mutable_locomotion()->mutable_translationalvelocity()->set_x(max_speed);
            } else if (fabs(sonar.data()-target_distance)<0.05) {
                // Obstruction at target range, so restart the rotation loop
                rotation_counter = 0;
                if ((float)rand()/(float)RAND_MAX < 0.5) {
                    rotation_speed *= -1;
                }
                rotation_steps = min_rotation_steps + int((max_rotation_steps-min_rotation_steps)*(float)rand()/(float)RAND_MAX);
            } else {
                // Obstruction in sensing range, so slowing the approach
                float target_offset_distance = sonar.data()-target_distance;
                float unit_velocity = 1.0-exp(-target_offset_distance/slowing_rate);
                motorSample->mutable_locomotion()->mutable_translationalvelocity()->set_x(max_speed*unit_velocity);
            }
        }
        rotation_counter++;

        // Step 7: Send the motor command
        Robot->motor->set(motorSample);

        // Delay to control the rate of loop execution
        std::this_thread::sleep_for(delay);
    }

    cv::destroyWindow(window_name);

    bow::common::Error* disconnect_result = Robot->disconnect();
    if (!disconnect_result->success()) {
        std::cout << disconnect_result->description() << std::endl;
        return -1;
    }

    bow_api::stopEngine();
    return 0;
}