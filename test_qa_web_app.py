'''
Script to test qa_web_app.py. Starts a REPL where messages are sent to ATAM.

To run this, first start the server by running qa_web_app.py. Then:

python test_qa_web_app.py [-h] [--port PORT]

Port argument are optional and defaults to 5000.
    question - What is an HMM?
'''

import argparse
import requests

HEADERS = {'Content-Type': 'application/json'}
PROMPT = '> '


def repl(port):
    print('Type a message and press enter to send to ATAM. Send `exit` to quit.')
    try:
        text = input(PROMPT)
    except:
        exit(0)

    while text.lower() != 'exit':
        data = {
            'question': text,
        }

        response = requests.post(
            f'http://localhost:{port}/ask', headers=HEADERS, json=data)

        print(response.text)
        try:
            text = input(PROMPT)
        except:
            exit(0)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--port', help='Port which dialog server is running on. Defaults to 5000.', required=False, type=int,
        default=5000)

    args = parser.parse_args()

    repl(args.port)
