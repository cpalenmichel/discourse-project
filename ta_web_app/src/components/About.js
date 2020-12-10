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
        weekend was.
      </p>
      <p>
        You can ask him questions like (
        <strong>todo: replace questions with ones that work really well</strong>
        ):
        <ul>
          <li>
            <code>What is an HMM?</code>
          </li>
          <li>
            <code>What is a syntax tree?</code>
          </li>
          <li>
            <code>How many parts of speech tags are there?</code>
          </li>
        </ul>
      </p>
    </div>
  );
};

export default About;
