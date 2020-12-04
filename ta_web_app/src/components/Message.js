import React from 'react';

const Message = ({ sender, text, justify }) => {
  return (
    <div className={`message text-${justify}`}>
      <span>
        <span className='font-weight-bold'>{sender}</span>: {text}
      </span>
    </div>
  );
};

export default Message;
