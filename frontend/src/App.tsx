import React, { useState } from 'react';
import './App.css';
import ChatWindow from './components/ChatWindow';
import Header from './components/Header';
import MemoryManager from './components/MemoryManager';

function App() {
  const [userId, setUserId] = useState<string>('user123');
  const [activeTab, setActiveTab] = useState<'chat' | 'memory'>('chat');

  return (
    <div className="App">
      <Header userId={userId} onUserIdChange={setUserId} />
      <main className="main-content">
        <div className="container">
          {/* Tab Navigation */}
          <div className="tab-navigation">
            <button 
              className={`tab-button ${activeTab === 'chat' ? 'active' : ''}`}
              onClick={() => setActiveTab('chat')}
            >
              Chat
            </button>
            <button 
              className={`tab-button ${activeTab === 'memory' ? 'active' : ''}`}
              onClick={() => setActiveTab('memory')}
            >
              Memory
            </button>
          </div>

          {/* Tab Content */}
          {activeTab === 'chat' && <ChatWindow userId={userId} />}
          {activeTab === 'memory' && <MemoryManager userId={userId} />}
        </div>
      </main>
    </div>
  );
}

export default App;
