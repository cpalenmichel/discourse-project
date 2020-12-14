"""
Web app that receives questions in JSON objects of the form:
{
    "question": "What is an HMM?"
}

by a POST request to '/ask'.

The app sends back an answer as a string.
"""
import os
from typing import Optional, Dict, List
from collections import defaultdict

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
    MULTI_INTENT = "multi_question"
    EXIT_INTENT = "exit"
    YES_INTENT = "yes"
    NO_INTENT = "no"
    YES_NO_INTENTS = {YES_INTENT, NO_INTENT}
    FALLBACK_INTENT = "fallback"
    GRADES = "grades"
    ASSIGNMENT = "assignment"
    # Discourse States:
    # Track whether we're in special states in conversation.
    # QA follow up, after we've just answered a question, seeing if should try another.
    QA_FOLLOW_UP = "QA-ing"
    INTRO = "intro"
    NEUTRAL = "neutral"
    MULTI = "multi_question"
    FIRST_OF_MULTI = "first_of_multi"
    PENDING_FOLLOW_UP = "pending_follow_up"

    def __init__(self, atam_client_access_token, debug=True):
        self.reset_state()
        self._wit = Wit(atam_client_access_token)
        # Set debug mode to indicate whether to log full response from wit.ai
        self._debug = debug

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

    def reset_state(self):
        """Reset dialog state. Called on initialization and when the user types 'exit' or otherwise indicates exit intent"""
        self._q_history = []
        self._last_q = ""
        self._last_intent = ""
        # store the current question and the general topic as a tuple
        self._qud = ("", "")

        # store pending questions to be discussed
        self.pending_Qs = []
        # track whatever state the agent is currently in
        self.current_state = self.INTRO
        self.responses = []
        # track inputs stored by intent
        self.log = defaultdict(list)

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

    def last_intent(self):
        return self._last_intent

    def qud(self):
        return self._qud

    def update_qud(self, new_qud):
        self._qud = new_qud

    def pending_Qs(self):
        return self.pending_Qs

    def answer(self, question):
        # use dialogue state and QUD and QA to produce good answers.

        # Send the preprocessed question to wit.ai
        response = self._wit.message(question)

        # Get the most likely intent.
        intent = Agent.get_most_likely_intent(response)
        intent_name = intent["name"]
        intent_confidence = intent["confidence"]

        # If the question has anaphora and is either a question or unknown intent, add our best guess at anaphora resolution and reprocess the question
        if (intent_name in (self.QUESTION_INTENT, self.FALLBACK_INTENT)) and (self.anaphora_detection(question)):
            question = self.anaphora_resolution(question)
            response = self._wit.message(question)

            intent = Agent.get_most_likely_intent(response)
            intent_name = intent["name"]
            intent_confidence = intent["confidence"]
        
        # log the question, storing based on intent
        self.log[intent_name].append(question)

        if intent_name == self.MULTI_INTENT:
            self.current_state = self.MULTI
            return "Ok! Please list all your questions separated by '?'"

        if intent_name not in self.YES_NO_INTENTS:
            self._last_q = question
            self._last_intent = intent_name

            # Update the QUD
            new_qud = self.get_new_qud(question, response)
            self.update_qud(new_qud)

        # Log the full response from wit.ai if in debug mode.
        if self._debug:
            print("Agent State:")
            print(self)
            print(response)

        # if it's a yes and we're waiting on follow up for pending Qs --- OR --- if this is the first of many pending Qs
        if intent_name == self.YES_INTENT and self.current_state == self.PENDING_FOLLOW_UP or self.current_state == self.FIRST_OF_MULTI:
            # run the relevant Q through wit
            response = self._wit.message(self.pending_Qs[0])
            intent = Agent.get_most_likely_intent(response)
            intent_name = intent["name"]
            
            # if it's not the first pop, because it won't be popped later
            if self.current_state != self.FIRST_OF_MULTI:
                self.log[intent_name].append(self.pending_Qs[0])
                
                if intent_name not in self.YES_NO_INTENTS:
                    self._last_q = self.pending_Qs[0]
                    self._last_intent = intent_name
        
                    # Update the QUD
                    new_qud = self.get_new_qud(self.pending_Qs[0], response)
                    self.update_qud(new_qud)
            
                self.pending_Qs.pop(0)
            # if it's a regular old question, send to the QA procedure
            if intent_name == self.QUESTION_INTENT:
                return self.first_question_response_attempt(response)
            # if it's not a regular QA
            else:
                # if it's grades and there are more to come
                if intent_name == self.GRADES and len(self.pending_Qs) != 0:
                    # do the popping now
                    if self.current_state == self.FIRST_OF_MULTI:
                        self.pending_Qs.pop(0)
                    # respond and prompt for next Q
                    self.current_state = self.PENDING_FOLLOW_UP
                    return "Sorry, I can't help you with grades. You'll have to talk with the TA. Your next question was \"" + self.pending_Qs[0] + "\"\n Would you like me to talk about that?"
                # if it's assignments and there are more to come
                elif intent_name == self.ASSIGNMENT and len(self.pending_Qs) != 0: 
                    # do the popping now
                    if self.current_state == self.FIRST_OF_MULTI:
                        self.pending_Qs.pop(0)
                    # respond and prompt for next Q
                    self.current_state = self.PENDING_FOLLOW_UP
                    return "Sorry, I can't help you with the assignment. You'll have to talk with the TA. Your next question was \"" + self.pending_Qs[0] + "\"\n Would you like me to talk about that?"
                # otherwise, use the hard coded responses
                else: 
                    # do the popping now
                    if self.current_state == self.FIRST_OF_MULTI:
                        self.pending_Qs.pop(0)
                        
                    if len(self.pending_Qs)==0:
                        self.current_state = self.NEUTRAL
                    
                    # return the hard coded response
                    return random.choice(self._hardcoded_responses[intent_name])
        # get hardcoded response, make log if exit
        elif intent_name in self._hardcoded_responses:
            if intent_name == self.EXIT_INTENT:
                self.log_conversation()
                self.reset_state()
            return random.choice(self._hardcoded_responses[intent_name])
        # if they responded no to wanting to discuss a pending Q 
        elif intent_name == self.NO_INTENT and self.current_state == self.PENDING_FOLLOW_UP:
            return "OK! What's next?"
        elif intent_name == self.QUESTION_INTENT:
            return self.first_question_response_attempt(response)
        elif intent_name in self.YES_NO_INTENTS and self.current_state == self.QA_FOLLOW_UP:
            return self.qa_follow_up(intent_name)

        """
        ...TODO return whatever other message we think is right,
        either by hardcoding more responses or by performing a text
        search.
        """

        return "Yes. " + question

    def first_question_response_attempt(self, response):
        """Student asked a question. Do a search for a relevant answer."""
        entities: Optional[Dict] = response.get("entities", None)
        self.responses.extend(self.lookup_reference_answer(entities))
        if self.current_state == self.FIRST_OF_MULTI:
            if self.responses:
                self.current_state = self.QA_FOLLOW_UP
                return f"Your first question was \"" + self.pending_Qs.pop(0) + f"\"\n I found this in the course materials: \"\n {self.responses.pop(0)}\n\n\" Is that helpful?"
            # if we couldn't return a chunk from the reference material, bail
            if len(self.pending_Qs) != 0:
                self.current_state = self.PENDING_FOLLOW_UP
                return "Sorry, I couldn't seem to find a good answer for your first question. Your next question was \"" + self.pending_Qs[0] + "\"\n Would you like me to talk about that?"
            return "Sorry, I couldn't seem to find a good answer for your first question."
        else:
            if self.responses:
                self.current_state = self.QA_FOLLOW_UP
                return f"I found this in the course materials: \"\n {self.responses.pop(0)}\n\n\" Is that helpful?"
            # if we couldn't return a chunk from the reference material, bail
            return "Sorry, I couldn't seem to find a good answer for your question."

    def qa_follow_up(self, intent_name):
        """
        When in QA follow up state, tries to pop potential responses.
        """
        if intent_name == self.NO_INTENT and self.responses:
            return f"I found this in the course materials: \"\n {self.responses.pop(0)}\n\n\" Is that helpful?"
        elif intent_name == self.NO_INTENT and not self.responses:
            self.current_state = self.NEUTRAL

            # Log that we failed to answerethe question
            self.log[self.last_intent()][len(self.log[self.last_intent()]) - 1] = self.log[self.last_intent()
                                                                                           ][len(self.log[self.last_intent()]) - 1] + "\t\t(I didn't answer this one)"
            # if there are pending Qs, prompt
            if len(self.pending_Qs) != 0:
                self.current_state = self.PENDING_FOLLOW_UP
                return "Sorry, I couldn't seem to find a good answer for your question. Your next question was \"" + self.pending_Qs[0] + "\"\n Would you like me to talk about that?"
            self.current_state = self.NEUTRAL
            return "Sorry I couldn't answer that. I'm still learning. What else can I do for you?"
        else:
            # Clear responses, since question answered
            self.responses = []
            self.current_state = self.NEUTRAL

            # Log that we believe we answered the question
            self.log[self.last_intent()][len(self.log[self.last_intent()]) - 1] = self.log[self.last_intent()
                                                                                           ][len(self.log[self.last_intent()]) - 1] + "\t\t(I think I answered this one)"
            # if there are pendign Qs, prompt
            if len(self.pending_Qs) != 0:
                self.current_state = self.PENDING_FOLLOW_UP
                return "great, glad it helped!. Your next question was \"" + self.pending_Qs[0] + "\"\n Would you like me to talk about that?"
            self.current_state = self.NEUTRAL
            return "great, glad it helped!"

    def lookup_reference_answer(self, entities: Optional[Dict]) -> Optional[List[str]]:
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
                # Use 3 tries to get useful info for now
                return self.search.query_top_chunks(search_query, window_size=3, chunks=3)
        return None

    def log_conversation(self):
        file = open("./conversation_summary.txt", "w+")
        conversation = self.log.items()
        for key, value in conversation:
            if (key not in ("yes", "no", "exit", "fallback")):
                file.write(key.upper() + ":\n")
                for entry in value:
                    file.write("\t" + entry + "\n")
                file.write("\n")
        file.close()

    def get_new_qud(self, question, response):
        """Given the most recent question and the Wit.ai analysis of it, return the predicted new QUD."""
        # Only determine topic overlap for questions
        if self.last_intent() == self.QUESTION_INTENT:
            old_qud = self.qud()
            old_topic = set(old_qud[1].split())

            new_topic = set(
                response["entities"]["wit$search_query:search_query"][0]["value"].split())
            overlap = old_topic.intersection(new_topic)

            # if the previous and current question topics overlap in some way, treat that overlap as the overall topic
            if len(overlap) > 0:
                topic = " ".join(overlap)
            else:
                topic = response["entities"]["wit$search_query:search_query"][0]["value"]
        else:
            topic = self.last_intent()

        return (question, topic)

    def anaphora_detection(self, text):
        """Given the text of a question, return whether or not it requires entity resolution"""
        pronouns = {"it", "they", "them", "their",
                    "itself", "themselves", "themself"}
        words = set(text.split())

        return len(pronouns.intersection(words)) > 0

    def anaphora_resolution(self, text):
        """Given the text of a question, return the question with the addition of the current topic"""
        return text + " " + self.qud()[1]


