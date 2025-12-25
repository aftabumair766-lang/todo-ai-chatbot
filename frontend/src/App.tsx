/**
 * Todo AI Chatbot - React Frontend
 *
 * Natural language task management with OpenAI GPT-4
 * Constitution Compliance: Principle II (Stateless - conversation stored in database)
 */

import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import './App.css';
import { Language, getTranslation, detectLanguage } from './translations';

// API Configuration
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

interface Message {
  role: 'user' | 'assistant';
  content: string;
}

interface User {
  id: number;
  email: string;
  username: string;
}

function App() {
  // Language state with localStorage persistence
  const [language, setLanguage] = useState<Language>(() => {
    const saved = localStorage.getItem('chatbot-language');
    return (saved as Language) || detectLanguage();
  });

  // Auth state
  const [authToken, setAuthToken] = useState<string>(() => {
    return localStorage.getItem('auth-token') || '';
  });
  const [isAuthenticated, setIsAuthenticated] = useState(() => {
    return !!localStorage.getItem('auth-token');
  });
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  const [user, setUser] = useState<User | null>(() => {
    const savedUser = localStorage.getItem('user');
    return savedUser ? JSON.parse(savedUser) : null;
  });
  const [authMode, setAuthMode] = useState<'login' | 'register'>('login');

  // Login/Register form state
  const [email, setEmail] = useState('');
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');

  // Chat state
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputMessage, setInputMessage] = useState('');
  const [conversationId, setConversationId] = useState<number | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string>('');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Get current translations
  const t = getTranslation(language);

  // Save language preference
  useEffect(() => {
    localStorage.setItem('chatbot-language', language);
  }, [language]);

  // Handle language change
  const handleLanguageChange = (newLang: Language) => {
    setLanguage(newLang);
  };

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Handle Login
  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');

    try {
      const response = await axios.post(`${API_URL}/api/auth/login`, {
        email: email,
        password: password
      });

      const { access_token, user: userData } = response.data;

      // Save token and user to state and localStorage
      setAuthToken(access_token);
      setUser(userData);
      setIsAuthenticated(true);
      localStorage.setItem('auth-token', access_token);
      localStorage.setItem('user', JSON.stringify(userData));

      // Reset form
      setEmail('');
      setPassword('');
      setError('');
    } catch (err: any) {
      console.error('Login failed:', err);
      const errorMessage = err.response?.data?.detail || 'Login failed';
      setError(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  // Handle Registration
  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');

    try {
      const response = await axios.post(`${API_URL}/api/auth/register`, {
        email: email,
        username: username,
        password: password
      });

      const { access_token, user: userData } = response.data;

      // Save token and user to state and localStorage
      setAuthToken(access_token);
      setUser(userData);
      setIsAuthenticated(true);
      localStorage.setItem('auth-token', access_token);
      localStorage.setItem('user', JSON.stringify(userData));

      // Reset form
      setEmail('');
      setUsername('');
      setPassword('');
      setError('');
    } catch (err: any) {
      console.error('Registration failed:', err);
      const errorMessage = err.response?.data?.detail || 'Registration failed';
      setError(errorMessage);
    } finally {
      setIsLoading(false);
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
        { role: 'assistant', content: `${t.errorPrefix} ${errorMessage}` }
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  // Logout
  const handleLogout = () => {
    setIsAuthenticated(false);
    setAuthToken('');
    setUser(null);
    setMessages([]);
    setConversationId(null);
    setError('');
    localStorage.removeItem('auth-token');
    localStorage.removeItem('user');
  };

  // Authentication Screen
  if (!isAuthenticated) {
    return (
      <div className="auth-container">
        <div className="auth-box">
          {/* Language Selector on Auth Screen */}
          <div className="language-selector-auth">
            <select
              value={language}
              onChange={(e) => handleLanguageChange(e.target.value as Language)}
              className="language-dropdown"
            >
              <option value="en">{t.languageEnglish}</option>
              <option value="ur">{t.languageUrdu}</option>
              <option value="zh">{t.languageChinese}</option>
            </select>
          </div>

          <h1>{t.appTitle}</h1>
          <p>{t.appSubtitle}</p>

          {/* Auth Mode Tabs */}
          <div className="auth-tabs">
            <button
              className={`auth-tab ${authMode === 'login' ? 'active' : ''}`}
              onClick={() => { setAuthMode('login'); setError(''); }}
            >
              {t.loginButton}
            </button>
            <button
              className={`auth-tab ${authMode === 'register' ? 'active' : ''}`}
              onClick={() => { setAuthMode('register'); setError(''); }}
            >
              Register
            </button>
          </div>

          {/* Login Form */}
          {authMode === 'login' && (
            <form onSubmit={handleLogin}>
              <input
                type="email"
                placeholder="Email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="auth-input"
                required
                autoFocus
              />
              <input
                type="password"
                placeholder="Password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="auth-input"
                required
              />
              <button type="submit" className="auth-button" disabled={isLoading}>
                {isLoading ? 'Logging in...' : t.loginButton}
              </button>
            </form>
          )}

          {/* Register Form */}
          {authMode === 'register' && (
            <form onSubmit={handleRegister}>
              <input
                type="email"
                placeholder="Email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="auth-input"
                required
                autoFocus
              />
              <input
                type="text"
                placeholder="Username (3-100 chars)"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                className="auth-input"
                minLength={3}
                maxLength={100}
                required
              />
              <input
                type="password"
                placeholder="Password (8-72 chars)"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="auth-input"
                minLength={8}
                maxLength={72}
                required
              />
              <button type="submit" className="auth-button" disabled={isLoading}>
                {isLoading ? 'Creating account...' : 'Create Account'}
              </button>
            </form>
          )}

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
        <div className="header-left">
          <h1>{t.appTitle}</h1>
          <p>{t.appSubtitle}</p>
        </div>
        <div className="header-right">
          {/* Language Selector */}
          <div className="language-selector">
            <label>{t.selectLanguage}:</label>
            <select
              value={language}
              onChange={(e) => handleLanguageChange(e.target.value as Language)}
              className="language-dropdown"
            >
              <option value="en">🇬🇧 {t.languageEnglish}</option>
              <option value="ur">🇵🇰 {t.languageUrdu}</option>
              <option value="zh">🇨🇳 {t.languageChinese}</option>
            </select>
          </div>
          <button onClick={handleLogout} className="logout-button">
            {t.logoutButton}
          </button>
        </div>
      </div>

      {/* Chat Container */}
      <div className="chat-container">
        {/* Messages */}
        <div className="messages-container">
          {messages.length === 0 ? (
            <div className="welcome-message">
              <h2>{t.welcomeTitle}</h2>
              <p>{t.welcomeDescription}</p>
              <ul>
                <li>{t.exampleAdd}</li>
                <li>{t.exampleList}</li>
                <li>{t.exampleComplete}</li>
                <li>{t.exampleDelete}</li>
                <li>{t.exampleUpdate}</li>
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
            placeholder={t.inputPlaceholder}
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
            {t.sendButton}
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
