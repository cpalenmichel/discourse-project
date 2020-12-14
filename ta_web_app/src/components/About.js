import React from 'react';

const About = () => {
  return (
    <div className='container card bg-light' id='about'>
      <h2 className='border-bottom padding mx-auto'>About ATAM</h2>
      <p className='blockquote'>
        <strong>Project by</strong> <br /> Katie Krajovic, Chester Palen-Michel,
        Vicky Steger, Julian Fernandez
      </p>
      <hr />
      <p className='text-justify'>
        ATAM is an automated TA who can help you find relevant passages from
        your textbook while you wait for a human TA.
      </p>
      <p className='text-justify'>
        He can also chat about the weather, how things are going, and how his
        weekend was. You can say <code>I have five questions</code> and ATAM
        will prompt you to ask them all in one message, separated by question
        marks.
      </p>
      <p>You can ask him questions like:</p>
      <ul>
        <li>
          <code>How are you?</code>
        </li>
        <li>
          <code>How is the weather?</code>
        </li>
        <li>
          <code>What is your name?</code>
        </li>
        <li>
          <code>What is smoothing?</code>
        </li>
      </ul>
      <p>
        <strong>Note:</strong> If ATAM tells you he's having a network error, it
        means the Python server isn't running.
      </p>
    </div>
  );
};

export default About;
