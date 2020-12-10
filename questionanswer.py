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

    def query(self, query: str, n: int = 10) -> List[str]:
        indices = self.index.get_nns_by_vector(self.model.encode(query), n)
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
    parser.add_argument(
        "text", help="A single text file to be used as the reference material"
    )
    parser.add_argument("question", help="The question that you want answered")
    parser.add_argument(
        "--best", action="store_true", default=False, help="Gives most similar sentence"
    )
    parser.add_argument(
        "--top-sents", action="store_true", default=False, help="Gives best n sentences"
    )
    parser.add_argument(
        "--chunks",
        action="store_true",
        default=False,
        help="Gives best chunks with window around sents",
    )
    parser.add_argument("--n", type=int, default=3, help="Number of chunks to use")
    parser.add_argument("--window-size", type=int, default=25)
    args = parser.parse_args()

    model = SentenceTransformer("bert-base-nli-mean-tokens")
    size = 768  # Sentence embedding size
    search = SimilaritySearch(model, size)

    if not os.path.exists("data/index.ann"):
        print("Index doesn't exist. Creating an index...")
        print("Preprocessing...")
        preprocessor = Preprocessor()
        sentences = preprocessor.preprocess_text(args.text)
        search.build_annoy_index(sentences)
        search.save("data")
    else:
        print("Loading the index")
        search.load("data")

    if args.best:
        result = search.query(args.question, n=1)
    elif args.top_sents:
        result = search.query(args.question, n=args.n)
    elif args.chunks:
        result = search.query_top_chunks(
            args.question, chunks=args.n, window_size=args.window_size
        )
    else:
        raise ValueError("Need to use either best/top-sents/chunks flag")
    for r in result:
        print(r + "\n\n\n")


if __name__ == "__main__":
    main()
