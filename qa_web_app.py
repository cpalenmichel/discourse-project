'''
Web app that receives questions in JSON objects of the form:
{
    "question": "What is an HMM?"
}

by a POST request to '/ask'.

The app sends back an answer as a string.
'''
from wit import Wit
import random
import json
from flask import Flask, request
from flask_cors import CORS
app = Flask(__name__)
CORS(app)


class Agent:
    QUESTION_INTENT = 'question'
    EXIT_INTENT = 'exit'

    def __init__(self, atam_client_access_token, debug=True):
        # Set debug mode to indicate whether to log full response from wit.ai
        self._debug = debug
        self._q_history = []
        self._last_q = ''
        self._qud = ''
        self._wit = Wit(atam_client_access_token)
        # Provides a dictionary from intentions to hardcoded responses.
        with open('responses.json', encoding='utf8') as fp:
            self._hardcoded_responses = json.load(fp)

    def __str__(self):
        return json.dumps({
            'q_history': self._q_history,
            'last_q': self._last_q,
            'qud': self._qud,
        })

    @staticmethod
    def get_most_likely_intent(wit_response):
        try:
            return wit_response['intents'][0]
        except IndexError:
            # If no intent can be identified, return the fallback intent.
            return {
                'id': -1,
                'name': 'fallback',
                'confidence': 1.0,
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
        intent_name = intent['name']
        intent_confidence = intent['confidence']

        # Log the full response from wit.ai if in debug mode.
        if self._debug:
            print('Agent State:')
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
            # TODO Student asked a question. Do a search for a relevant answer.
            pass

        '''
        ...TODO return whatever other message we think is right,
        either by hardcoding more responses or by performing a text
        search.
        '''

        return 'Yes. ' + question


agent = Agent(atam_client_access_token='WVYVUAYCY4BVTT5JYA6TAWLYCZQXHEHH')


def preprocess(text, qud):
    '''TODO Remove stopwords, punctuation, stem/lemmatize, rephrase, etc.
        Maybe use qud to add evocative words that will give better results...
    '''
    return text


def get_new_qud(q_history, curr_qud, question):
    '''TODO Given a dialogue history, the current QUD, and a new question, return the predicted new QUD.'''

    return curr_qud


def get_answer(question):
    '''Return an answer, given a question. Preprocess question and update state as necessary.'''
    preprocessed_question = preprocess(question, agent.qud())

    # Update state.
    agent.add_to_history(preprocessed_question)
    new_qud = get_new_qud(agent.q_history(),
                          agent.qud(), preprocessed_question)
    agent.update_qud(new_qud)

    # Answer the question.
    answer = agent.answer(preprocessed_question)

    return answer


@app.route('/ask', methods=['POST'])
def ask():
    '''Expects a posted JSON object with a field called 'question' that contains user's question.'''
    data = request.get_json()
    question = data['question']
    answer = get_answer(question)
    return answer


def main(debug=False, port=5000):
    '''Runs web app on specified port. If debug is true, the server will restart whenever the file is saved.'''
    app.run(debug=debug, port=port)


if __name__ == "__main__":
    main(debug=True, port=5000)
