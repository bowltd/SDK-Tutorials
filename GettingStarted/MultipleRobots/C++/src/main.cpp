#include <iostream>
#include <csignal>
#include <chrono>
#include <thread>
#include <map>
#include <string>
#include <atomic>
#include <vector>
#include "bow_api.h"
#include <opencv2/opencv.hpp>

#ifdef _WIN32
#include <conio.h>
bool kbhit() {
    return _kbhit();
}
char getch() {
    return _getch();
}
#else
#include <termios.h>
#include <unistd.h>
#include <fcntl.h>
bool kbhit() {
    struct termios oldt, newt;
    int ch;
    int oldf;

    tcgetattr(STDIN_FILENO, &oldt);
    newt = oldt;
    newt.c_lflag &= ~(ICANON | ECHO);
    tcsetattr(STDIN_FILENO, TCSANOW, &newt);
    oldf = fcntl(STDIN_FILENO, F_GETFL, 0);
    fcntl(STDIN_FILENO, F_SETFL, oldf | O_NONBLOCK);

    ch = getchar();

    tcsetattr(STDIN_FILENO, TCSANOW, &oldt);
    fcntl(STDIN_FILENO, F_SETFL, oldf);

    if (ch != EOF) {
        ungetc(ch, stdin);
        return true;
    }
    return false;
}
char getch() {
    return getchar();
}
#endif

using namespace bow;
using namespace std;
using namespace cv;

std::vector<std::thread> threads;
std::atomic<bool> shutdownFlag(false);
std::map<int, std::string> keyMappings = {
        {'w', "MoveForward"}, {'s', "MoveBack"},
        {'a', "RotateLeft"}, {'d', "RotateRight"},
        {'q', "MoveLeft"}, {'e', "MoveRight"},
        {'r', "MoveUp"}, {'f', "MoveDown"},
        {'j', "LookLeft"}, {'l', "LookRight"},
        {'i', "LookUp"}, {'k', "LookDown"},
};


std::chrono::nanoseconds rateToTimerDelay(double hertz) {
    double delayInSeconds = 1 / hertz;
    double delayInNanoseconds = delayInSeconds * 1e9;
    return std::chrono::nanoseconds(static_cast<long>(delayInNanoseconds));
}

std::map<std::string, bool> movements;

void keyboardListener() {
    while (!shutdownFlag.load()) {
        if (kbhit()) {
            char key = getch();
            if (key == 'x') {
                shutdownFlag.store(true);
                break;
            }
            if (keyMappings.count(key)) {
                movements[keyMappings[key]] = true;
            }
        }
        std::this_thread::sleep_for(std::chrono::milliseconds(50));
    }
}

void motorThread(double rate, bow_robot *Robot) {
    auto delay = rateToTimerDelay(rate);
    while (!shutdownFlag.load()) {
        std::this_thread::sleep_for(delay);

        auto motor = new bow::data::MotorSample();

        // Set movement flags
        if (movements["MoveBack"]) {
            motor->mutable_locomotion()->mutable_translationalvelocity()->set_x(-0.2);
        } else if (movements["MoveForward"]) {
            motor->mutable_locomotion()->mutable_translationalvelocity()->set_x(0.2);
        } else {
            motor->mutable_locomotion()->mutable_translationalvelocity()->set_x(0);
        }

        if (movements["MoveLeft"]) {
            motor->mutable_locomotion()->mutable_translationalvelocity()->set_y(1);
        } else if (movements["MoveRight"]) {
            motor->mutable_locomotion()->mutable_translationalvelocity()->set_y(-1);
        } else {
            motor->mutable_locomotion()->mutable_translationalvelocity()->set_y(0);
        }

        if (movements["MoveUp"]) {
            motor->mutable_locomotion()->mutable_translationalvelocity()->set_z(1);
        } else if (movements["MoveDown"]) {
            motor->mutable_locomotion()->mutable_translationalvelocity()->set_z(-1);
        } else {
            motor->mutable_locomotion()->mutable_translationalvelocity()->set_z(0);
        }

        if (movements["RotateLeft"]) {
            motor->mutable_locomotion()->mutable_rotationalvelocity()->set_z(1);
        } else if (movements["RotateRight"]) {
            motor->mutable_locomotion()->mutable_rotationalvelocity()->set_z(-1);
        } else {
            motor->mutable_locomotion()->mutable_rotationalvelocity()->set_z(0);
        }

        // Reset movement states (optional)
        for (auto& movement : movements) {
            movement.second = false;
        }

        Robot->motor->set(motor);
    }
}

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

void visionThread(double rate, bow_robot* Robot)
{
    auto delay = rateToTimerDelay(rate);
    while (!shutdownFlag.load()) {
        std::this_thread::sleep_for(delay);

        auto imageSamples = Robot->vision->get(true);
        if (imageSamples.has_value()) {
            show_all_images(imageSamples.value());
        }
        imageSamples.reset();
    }
}

