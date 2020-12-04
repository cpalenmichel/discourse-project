'''
This module provides functions to interact with ATAM through Wit.AI.

Example usage from another file:
    from qa_wit import wit_bot, get_wit_response_intents

    response = wit_bot.send('hello')

    intents = get_wit_response_intents(response)
    print(intents)

This will produce output like:
    [{'id': '470742860992984', 'name': 'greeting', 'confidence': .998}, ...]
'''

from wit import Wit


def get_wit_response_text(wit_response):
    '''
    Convenience function to get text out of Wit.ai response dictionary.

    This is just the message that was sent to Wit.AI.
    '''
    return wit_response['text']


def get_wit_response_intents(wit_response):
    '''
    Convenience function to get intents out of Wit.ai response dictionary.
    '''
    return wit_response['intents']


def get_wit_response_entities(wit_response):
    '''
    Convenience function to get entities out of Wit.ai response dictionary.
    '''
    return wit_response['entities']


def get_wit_response_traits(wit_response):
    '''
    Convenience function to get traits out of Wit.ai response dictionary.
    '''
    return wit_response['traits']


class WitBot:
    def __init__(self, client_access_token):
        self._wit = Wit(client_access_token)

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
        return response


_atam_client_access_token = 'WVYVUAYCY4BVTT5JYA6TAWLYCZQXHEHH'

wit_bot = WitBot(_atam_client_access_token)
