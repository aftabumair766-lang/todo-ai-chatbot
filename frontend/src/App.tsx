/**
 * Todo AI Chatbot - React Frontend
 *
 * Natural language task management with OpenAI GPT-4
 * Constitution Compliance: Principle II (Stateless - conversation stored in database)
 */

import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import './App.css';

// API Configuration
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

interface Message {
  role: 'user' | 'assistant';
  content: string;
}

function App() {
  const [authToken, setAuthToken] = useState<string>('');
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputMessage, setInputMessage] = useState('');
  const [conversationId, setConversationId] = useState<number | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string>('');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Handle authentication
  const handleLogin = (e: React.FormEvent) => {
    e.preventDefault();
    if (authToken.trim()) {
      setIsAuthenticated(true);
      setError('');
    }
  };

  // Send message to backend
  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!inputMessage.trim() || isLoading) return;

    const userMessage = inputMessage.trim();
    setInputMessage('');
    setIsLoading(true);
    setError('');

    // Add user message to UI immediately
    setMessages(prev => [...prev, { role: 'user', content: userMessage }]);

    try {
      const response = await axios.post(
        `${API_URL}/api/chat`,
        {
          message: userMessage,
          conversation_id: conversationId
        },
        {
          headers: {
            'Authorization': `Bearer ${authToken}`,
            'Content-Type': 'application/json'
          }
        }
      );

      // Update conversation ID if this is the first message
      if (!conversationId && response.data.conversation_id) {
        setConversationId(response.data.conversation_id);
      }

      // Add assistant response to UI
      setMessages(prev => [
        ...prev,
        { role: 'assistant', content: response.data.message }
      ]);

    } catch (err: any) {
      console.error('Failed to send message:', err);
      const errorMessage = err.response?.data?.detail || err.message || 'Failed to send message';
      setError(errorMessage);

      // Add error message to chat
      setMessages(prev => [
        ...prev,
        { role: 'assistant', content: `⚠️ Error: ${errorMessage}` }
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  // Logout
  const handleLogout = () => {
    setIsAuthenticated(false);
    setAuthToken('');
    setMessages([]);
    setConversationId(null);
    setError('');
  };

  // Authentication Screen
  if (!isAuthenticated) {
    return (
      <div className="auth-container">
        <div className="auth-box">
          <h1>🤖 Todo AI Chatbot</h1>
          <p>Manage your tasks with natural language</p>
          <form onSubmit={handleLogin}>
            <input
              type="text"
              placeholder="Enter auth token (use 'test' for demo)"
              value={authToken}
              onChange={(e) => setAuthToken(e.target.value)}
              className="auth-input"
              autoFocus
            />
            <button type="submit" className="auth-button">
              Login
            </button>
          </form>
          {error && <div className="error-message">{error}</div>}
        </div>
      </div>
    );
  }

  // Chat Screen
  return (
    <div className="app-container">
      {/* Header */}
      <div className="app-header">
        <h1>🤖 Todo AI Chatbot</h1>
        <p>Natural language task management</p>
        <button onClick={handleLogout} className="logout-button">
          Logout
        </button>
      </div>

      {/* Chat Container */}
      <div className="chat-container">
        {/* Messages */}
        <div className="messages-container">
          {messages.length === 0 ? (
            <div className="welcome-message">
              <h2>👋 Welcome!</h2>
              <p>I can help you manage your tasks using natural language.</p>
              <ul>
                <li>"Add a task to buy groceries"</li>
                <li>"Show me all my tasks"</li>
                <li>"Mark task 1 as complete"</li>
                <li>"Delete task 2"</li>
                <li>"Update task 3 to call mom at 6pm"</li>
              </ul>
            </div>
          ) : (
            messages.map((msg, index) => (
              <div key={index} className={`message message-${msg.role}`}>
                <div className="message-avatar">
                  {msg.role === 'user' ? '👤' : '🤖'}
                </div>
                <div className="message-content">
                  <div className="message-text">{msg.content}</div>
                </div>
              </div>
            ))
          )}
          {isLoading && (
            <div className="message message-assistant">
              <div className="message-avatar">🤖</div>
              <div className="message-content">
                <div className="typing-indicator">
                  <span></span>
                  <span></span>
                  <span></span>
                </div>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Input */}
        <form onSubmit={handleSendMessage} className="input-container">
          <input
            type="text"
            placeholder="Type your message... (e.g., 'Add a task to buy groceries')"
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            disabled={isLoading}
            className="message-input"
            autoFocus
          />
          <button
            type="submit"
            disabled={isLoading || !inputMessage.trim()}
            className="send-button"
          >
            Send
          </button>
        </form>

        {/* Error Display */}
        {error && (
          <div className="error-banner">
            {error}
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
