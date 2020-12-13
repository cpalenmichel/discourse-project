import React from 'react';

const Message = ({ sender, text, justify }) => {
  return (
    <div className={`messages text-${justify}`}>
      <span className='message'>
        <span className='font-weight-bold'>{sender}</span>: {text}
      </span>
    </div>
  );
};

export default Message;
