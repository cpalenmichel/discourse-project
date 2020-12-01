# discourse-project
Part of group project for COSI233 (virtual TA)


Create a fresh env and install the requirements. (I think this is all you need but haven't tried it out). 
`pip install -r requirements`
You also will likely need to download the spacy model 
`python -m spacy download en_core_web_sm`

The required embeddings/models from huggingface should download
themselves the first time you run the script. 

If an index hasn't been build for the text, it will build the index when you first run it. 
That can take a bit of time to sentence split, get embeddings, and 
put them in an index. 
If you need to build a new index, (say you want a different set of sentences to search), just delete the .ann and .json files created in `/data`

Sample call:
`python questionanswer.py data/JurafskyandMartin3.txt "What is a language model?" --n 3 --window-size 30`
