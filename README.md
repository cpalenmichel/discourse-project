# discourse-project
Part of group project for COSI233 (virtual TA)

To enable the question-answering portion of the code:
Create a fresh env and install the requirements.
`pip install -r requirements.txt`

If they are not present already, install Tensorflow, PyTorch, Annoy, and sentence_transformers
`pip install tensorflow`
`pip install torch`
`pip install annoy`
`pip install sentence_transformers`

You also will likely need to download the spacy model 
`python -m spacy download en_core_web_sm`


To enable the web app and the full range of responses and usage of the TA application:
Install Node.js from
https://nodejs.org/en/

Install the app's requirements
`npm install`

To start the node, run the below in the command prompt.
`start_atam.sh`

This should open a window in your web browser that allows you to converse with the virtual TA.
If the window opens but you always receive the response "Sorry. I'm having trouble talking to my server. It's saying "Error: Network Error"", run the below in a command prompt to finish starting the app.
`python qa_web_app.py`

The required embeddings/models from huggingface should download
themselves the first time you run the script. 

If an index hasn't been build for the text, it will build the index when you first run it. 
That can take a bit of time to sentence split, get embeddings, and 
put them in an index. 
If you need to build a new index, (say you want a different set of sentences to search), just delete the .ann and .json files created in `/data`