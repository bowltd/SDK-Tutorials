# BOW SDK Tutorials Repository

Welcome to the BOW SDK Tutorials repository. This repository contains tutorial projects demonstrating the use of the BOW SDK across various programming languages and operating systems. The tutorials cover an ever-increasing range of topics.

## Repository Structure

The repository is organized into different steps, each focusing on a specific aspect of using the BOW SDK:

- `Step_0_Dependencies`: Scripts and instructions for setting up necessary dependencies needed for the tutorials based on your operating system and programming language.
- `Step_1_Vision`: Sample applications demonstrating sampling and visualisation of images coming from Vision Modality.
- `Step_2_Locomotion`: Sample applications combining sampling images from the Vision Modality with controlling Locomotion via the Motor Modality to navigate an environment.
  
## Getting Started

### Prerequisites

Ensure you have Git installed on your system to clone the repository. Depending on the programming language you choose, specific tools and environments will be required:

- **C++**: GCC or MSVC, CMake
- **.NET**: .NET SDK
- **Python**: Python 3.7 or higher

### Clone the Repository

```bash
git clone https://github.com/bowltd/SDK-Tutorials.git
cd SDK-Tutorials
```

## Usage

### Step 0: Dependencies

Navigate to the `Step_0_Dependencies` directory to set up the necessary environment for your chosen language and operating system.

#### C++

**Linux**

```bash
cd C++/Linux
./install_opencv_local.sh
```

**Windows**

Coming Soon

### Step 1: Vision Applications

This step contains basic vision applications implemented in C++, .NET, and Python. Navigate to the respective directory for detailed instructions.

#### C++

```bash
cd ../Step_1_Vision/C++
./build.sh
./bow_tutorial_1
```

#### .NET

```bash
cd ../Step_1_Vision/DotNet/Bow_Tutorial_1
dotnet build Bow_Tutorial_1.sln
dotnet run --project Bow_Tutorial_1/Bow_Tutorial_1.csproj
```
In case of libOpenCvSharpExtern.so errors please consult README in Step_1_Vision/DotNet

#### Python

```bash
cd ../Step_1_Vision/Python
pip install -r requirements.txt
python bow_tutorial_1.py
```

## Support

For any issues or queries, please refer to our support guidelines or contact the community support team through the BOW SDK community app store.

## Contributing

We encourage contributions from the community. Please read the CONTRIBUTING.md file for more details on how to submit pull requests or issues.

