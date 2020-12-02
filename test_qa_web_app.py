'''
Script to test qa_web_app.py. Sends a POST request to the server and prints the response.

To run this, first start the server by running qa_web_app.py. Then:

python test_qa_web_app.py [-h] [--question QUESTION] [--port PORT]

Both arguments are optional and default to:
    question - What is an HMM?
    port - 5000 (this must be the same as the port that the server is running on)
'''

import argparse
import requests


def main(question, port):
    headers = {'Content-Type': 'application/json'}
    data = {
        'question': question,
    }

    response = requests.post(
        f'http://localhost:{port}/ask', headers=headers, json=data)

    print(response.text)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--question', help='Question to send to dialog server.', required=False, type=str,
                        default='What is an HMM?')
    parser.add_argument(
        '--port', help='Port which dialog server is running on. Defaults to 5000.', required=False, type=int,
        default=5000)

    args = parser.parse_args()

    main(args.question, args.port)