// ✅ 4️⃣ Handle CTRL+C (SIGINT)
void handle_sigint(int sig) {
    std::cout << "Interrupt signal received. Closing program...\n";
    shutdownFlag.store(true);
}


int GetRobotSelection(std::string prompt, int robotCount, std::vector<int> selected){
    while (true) {
        try {
            std::cout << prompt << std::endl;
            std::string input;
            std::getline(std::cin, input);
            int idx = stoi(input);
            if (idx >= 0 && idx < robotCount) {
                bool alreadyChosen = false;
                for (int i=0;i<selected.size();i++) {
                    if (selected[i] == idx) {
                        alreadyChosen = true;
                        break;
                    }
                }
                if (alreadyChosen) {
                    std::cout << "Cannot choose the same robot again" << std::endl;
                } else {
                    return idx;
                }
            } else {
                std::cout << "Invalid index. Please try again." <<std::endl;
            }
        } catch (std::invalid_argument){
            std::cout << "Invalid input. Please enter a valid integer index."<< std::endl;
        }
    }
}


int main(int argc, char** argv) {
    int _numRobots = 2;

    std::vector<std::string> channels = { "vision", "motor" };

    bow::structs::AudioParams* audioParams = new bow::structs::AudioParams();
    audioParams->clear_backends();
    audioParams->add_backends("");
    audioParams->set_samplerate(24000);
    audioParams->set_channels(1);
    audioParams->set_sizeinframes(true);
    audioParams->set_transmitrate(25);

    // start engine
    bow::common::Error* setupResult = bow_api::startEngine("BOW_Example", true, audioParams);
    if (!setupResult->success()) {
        std::cout << "Start engine failed: " << setupResult->description() << std::endl;
        return -1;
    }

    // login
    bow::common::Error* loginResult = bow_api::loginUser("", "", true);
    if (!loginResult->success()){
        std::cout << "Login failed: " << loginResult->description() << std::endl;
        return -1;
    }

    // get robots
    bow::sdk::GetRobotsProtoReply* robotsResult = bow_api::getRobots(true,true,false);
    if (!robotsResult->localsearcherror().success()) {
        std::cout << "Local search error: " << robotsResult->localsearcherror().description() << std::endl;
    }
    if (!robotsResult->remotesearcherror().success()) {
        std::cout << "Remote search error: " << robotsResult->remotesearcherror().description() << std::endl;
    }

    // print info
    std::cout << "Available Robots:" << std::endl;
    for (int i = 0; i < robotsResult->robots().size(); i++){
        std::cout << i << ":" << robotsResult->robots()[i].name() << std::endl;
    }

    if (robotsResult->robots().size() < _numRobots) {
        std::cout << "Not enough available robots. " << _numRobots << " expected." << std::endl;
        return -1;
    }

    // user input to select robot indices
    std::vector<int> robotIndices(0);
    for (int i = 0; i < _numRobots; i++) {
        std::string prompt = "Select robot " + std::to_string(i+1) + " of " + std::to_string(_numRobots);
        robotIndices.push_back(GetRobotSelection(prompt, robotsResult->robots().size(), robotIndices));
    }

    std::vector<robot::Robot> robotDetails(0);
    for (int i=0;i<robotIndices.size();i++) {
        robotDetails.push_back(robotsResult->robots()[robotIndices[i]]);
    }

    std::vector<bow_robot*> robots(0);
    for (int i=0;i<robotDetails.size();i++) {
        auto robot = new bow_robot(&robotDetails[i]);
        robots.push_back(robot);
    }

    for (auto robot : robots) {
        bow::common::Error* connectResult = robot->connect();
        if (!connectResult->success()) {
            std::cout << "Could not connect with robot: " << robot->details->name() << std::endl;
            return -1;
        }
        for (int j=0;j<channels.size();j++) {
            bow::common::Error* openChannelResult = robot->openChannel(channels[j]);
            if (!openChannelResult->success()) {
                std::cout << "Failed to open " << channels[j] << " channel: " <<openChannelResult->description() << std::endl;
            }
        }
    }

    for (auto robot : robots) {
        if (std::find(channels.begin(), channels.end(), "motor") != channels.end()) {
            threads.emplace_back(motorThread, 20, robot);
        }
        // image thread
        if (std::find(channels.begin(), channels.end(), "vision") != channels.end()) {
            threads.emplace_back(visionThread, 30, robot);
        }
    }

    signal(SIGINT, handle_sigint);
    // Start keyboard listener thread
    threads.emplace_back(keyboardListener);


    for (auto& thread : threads) {
         thread.join();
    }


    // disconnect
    for (auto robot : robots) {
         bow::common::Error* disconnect_result(robot->disconnect());
         if (!disconnect_result->success()) {
             std::cout << disconnect_result->description() << std::endl;
             return -1;
        }
    }

    cv::destroyAllWindows();
    bow_api::stopEngine();

}

