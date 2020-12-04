import React from 'react';
import './App.css';
import './custom.scss';
import About from './components/About';
import Chatbot from './components/Chatbot';
import Navbar from './components/layout/Navbar';
import ChatState from './context/message/ChatState';

function App() {
  return (
    <div className='App'>
      <ChatState>
        <Navbar />
        <div className='wrapper bg-light'>
          <About />
          <Chatbot />
        </div>
      </ChatState>
    </div>
  );
}

export default App;
