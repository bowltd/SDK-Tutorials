# Using the BOW Python SDK with BOW Tutorial 2

To use the BOW Python SDK we recommend using a [Python Virtual Environment](https://docs.python.org/3/library/venv.html) to manage your python dependencies.

## Setting up a Virtual Environment

### Prerequisites

Ensure you have Python installed on your system. You can check if Python is installed by running:

```bash
python --version
````

If Python is not installed, download and install it from the [official Python website](https://www.python.org/downloads/).

### Creating a Virtual Environment

To get started with using a virtual environment, run the following commands in your Terminal Emulator of choice.

### Creating a Virtual Environment

1. Open your Terminal Emulator of choice.


2. Navigate to this tutorial directory

```bash
cd /path/to/this/tutorial/Python
```

3. Create a virtual environment by running:

```bash
python -m venv .venv
```

This will create a directory named `.venv` containing the virtual environment.

### Activating the Virtual Environment

- On **Windows**, run:

```sh
.venv\Scripts\activate
```

- On **macOS** and **Linux**, run:

```sh
source .venv/bin/activate
```

After activation, your terminal prompt should change to indicate that you are now using the virtual environment.

### Installing Dependencies

Once the virtual environment is activated, you can install the required dependencies by using `pip`. To install the dependencies for this tutorial, run the following command in your activated virtual environment terminal:

```bash
pip install -r requirements.txt
```

### Deactivating the Virtual Environment

To deactivate the virtual environment and return to the global Python environment, simply run:

```bash
deactivate
```


## Running the Tutorial

### Prerequisites

With the dependencies installed, you can now run the example tutorial, to run the program ensure the following:

- You have the BOW Hub running
- You have the BOW-Webots simulator running
- You have a Terminal Emulator open with the Virtual Environment activated.

### Running

To run the tutorial, simply run in the aforementioned terminal:
```bash
python bow_tutorial_2.py
```

This will launch a preview of the robot's camera and listen for keyboard inputs to remotely control the robot in the simulator.

### Keyboard Controls

To move the robot, you can use the following input table.

| Key | Action        | Description                                  |
|-----|---------------|----------------------------------------------|
| W   | Move Forward  | Moves the robot forward                      |
| A   | Turn Left     | Turns the robot to the left                  |
| S   | Move Backward | Moves the robot backward                     |
| D   | Turn Right    | Turns the robot to the right                 |
| E   | Strafe Right  | Moves the robot to the right without turning |
| Q   | Strafe Left   | Moves the robot to the left without turning  |

### Stopping

To cancel the program's execution, you can either close the camera preview window, or you can press `Ctrl + C` in the running terminal.