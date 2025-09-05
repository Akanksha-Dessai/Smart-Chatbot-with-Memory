import React from 'react';
import Message from './Message';
import TypingIndicator from './TypingIndicator';
import { Message as MessageType } from '../types/chat';

interface MessageListProps {
  messages: MessageType[];
  isLoading: boolean;
}

const MessageList: React.FC<MessageListProps> = ({ messages, isLoading }) => {
  return (
    <div className="message-list">
      {messages.map((message) => (
        <Message key={message.id} message={message} />
      ))}
      {isLoading && <TypingIndicator />}
    </div>
  );
};

export default MessageList;
