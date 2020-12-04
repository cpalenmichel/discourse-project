'''
This module provides functions to interact with ATAM through Wit.AI.

Example usage from another file:
    from qa_wit import wit_bot, get_wit_response_intents

    response = wit_bot.send('hello')

    print(response)

This will produce output like:
    Hello!
'''

from wit import Wit
import random


def get_most_likely_intent(wit_response):
    return wit_response['intents'][0]


class WitBot:
    GREETING_INTENT = 'greeting'

    def __init__(self, client_access_token):
        self._wit = Wit(client_access_token)
        # Provides a dictionary from intentions to hardcoded responses.
        self._responses = {
            self.GREETING_INTENT: ['Hello!', 'Hi!', 'Hello.', 'Hi.']
        }

    def send(self, message):
        '''
        Send a message to the Wit app and return the response.

        Responses are dictionaries of the form:
            {
                'text': ...
                'intents': [{'id': ..., 
                    'name': ..., 
                    'confidence': ...},
                    ...], 
                'entities': {...}, 
                'traits': {...}
            }
        '''
        response = self._wit.message(message)
        intent = get_most_likely_intent(response)

        intent_name = intent['name']
        intent_confidence = intent['confidence']

        # Return hardcoded responses.
        if intent_name == self.GREETING_INTENT:
            return random.choice(self._responses[self.GREETING_INTENT])

        '''
        ...TODO return whatever other message we think is right,
        either by hardcoding more responses or by performing a text
        search.
        '''

        return "I just don't know what to say."


_atam_client_access_token = 'WVYVUAYCY4BVTT5JYA6TAWLYCZQXHEHH'

wit_bot = WitBot(_atam_client_access_token)
