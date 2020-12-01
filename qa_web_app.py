from flask import Flask, request
app = Flask(__name__)


class Agent:
    def __init__(self):
        self._q_history = []
        self._last_q = ''
        self._qud = ''

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
        # TODO Use Chester's code to get an answer.
        return 'Yes. ' + question


agent = Agent()


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
