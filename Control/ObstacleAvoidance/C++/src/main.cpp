#include <iostream>
#include <chrono>
#include <thread>
#include <map>
#include <string>

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
    string front_sonar_name;
    for (const auto& sonar : sonars) {
        if (sonar.transform().position().x() > front_sonar_x_pos) {
            front_sonar_x_pos = sonar.transform().position().x();
            front_sonar_name = sonar.source();
        }
    }

    // Return the name of the forward most sonar sensor
    return front_sonar_name;
}

int main(int argc, char *argv[]) {
    std::cout << bow_api::version() << std::endl;




    // Setup
    std::vector<std::string> strArray = {"vision", "motor","exteroception"};
    std::unique_ptr<bow::common::Error> setup_result = std::make_unique<bow::common::Error>();
    auto* Robot= bow_api::quickConnect("SendingCommands", strArray, true, nullptr, setup_result.get());
    if (!setup_result->success() || !Robot) {
        std::cout << setup_result->description() << std::endl;
        return -1;
    }


    std::optional<bow::data::ExteroceptionSample*> exSample;
    while (true) {
        //auto exSample = Robot->exteroception->get(true);
        exSample = Robot->exteroception->get(true);
        if (exSample.has_value()) {
            break;
        }
    }

    // Identify the forward most sonar sensor
    string front_sonar = identify_front_sonar(exSample.value()->range());

    // OpenCV Configuration
    cv::namedWindow("Image", cv::WINDOW_NORMAL);
    auto receivedRGB = new Mat();

    // Calculate delay needed for rate of loop execution
    auto delay = rateToTimerDelay(10);
    string window_name = "Robot view";

    while (!shutdownFlag.load()) {
        // SENSE
        // Vision
        // Get and display all images
        auto imageSamples = Robot->vision->get(true);
        if (imageSamples.has_value()) {
            show_all_images(imageSamples.value());
        }

        // Exteroception
        // Get exteroception sample
        exSample = Robot->exteroception->get(true);

        // Iterate through range sensors until front sensor
        bow::data::Range sonar;
        for (const auto& range_sensor : exSample.value()->range()) {
            if (range_sensor.source() == front_sonar) {
                sonar = range_sensor;
                break;
            }
        }

        // DECIDE
        // Create a motor message to populate
        auto* motorSample = new bow::data::MotorSample();

        // Base the velocity command on the sonar reading
        if (sonar.data() == -1) {
            cout << "Invalid Sonar Data: " << sonar.data() << " meters" << endl;
            motorSample->mutable_locomotion()->mutable_rotationalvelocity()->set_z(0.5);
        } else if (sonar.data() == 0) {
            cout << "No obstruction in range: " << sonar.data() << " meters" << endl;
            motorSample->mutable_locomotion()->mutable_translationalvelocity()->set_x(0.2);
        } else if (sonar.min() + 0.5 < sonar.data() < sonar.min() + 1.5) {
            cout << "Obstruction approaching sensor minimum: " << sonar.data() << " meters" << endl;
            motorSample->mutable_locomotion()->mutable_rotationalvelocity()->set_z(0.5);
        } else if (sonar.data() <sonar.min() + 0.5) {
            cout << "Obstruction too close to maneuver, reverse: " << sonar.data() << " meters" << endl;
            motorSample->mutable_locomotion()->mutable_translationalvelocity()->set_x(-0.2);
        } else {
            cout << "Obstruction detected at safe range: " << sonar.data() << " meters" << endl;
            motorSample->mutable_locomotion()->mutable_translationalvelocity()->set_x(0.2);
        }

        // ACT
        // Send the motor command
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
