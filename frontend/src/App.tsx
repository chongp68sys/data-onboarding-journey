import React from 'react';
import Header from './components/Header';
import FlowCanvas from './components/FlowCanvas';
import './App.css';

function App() {
  return (
    <div className="h-screen flex flex-col bg-gray-50">
      <Header />
      <main className="flex-1 overflow-hidden">
        <FlowCanvas />
      </main>
    </div>
  );
}

export default App;