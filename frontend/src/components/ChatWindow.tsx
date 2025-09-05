import React, { useState, useRef, useEffect } from 'react';
import MessageList from './MessageList';
import MessageInput from './MessageInput';
import { Message, StreamChunk } from '../types/chat';

interface ChatWindowProps {
  userId: string;
}

const ChatWindow: React.FC<ChatWindowProps> = ({ userId }) => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [connectionStatus, setConnectionStatus] = useState<'connected' | 'connecting' | 'error'>('connected');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom when new messages arrive
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Test backend connection
  useEffect(() => {
    const testConnection = async () => {
      try {
        setConnectionStatus('connecting');
        const response = await fetch('/api/health');
        if (response.ok) {
          setConnectionStatus('connected');
        } else {
          setConnectionStatus('error');
        }
      } catch (error) {
        setConnectionStatus('error');
      }
    };

    testConnection();
  }, []);

  const handleSendMessage = async (content: string) => {
    if (!content.trim() || isLoading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      content: content.trim(),
      sender: 'user',
      timestamp: new Date().toISOString(),
    };

    setMessages(prev => [...prev, userMessage]);
    setIsLoading(true);

    try {
      // Start streaming response
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          user_id: userId,
          message: content.trim(),
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const reader = response.body?.getReader();
      if (!reader) {
        throw new Error('No response body');
      }

      const decoder = new TextDecoder();
      let assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        content: '',
        sender: 'assistant',
        timestamp: new Date().toISOString(),
      };

      setMessages(prev => [...prev, assistantMessage]);

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value);
        const lines = chunk.split('\n');

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const data = line.slice(6);
            if (data === '[DONE]') {
              setIsLoading(false);
              return;
            }

            try {
              const streamChunk: StreamChunk = JSON.parse(data);
              if (streamChunk.content) {
                setMessages(prev => 
                  prev.map(msg => 
                    msg.id === assistantMessage.id 
                      ? { ...msg, content: msg.content + streamChunk.content }
                      : msg
                  )
                );
              }
            } catch (error) {
              console.error('Error parsing stream chunk:', error);
            }
          }
        }
      }
    } catch (error) {
      console.error('Error sending message:', error);
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        content: 'Sorry, I encountered an error. Please try again.',
        sender: 'assistant',
        timestamp: new Date().toISOString(),
      };
      setMessages(prev => [...prev, errorMessage]);
      setConnectionStatus('error');
    } finally {
      setIsLoading(false);
    }
  };

  const getStatusText = () => {
    switch (connectionStatus) {
      case 'connected':
        return 'Connected to backend';
      case 'connecting':
        return 'Connecting...';
      case 'error':
        return 'Connection error - check backend';
      default:
        return 'Unknown status';
    }
  };

  return (
    <div className="chat-window">
      <div className="chat-header">
        <h2>Chat with AI Assistant</h2>
        <p>User: {userId}</p>
      </div>
      
      <MessageList 
        messages={messages} 
        isLoading={isLoading}
      />
      
      <div ref={messagesEndRef} />
      
      <MessageInput 
        onSendMessage={handleSendMessage}
        disabled={isLoading}
      />
      
      <div className="status-indicator">
        <div className={`status-dot ${connectionStatus}`}></div>
        <span>{getStatusText()}</span>
      </div>
    </div>
  );
};

export default ChatWindow;
