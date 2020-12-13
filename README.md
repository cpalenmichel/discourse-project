# COSI233 Project: Automated Teaching Assistant Machine (ATAM)

## Authors

Katie Krajovic
Chester Palen-Michel
Vicky Steger
Julian Fernandez

## Description

Our app consists of two services: a virtual TA dialogue agent named ATAM and a web interface.

Currently, our app only supports running on a local environment. The dialogue agent runs on http://localhost:5000 and the interface runs on http://localhost:3000. Messages sent through the interface are POSTed to the dialogue agent's server, preprocessed, sent to Wit.ai for intent classification, and used to update ATAM's state.

## Usage

Before using, please follow the installation instructions below.

The dialogue agent may be run on its own and interacted through a CLI by first running:

`python qa_web_app.py`

And then starting the interactive CLI from a separate terminal with:

`python test_qa_web_app.py`

You may then send messages and receive responses from ATAM.

To start the React UI and speak with ATAM through the browser, run:

`sh start_atam.sh`

which will start the dialogue agent and the React app simultaneously. Note: This doesn't work on the default Windows command prompt because `&` waits for the first web app to stop running before opening the second. If using the Windows command prompt, open two prompts in the root directory and run on one:

`npm start --prefix ta_web_app`

and run on the other:

`python qa_web_app.py`

## Installation

To install, first create a fresh env and install the requirements.
`pip install -r requirements.txt`


If they are not present already, install Tensorflow, PyTorch, Annoy, and sentence_transformers:
`pip install tensorflow`
`pip install torch`
`pip install annoy`
`pip install sentence_transformers`

You also will likely need to download the spacy model: 
`python -m spacy download en_core_web_sm`

To enable the web app and the full range of responses and usage of the TA application:
Install Node.js from
https://nodejs.org/en/

Install the app's requirements:
`npm install --prefix ta_web_app`

To run the UI by itself:
`npm start --prefix ta_web_app`

This should open a window in your web browser that allows you to converse with the virtual TA.
If the window opens but you always receive the response "Sorry. I'm having trouble talking to my server. It's saying "Error: Network Error"", run the below in a command prompt to finish starting the app.
`python qa_web_app.py`

The required embeddings/models from huggingface should download
themselves the first time you run the script. 

If an index hasn't been build for the text, it will build the index when you first run it. 
That can take a bit of time to sentence split, get embeddings, and 
put them in an index. 
If you need to build a new index, (say you want a different set of sentences to search), just delete the .ann and .json files created in `/data`
