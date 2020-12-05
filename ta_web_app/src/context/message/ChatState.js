import React, { useReducer } from 'react';
import chatReducer from './chatReducer';
import { ADD_MESSAGE, CLEAR_MESSAGES } from '../types';
import ChatContext from './chatContext';
import axios from 'axios';

const ChatState = (props) => {
  const initialState = {
    messages: [],
  };

  const [state, dispatch] = useReducer(chatReducer, initialState);

  const respondTo = async (message) => {
    const { text } = message;

    const res = await axios.post(
      'http://localhost:5000/ask',
      {
        question: text,
      },
      {
        headers: { 'Access-Control-Allow-Origin': '*' },
      }
    );

    dispatch({
      type: ADD_MESSAGE,
      payload: {
        text: res.data,
        sender: 'ATAM',
      },
    });
  };

  const addMessage = async (message) => {
    console.log(`adding ${message}`);
    dispatch({
      type: ADD_MESSAGE,
      payload: message,
    });

    await respondTo(message);
  };

  const clearMessages = () => {
    dispatch({
      type: CLEAR_MESSAGES,
    });
  };

  return (
    <ChatContext.Provider
      value={{
        messages: state.messages,
        addMessage,
        clearMessages,
      }}
    >
      {props.children}
    </ChatContext.Provider>
  );
};

export default ChatState;
