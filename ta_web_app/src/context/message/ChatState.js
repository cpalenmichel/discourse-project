import React, { useReducer } from 'react';
import chatReducer from './chatReducer';
import { ADD_MESSAGE, CLEAR_MESSAGES } from '../types';
import ChatContext from './chatContext';

const ChatState = (props) => {
  const initialState = {
    messages: [],
  };

  const [state, dispatch] = useReducer(chatReducer, initialState);

  const addMessage = (message) => {
    console.log(`adding ${message}`);
    dispatch({
      type: ADD_MESSAGE,
      payload: message,
    });
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
