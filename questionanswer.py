#! /usr/bin/env python
"""
Sentence similarity search using annoy.

To use preprocess, you need spacy.
python -m spacy download en_core_web_sm
"""
import json
import os
from argparse import ArgumentParser
from typing import List

from annoy import AnnoyIndex
from sentence_transformers import SentenceTransformer
from transformers import pipeline
import spacy


class SimilaritySearch:
    """
    Sentence embedding similarity search using Annoy and sentence embeddings.
    I've been using some of huggingface's sentence embeddings, but
    could adapt to use other embeddings.
    """

    def __init__(self, model, embedding_size=768):
        self.index = AnnoyIndex(embedding_size, "euclidean")
        self.idx_to_sentence = {}
        self.model = model

    def build_annoy_index(self, sentences: List[str], trees: int = 10):
        print(f"Building index for {len(sentences)} sentences")
        for i, sent in enumerate(sentences):
            if i % 100 == 0:
                print(f"{i} sentences complete")
            if len(sent.split()) > 4:
                self.index.add_item(i, self.model.encode(sent))
            self.idx_to_sentence[i] = sent
        # More trees gives better accuracy
        self.index.build(trees)

    def save(self, path: str) -> None:
        self.index.save(os.path.join(path, "index.ann"))
        with open(os.path.join(path, "index.json"), "w", encoding="utf8") as f:
            json.dump(self.idx_to_sentence, f)

    def load(self, path: str) -> None:
        self.index.load(os.path.join(path, "index.ann"))
        with open(os.path.join(path, "index.json"), "r", encoding="utf8") as f:
            self.idx_to_sentence = {int(k): v for k, v in json.load(f).items()}

    def query(self, query: str) -> List[str]:
        indices = self.index.get_nns_by_vector(self.model.encode(query), 10)
        return [self.idx_to_sentence[idx] for idx in indices]

    def query_top_chunks(
        self, query: str, window_size: int = 10, chunks: int = 1
    ) -> List[str]:
        """
        Queries for top n similar sentences then gets all the sentences in the window
        to build chunks of text to return. Useful if you want broader context for the matched
        sentence
        """
        indices = self.index.get_nns_by_vector(self.model.encode(query), chunks)
        chunks = []
        for idx in indices:
            start = idx - window_size
            end = idx + window_size + 1  # Range isn't inclusive with end
            chunks.append(
                " ".join([self.idx_to_sentence[i] for i in range(start, end)])
            )
        return chunks


class QASearch:
    """
    Answers question by finding excerpt from context string using huggingface
    model.
    """

    def __init__(self):
        self.qapipe = pipeline("question-answering")

    def query(self, question: str, context: str) -> str:
        """
        Runs question through the question answering pipeline for hugging face's
        SQuAD model.
        """
        result = self.qapipe({"question": question, "context": context})
        # Can get the offsets if needed, use 'start' and 'end' in result dict
        return result["answer"]


class Preprocessor:
    def __init__(self):
        self.nlp = spacy.load("en_core_web_sm")

    def preprocess_text(self, path: str) -> List[str]:
        """
        Preprocesses a raw text file to use as context for question answering.
        """
        with open(path, "r", encoding="utf8") as f:
            doc = self.nlp(f.read())
        # Throw out short sentence junk
        return [sent.text for sent in doc.sents]


def main():
    parser = ArgumentParser()
    parser.add_argument("text", help="A single text file to be used as the reference material")
    parser.add_argument("question", help="The question that you want answered")
    parser.add_argument("--n", type=int, default=3, help="Number of chunks to use")
    parser.add_argument("--window-size", type=int, default=25)
    args = parser.parse_args()

    model = SentenceTransformer("bert-base-nli-mean-tokens")
    size = 768  # Sentence embedding size
    search = SimilaritySearch(model, size)
    print("Preprocessing...")
    preprocessor = Preprocessor()
    sentences = preprocessor.preprocess_text(args.text)
    if not os.path.exists("data/index.ann"):
        print("Index doesn't exist. Creating an index...")
        search.build_annoy_index(sentences)
        search.save("data")
    else:
        print("Loading the index")
        search.load("data")

    chunks = search.query_top_chunks(
        args.question, chunks=args.n, window_size=args.window_size
    )
    qas = QASearch()
    for chunk in chunks:
        answer = qas.query(args.question, chunk)
        print("Answer: ", answer)


if __name__ == "__main__":
    main()
