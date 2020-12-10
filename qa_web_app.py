"""
Web app that receives questions in JSON objects of the form:
{
    "question": "What is an HMM?"
}

by a POST request to '/ask'.

The app sends back an answer as a string.
"""
import os
from typing import Optional, Dict

from sentence_transformers import SentenceTransformer
from wit import Wit
import random
import json
from flask import Flask, request
from flask_cors import CORS

from questionanswer import SimilaritySearch, Preprocessor

app = Flask(__name__)
CORS(app)


REFERENCE_TEXT_PATH = "data/cleaned_jurafsky_and_martin.txt"


class Agent:
    QUESTION_INTENT = "question"
    EXIT_INTENT = "exit"

    def __init__(self, atam_client_access_token, debug=True):
        # Set debug mode to indicate whether to log full response from wit.ai
        self._debug = debug
        self._q_history = []
        self._last_q = ""
        self._qud = ""
        self._wit = Wit(atam_client_access_token)
        # Provides a dictionary from intentions to hardcoded responses.
        with open("responses.json", encoding="utf8") as fp:
            self._hardcoded_responses = json.load(fp)

        # Similarity stuff
        model = SentenceTransformer("bert-base-nli-mean-tokens")
        size = 768  # Sentence embedding size, probs shouldn't hardcode it but *shrug*
        self.search = SimilaritySearch(model, size)

        if not os.path.exists("data/index.ann"):
            print("Index doesn't exist. Creating an index...")
            print("Preprocessing...")
            preprocessor = Preprocessor()
            sentences = preprocessor.preprocess_text(REFERENCE_TEXT_PATH)
            self.search.build_annoy_index(sentences)
            self.search.save("data")
        else:
            print("Loading the index")
            self.search.load("data")

    def __str__(self):
        return json.dumps(
            {
                "q_history": self._q_history,
                "last_q": self._last_q,
                "qud": self._qud,
            }
        )

    @staticmethod
    def get_most_likely_intent(wit_response):
        try:
            return wit_response["intents"][0]
        except IndexError:
            # If no intent can be identified, return the fallback intent.
            return {
                "id": -1,
                "name": "fallback",
                "confidence": 1.0,
            }

    def q_history(self):
        return self._q_history

    def add_to_history(self, question):
        self._q_history.append(question)

    def last_q(self):
        return self._last_q

    def qud(self):
        return self._qud

    def update_qud(self, new_qud):
        self._qud = new_qud

    def answer(self, question):
        # TODO use dialogue state and QUD and QA to produce good answers.

        # Send the preprocessed question to wit.ai
        response = self._wit.message(question)

        # Get the most likely intent.
        intent = Agent.get_most_likely_intent(response)
        intent_name = intent["name"]
        intent_confidence = intent["confidence"]

        # Log the full response from wit.ai if in debug mode.
        if self._debug:
            print("Agent State:")
            print(self)
            print(response)

        self._last_q = question

        # Return hardcoded responses.
        if intent_name in self._hardcoded_responses:
            return random.choice(self._hardcoded_responses[intent_name])
        elif intent_name == self.EXIT_INTENT:
            # TODO handle quitting behavior
            pass
        elif intent_name == self.QUESTION_INTENT:
            # Student asked a question. Do a search for a relevant answer.
            entities: Optional[Dict] = response.get("entities", None)
            response = self.lookup_reference_answer(entities)
            if response:
                return f"I found this in the course materials: \"\n {response}\n\n\" Is that helpful?"
            # if we couldn't return a chunk from the reference material, bail
            return "Sorry, I couldn't seem to find a good answer for your question."

        """
        ...TODO return whatever other message we think is right,
        either by hardcoding more responses or by performing a text
        search.
        """

        return "Yes. " + question

    def lookup_reference_answer(self, entities: Optional[Dict]) -> Optional[str]:
        """
        Grab the search_query entities identified by WIT for a question intent, and do
        a lookup for chunks from the text.
        """
        if entities is not None:
            search_queries = entities.get("wit$search_query:search_query", [])
            print("Search Query: ", search_queries)
            # Not the best way to grab all the search terms, but maybe good enough
            search_query = " ".join([d["value"] for d in search_queries])
            if search_query:
                # Assume best chunk is the one to use for now
                return self.search.query_top_chunks(search_query, window_size=3)[0]
        return None


agent = Agent(atam_client_access_token="WVYVUAYCY4BVTT5JYA6TAWLYCZQXHEHH")


def preprocess(text, qud):
    """TODO Remove stopwords, punctuation, stem/lemmatize, rephrase, etc.
    Maybe use qud to add evocative words that will give better results...
    """
    return text


def get_new_qud(q_history, curr_qud, question):
    """TODO Given a dialogue history, the current QUD, and a new question, return the predicted new QUD."""

    return curr_qud


def get_answer(question):
    """Return an answer, given a question. Preprocess question and update state as necessary."""
    preprocessed_question = preprocess(question, agent.qud())

    # Update state.
    agent.add_to_history(preprocessed_question)
    new_qud = get_new_qud(agent.q_history(), agent.qud(), preprocessed_question)
    agent.update_qud(new_qud)

    # Answer the question.
    answer = agent.answer(preprocessed_question)

    return answer


@app.route("/ask", methods=["POST"])
def ask():
    """Expects a posted JSON object with a field called 'question' that contains user's question."""
    data = request.get_json()
    question = data["question"]
    answer = get_answer(question)
    return answer


def main(debug=False, port=5000):
    """Runs web app on specified port. If debug is true, the server will restart whenever the file is saved."""
    app.run(debug=debug, port=port)


if __name__ == "__main__":
    main(debug=True, port=5000)
