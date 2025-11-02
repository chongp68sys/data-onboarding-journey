import React from 'react';
import { ReactFlowProvider } from '@xyflow/react';
import Header from './components/Header';
import FlowCanvas from './components/FlowCanvas';
import NodePalette from './components/NodePalette';
import './App.css';

function App() {
  return (
    <div className="h-screen w-screen flex flex-col bg-slate-900 overflow-hidden">
      <Header />
      <main className="flex-1 min-h-0 flex">
        <NodePalette />
        <div className="flex-1 min-h-0">
          <ReactFlowProvider>
            <FlowCanvas />
          </ReactFlowProvider>
        </div>
      </main>
    </div>
  );
}

export default App;