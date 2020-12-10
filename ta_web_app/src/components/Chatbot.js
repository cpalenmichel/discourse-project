import React, { useContext, useRef, useEffect } from 'react';
import { Button, Form, InputGroup } from 'react-bootstrap';
import Message from './Message';
import ChatContext from '../context/message/chatContext';
import nextId from 'react-id-generator';

const Chatbot = () => {
  const messagesEndRef = useRef(null);
  const chatContext = useContext(ChatContext);

  const { addMessage, messages } = chatContext;

  useEffect(() => {
    messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
  });

  const onSubmit = (e) => {
    e.preventDefault();
    let textbox = e.target.messageBox;
    const message = textbox.value;
    textbox.value = '';

    if (message === '') {
      return;
    }

    addMessage({
      sender: 'You',
      text: message,
    });
  };

  return (
    <>
      <div className='container card bg-light' id='chatbot'>
        <h2 className='border-bottom padding mx-auto'>Talk with me!</h2>
        <div className='container card text-center'>
          <div className='chat-display text-left'>
            {messages.map((msg) => {
              const key = nextId();
              return (
                <Message
                  key={key}
                  sender={msg.sender}
                  text={msg.text}
                  justify={msg.sender === 'You' ? 'right' : 'left'}
                ></Message>
              );
            })}
            <div ref={messagesEndRef} />
          </div>
        </div>
        <Form onSubmit={onSubmit}>
          <InputGroup>
            <Form.Control
              type='text'
              name='messageBox'
              placeholder='Send a message'
              autoComplete='off'
            />
            <InputGroup.Append>
              <Button
                variant='primary'
                type='submit'
                style={{ color: 'white' }}
              >
                Submit
              </Button>
            </InputGroup.Append>
          </InputGroup>
        </Form>
      </div>
    </>
  );
};

export default Chatbot;
