import React from 'react';

export default function Header() {
  return (
    <header className="bg-slate-900 border-b border-slate-700 px-6 py-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-2">
            <div className="w-8 h-8 bg-gradient-to-r from-purple-600 to-indigo-600 rounded-lg flex items-center justify-center">
              <span className="text-white font-bold text-sm">D</span>
            </div>
            <h1 className="text-xl font-semibold text-white">Data Intelligence Platform</h1>
          </div>
        </div>
        
        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-2">
            <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
            <span className="text-sm text-gray-300">Connected</span>
          </div>
          
          <div className="px-3 py-1.5 bg-purple-900/30 text-purple-300 text-sm font-medium rounded-lg border border-purple-700/50">
            Phase 2 - Flow Canvas
          </div>
        </div>
      </div>
    </header>
  );
}