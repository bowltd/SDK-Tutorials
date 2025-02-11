#include <iostream>
#include <csignal>
#include <thread>
#include <map>
#include <string>
#include <atomic>
#include <vector>
#include <opencv2/opencv.hpp>
#include "bow_api.h"

using namespace bow;
using namespace std;
using namespace cv;

std::atomic<bool> shutdownFlag(false);

static std::map<std::string, std::string> window_names;
void show_all_images(bow::data::ImageSamples* images_list){
    for (int i = 0; i < images_list->samples_size(); ++i){
        const auto& img_data = images_list->samples(i);
        // We will store the image to display here
        cv::Mat show_image;
        if (img_data.newdataflag()){
            int image_width = img_data.datashape(0);
            int image_height = img_data.datashape(1);

            if (img_data.imagetype() == bow::data::ImageSample::ImageTypeEnum::ImageSample_ImageTypeEnum_RGB){
                // Expecting YUV I420 data with size (width * height * 3/2)
                int expected_size = image_width * image_height * 3 / 2;
                if (static_cast<int>(img_data.data().size()) < expected_size){
                    continue; // not enough data
                }

                // Create a cv::Mat pointing to the raw YUV buffer
                // The image layout is height*3/2 rows (Y then U, V), width columns, 1 channel
                cv::Mat yuv_image(image_height * 3 / 2, image_width, CV_8UC1, const_cast<char*>(img_data.data().data()));

                // Convert from I420 YUV to RGB
                cv::cvtColor(yuv_image, show_image, cv::COLOR_YUV2RGB_IYUV);
            } else if (img_data.imagetype() == bow::data::ImageSample::ImageTypeEnum::ImageSample_ImageTypeEnum_DEPTH){
                // Expecting 16-bit unsigned depth data with size (width * height)
                // Each pixel is 2 bytes => total Data size = (width * height * 2)
                int expected_pixel_count = image_width * image_height;
                int expected_size_bytes = expected_pixel_count * static_cast<int>(sizeof(uint16_t));
                if (static_cast<int>(img_data.data().size()) < expected_size_bytes){
                    continue; // not enough data
                }

                // Interpret Data as 16-bit depth
                cv::Mat depth_image(image_height, image_width, CV_16UC1,const_cast<char*>(img_data.data().data()));

                // Normalize depth range to 0-255 (8-bit) so we can visualize
                cv::Mat normalized_depth;
                cv::normalize(depth_image, normalized_depth, 0, 255, cv::NORM_MINMAX, CV_8UC1);

                // Apply a colormap for visualization
                cv::applyColorMap(normalized_depth, show_image, cv::COLORMAP_JET);
            } else {
                std::cout << "Unknown image type" << std::endl;
            }
        }

        //If we got a valid image to display, show it
        if (!show_image.empty()) {
            // If we haven't seen this Source name before, create a new window
            if (window_names.find(img_data.source()) == window_names.end()) {
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

// Handle CTRL+C (SIGINT)
void handle_sigint(int sig) {
    std::cout << "Interrupt signal received. Closing program...\n";
    shutdownFlag.store(true);
}

int main(int argc, char *argv[]) {
    std::cout << bow_api::version() << std::endl;

    std::vector<std::string> strArray = {"vision"};
    std::unique_ptr<bow::common::Error> setup_result = std::make_unique<bow::common::Error>();

    auto* Robot= bow_api::quickConnect("BOW_Tutorial", strArray, true, nullptr, setup_result.get());

    if (!setup_result->success() || !Robot) {
        std::cout << setup_result->description() << std::endl;
        return -1;
    }

    signal(SIGINT, handle_sigint);

    // Main sampling loop
    while (!shutdownFlag.load()) {
        auto imageSamples = Robot->vision->get(true);
        if (imageSamples.has_value()) {
            show_all_images(imageSamples.value());
        }
        imageSamples.reset();
    }

    // Disconnect
    std::unique_ptr<bow::common::Error> disconnect_result(Robot->disconnect());
    if (!disconnect_result->success()) {
        std::cout << disconnect_result->description() << std::endl;
        return -1;
    }
    cv::destroyAllWindows();
    bow_api::stopEngine();
    return 0;
}
