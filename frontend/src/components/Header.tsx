import React from 'react';

interface HeaderProps {
  userId: string;
  onUserIdChange: (userId: string) => void;
}

const Header: React.FC<HeaderProps> = ({ userId, onUserIdChange }) => {
  return (
    <header className="header">
      <div className="header-content">
        <h1>Smart Chatbot</h1>
        <div className="user-id-section">
          <label htmlFor="userId">User ID:</label>
          <input
            id="userId"
            type="text"
            value={userId}
            onChange={(e) => onUserIdChange(e.target.value)}
            className="user-id-input"
            placeholder="Enter user ID"
          />
        </div>
      </div>
    </header>
  );
};

export default Header;
