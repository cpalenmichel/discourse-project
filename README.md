# discourse-project
Part of group project for COSI233 (virtual TA)


TODO pip install requirements
TODO setup spacy

The required embeddings/models from huggingface should download
themselves the first time you run the script. 

If an index hasn't been build for the text, it will build the index. 
That can take a bit of time to sentence split, get embeddings, and 
put them in an index. 

Sample call:
`python questionanswer.py data/JurafskyandMartin3.txt "What is a language model?" --n 3 --window-size 30`
