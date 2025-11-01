import React, { useState, useEffect } from 'react';
import { healthCheck } from '../services/api';

export default function Header() {
  const [isConnected, setIsConnected] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const checkConnection = async () => {
      try {
        await healthCheck();
        setIsConnected(true);
      } catch (error) {
        setIsConnected(false);
      } finally {
        setIsLoading(false);
      }
    };

    checkConnection();
    // Check connection every 30 seconds
    const interval = setInterval(checkConnection, 30000);
    
    return () => clearInterval(interval);
  }, []);

  return (
    <header className="bg-white shadow-sm border-b border-gray-200 px-6 py-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <h1 className="text-2xl font-bold text-gray-900">
            Data Onboarding Journey
          </h1>
          <span className="px-3 py-1 bg-blue-100 text-blue-800 text-sm font-medium rounded-full">
            Phase 1 - Core Infrastructure
          </span>
        </div>
        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-2 text-sm text-gray-600">
            {isLoading ? (
              <>
                <div className="w-2 h-2 bg-yellow-400 rounded-full animate-pulse"></div>
                <span>Checking Backend...</span>
              </>
            ) : isConnected ? (
              <>
                <div className="w-2 h-2 bg-green-400 rounded-full"></div>
                <span>Backend Connected</span>
              </>
            ) : (
              <>
                <div className="w-2 h-2 bg-red-400 rounded-full"></div>
                <span>Backend Disconnected</span>
              </>
            )}
          </div>
          <button 
            className={`px-4 py-2 rounded-md font-medium transition-colors ${
              isConnected 
                ? 'bg-blue-600 hover:bg-blue-700 text-white' 
                : 'bg-gray-300 text-gray-500 cursor-not-allowed'
            }`}
            disabled={!isConnected}
          >
            Save Workflow
          </button>
        </div>
      </div>
    </header>
  );
}