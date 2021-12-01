import React from 'react';
import Login from './login.js';
import About from './about.js';

function MainPage() {
  return (
    <div className='center'>
      <Login />
      <h1>Al's Advanced ATMs</h1>
      <About />
    </div>
  );
}

export default MainPage;
