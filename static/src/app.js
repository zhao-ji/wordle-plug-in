import React, { Component } from 'react';
import { Suggestions, History, KeyBoard } from "./components";


function App() {
  return (
    <div className="App">
      <header className="App-header">
        Wordle Plug In
      </header>
      <Suggestions />
      <History />
      <KeyBoard />
    </div>
  );
}

export default App;
