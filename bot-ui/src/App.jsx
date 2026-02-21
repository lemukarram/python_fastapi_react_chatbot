import React, { useState, useEffect, useRef } from 'react';
import { Send, User, Bot, Loader2 } from 'lucide-react';

// Standard JS object for styles to avoid framework dependencies
const styles = {
  container: {
    display: 'flex',
    flexDirection: 'column',
    height: '100vh',
    backgroundColor: '#f9fafb',
    color: '#111827',
    fontFamily: 'system-ui, -apple-system, sans-serif'
  },
  header: {
    backgroundColor: '#ffffff',
    borderBottom: '1px solid #e5e7eb',
    padding: '16px 24px',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    boxShadow: '0 1px 2px 0 rgba(0, 0, 0, 0.05)',
    flexShrink: 0
  },
  logoSection: {
    display: 'flex',
    alignItems: 'center',
    gap: '8px'
  },
  iconContainer: {
    backgroundColor: '#2563eb',
    padding: '8px',
    borderRadius: '8px',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center'
  },
  title: {
    fontWeight: '700',
    fontSize: '20px',
    margin: 0,
    color: '#1f2937'
  },
  main: {
    flex: 1,
    overflowY: 'auto',
    padding: '24px'
  },
  chatContainer: {
    maxWidth: '768px',
    margin: '0 auto',
    display: 'flex',
    flexDirection: 'column',
    gap: '24px'
  },
  messageRow: {
    display: 'flex',
    gap: '16px'
  },
  messageRowUser: {
    flexDirection: 'row-reverse'
  },
  avatar: {
    width: '40px',
    height: '40px',
    borderRadius: '50%',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    flexShrink: 0,
    boxShadow: '0 1px 2px 0 rgba(0, 0, 0, 0.05)'
  },
  bubble: {
    maxWidth: '85%',
    padding: '12px 16px',
    borderRadius: '16px',
    fontSize: '15px',
    lineHeight: '1.5',
    boxShadow: '0 1px 2px 0 rgba(0, 0, 0, 0.05)',
    whiteSpace: 'pre-wrap'
  },
  footer: {
    backgroundColor: '#ffffff',
    borderTop: '1px solid #e5e7eb',
    padding: '24px',
    flexShrink: 0
  },
  inputWrapper: {
    maxWidth: '768px',
    margin: '0 auto',
    position: 'relative'
  },
  input: {
    width: '100%',
    backgroundColor: '#f3f4f6',
    border: 'none',
    borderRadius: '16px',
    padding: '16px 60px 16px 16px',
    fontSize: '16px',
    outline: 'none',
    boxSizing: 'border-box'
  },
  sendButton: {
    position: 'absolute',
    right: '0px',
    top: '31%',
    transform: 'translateY(-50%)',
    backgroundColor: '#2563eb',
    color: 'white',
    border: 'none',
    borderRadius: '14px',
    padding: '10px',
    cursor: 'pointer',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    transition: 'background-color 0.2s'
  }
};

export default function App() {
  const [messages, setMessages] = useState([
    { role: 'bot', content: 'Hi there! I am your AI assistant. I can remember our conversation now. How can I help you?' }
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId, setSessionId] = useState('');
  const messagesEndRef = useRef(null);

  // Generate a simple session ID when the app loads
  useEffect(() => {
    const newSessionId = 'session-' + Math.random().toString(36).substr(2, 9);
    setSessionId(newSessionId);
  }, []);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  const handleSendMessage = async (e) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    const userMessage = input.trim();
    setInput('');
    setMessages(prev => [...prev, { role: 'user', content: userMessage }]);
    setIsLoading(true);

    try {
      const response = await fetch('http://127.0.0.1:8000/api/v1/message', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          message: userMessage,
          session_id: sessionId // We are now sending the session_id
        }),
      });

      const data = await response.json();
      setMessages(prev => [...prev, { 
        role: 'bot', 
        content: data.reply || "I am sorry, I encountered an issue." 
      }]);
    } catch (error) {
      setMessages(prev => [...prev, { 
        role: 'bot', 
        content: "Error: Connection to the backend failed. Please check if the FastAPI server is running." 
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div style={styles.container}>
      {/* Header */}
      <header style={styles.header}>
        <div style={styles.logoSection}>
          <div style={styles.iconContainer}>
            <Bot size={24} color="white" />
          </div>
          <h1 style={styles.title}>AI Chat Assistant</h1>
        </div>
        <div style={{ fontSize: '10px', color: '#9ca3af', backgroundColor: '#f3f4f6', padding: '4px 8px', borderRadius: '4px', textAlign: 'right' }}>
          ID: {sessionId}<br/>
          v1.1 (Memory Enabled)
        </div>
      </header>

      {/* Chat Area */}
      <main style={styles.main}>
        <div style={styles.chatContainer}>
          {messages.map((msg, index) => (
            <div 
              key={index} 
              style={{
                ...styles.messageRow,
                ...(msg.role === 'user' ? styles.messageRowUser : {})
              }}
            >
              <div style={{
                ...styles.avatar,
                backgroundColor: msg.role === 'user' ? '#2563eb' : '#ffffff',
                color: msg.role === 'user' ? 'white' : '#2563eb',
                border: msg.role === 'user' ? 'none' : '1px solid #e5e7eb'
              }}>
                {msg.role === 'user' ? <User size={20} /> : <Bot size={20} />}
              </div>
              
              <div style={{
                ...styles.bubble,
                backgroundColor: msg.role === 'user' ? '#2563eb' : '#ffffff',
                color: msg.role === 'user' ? 'white' : '#1f2937',
                border: msg.role === 'user' ? 'none' : '1px solid #f3f4f6',
                borderTopLeftRadius: msg.role === 'bot' ? '0' : '16px',
                borderTopRightRadius: msg.role === 'user' ? '0' : '16px',
              }}>
                {msg.content}
              </div>
            </div>
          ))}
          
          {isLoading && (
            <div style={styles.messageRow}>
              <div style={{...styles.avatar, backgroundColor: 'white', border: '1px solid #e5e7eb', color: '#2563eb'}}>
                <Bot size={20} />
              </div>
              <div style={{...styles.bubble, backgroundColor: 'white', border: '1px solid #f3f4f6', display: 'flex', alignItems: 'center', gap: '8px'}}>
                <Loader2 size={18} className="animate-spin" style={{ color: '#2563eb' }} />
                <span style={{ color: '#9ca3af', fontSize: '14px' }}>Thinking...</span>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>
      </main>

      {/* Input Area */}
      <footer style={styles.footer}>
        <div style={styles.inputWrapper}>
          <form onSubmit={handleSendMessage}>
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Type your message..."
              style={styles.input}
              disabled={isLoading}
            />
            <button
              type="submit"
              disabled={!input.trim() || isLoading}
              style={{
                ...styles.sendButton,
                backgroundColor: (!input.trim() || isLoading) ? '#d1d5db' : '#2563eb'
              }}
            >
              <Send size={20} />
            </button>
          </form>
          <div style={{ textAlign: 'center', marginTop: '16px', fontSize: '10px', color: '#9ca3af', textTransform: 'uppercase', letterSpacing: '1px', fontWeight: 'bold' }}>
            Powered by Gemini 2.5 . Developed by Mukarram
          </div>
        </div>
      </footer>
      
      {/* Animation Styles */}
      <style>{`
        @keyframes spin {
          from { transform: rotate(0deg); }
          to { transform: rotate(360deg); }
        }
        .animate-spin {
          animation: spin 1s linear infinite;
        }
      `}</style>
    </div>
  );
}