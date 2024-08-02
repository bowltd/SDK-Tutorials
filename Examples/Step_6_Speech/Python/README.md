# BOW Tutorial: Speech: Python 

Welcome to the BOW Tutorial on Speech (Streaming Text) with Python. Check out our running guide below.

## Prerequisites

- A [Virtual Environment](https://docs.bow.software/tutorials/tutorial_resources/python/venv) with the requirements installed from `requirements.txt`

- One of the [inference methods mentioned in the tutorial](https://docs.bow.software/tutorials/tutorial_1/step_6#generating-the-tts-voice) ready to use.

- A BOW Standard Subscription or higher to simulate a robot to connect to. (Remember to use our Free Trial!)

## Environment Variables

Before proceeding, ensure that you have copied the example environment file and set the variables according to how you want to generate the speech. To do this, run in your terminal
```bash
cp .env.example .env
```
and then edit the .env file and set the variables accordingly. 


### Testing the TTS

Depending on your TTS method, you can run the corresponding test script to test things are working correctly before trying it out on a robot.

### Willow IS

To test Willow, make sure the inference server is running, and you have a virtual environment setup with the deps installed and then run:
```bash
python test_willow.py
```

### OpenAI

To test OpenAI, make sure you have an account, an API key, and you have a virtual environment setup with the deps installed and then run:
```bash
python test_openai.py
```

### Running the Tutorial

To run the main tutorial ensure that you have copied over the `.env.example` file and set the environment variables as mentioned earlier. Then in your virtual environment run:

```bash
python main.py
```

### Stopping the Tutorial

To stop the program execution use the key combination `ctrl + c` in your terminal.