agent = Agent(atam_client_access_token="WVYVUAYCY4BVTT5JYA6TAWLYCZQXHEHH")


def preprocess(text, qud):
    """
    Preprocess text before sending to agent.
    """
    text = text.strip()

    # remove extra punct
    punct = ['!', ',', '.', ':', ';']
    text = [c for c in text if not c in punct]
    text = "".join(text)

    if len(text) > 1: 
        # delete last ? if there is a final one
        if text[-1] == '?':
            text = text[:-1]
        # split input on ?
        questions = text.split('?')
        # if there is more than one question, add all to pending Qs
        if len(questions) > 1:
            for q in questions:
                q = q.strip()
                agent.pending_Qs.append(q)
            agent.current_state = agent.FIRST_OF_MULTI
            
            return agent.pending_Qs[0]
        else:
            return text
    else:
        return "!"


def get_answer(question):
    """Return an answer, given a question. Preprocess question and update state as necessary."""
    preprocessed_question = preprocess(question, agent.qud())
    # Update state.
    agent.add_to_history(preprocessed_question)

    # Answer the question.
    answer = agent.answer(preprocessed_question)

    return answer


@app.route("/ask", methods=["POST"])
def ask():
    """Expects a posted JSON object with a field called 'question' that contains user's question."""
    data = request.get_json()
    question = data.get("question")
    if not question:
        return "Error: Bad JSON. Needs question field."

    answer = get_answer(question)
    return answer


def main(debug=False, port=5000):
    """Runs web app on specified port. If debug is true, the server will restart whenever the file is saved."""
    app.run(debug=debug, port=port)


if __name__ == "__main__":
    main(debug=True, port=5000)
