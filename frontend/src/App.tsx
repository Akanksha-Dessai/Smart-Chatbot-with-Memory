import React, { useState } from 'react';
import './App.css';
import ChatWindow from './components/ChatWindow';
import Header from './components/Header';

function App() {
  const [userId, setUserId] = useState<string>('user123');

  return (
    <div className="App">
      <Header userId={userId} onUserIdChange={setUserId} />
      <main className="main-content">
        <div className="container">
          <ChatWindow userId={userId} />
        </div>
      </main>
    </div>
  );
}

export default App;
