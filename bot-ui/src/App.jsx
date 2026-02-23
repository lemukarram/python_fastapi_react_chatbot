import React, { useState, useEffect, useRef } from 'react';

const API_BASE = "http://127.0.0.1:8000";

export default function App() {
  // State management
  const [token, setToken] = useState(localStorage.getItem('token') || '');
  const [userEmail, setUserEmail] = useState(localStorage.getItem('userEmail') || '');
  const [view, setView] = useState(token ? 'chat' : 'login');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const chatEndRef = useRef(null);

  // Auto-scroll to bottom of chat
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  // Auth: Register
  const handleRegister = async (e) => {
    e.preventDefault();
    setError('');
    try {
      const res = await fetch(`${API_BASE}/auth/register`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password })
      });
      if (res.ok) {
        alert("Registration successful. Please login.");
        setView('login');
      } else {
        const data = await res.json();
        setError(data.detail || "Registration failed.");
      }
    } catch (err) {
      setError("Server connection failed.");
    }
  };

  // Auth: Login (FastAPI Users uses Form Data for OAuth2)
  const handleLogin = async (e) => {
    e.preventDefault();
    setError('');
    const formData = new URLSearchParams();
    formData.append('username', email);
    formData.append('password', password);

    try {
      const res = await fetch(`${API_BASE}/auth/jwt/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: formData
      });
      const data = await res.json();
      if (res.ok) {
        setToken(data.access_token);
        setUserEmail(email);
        localStorage.setItem('token', data.access_token);
        localStorage.setItem('userEmail', email);
        setView('chat');
      } else {
        setError(data.detail || "Invalid email or password.");
      }
    } catch (err) {
      setError("Connection error.");
    }
  };

  // Auth: Logout
  const handleLogout = async () => {
    try {
      await fetch(`${API_BASE}/auth/jwt/logout`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` }
      });
    } catch (e) {}
    setToken('');
    setUserEmail('');
    localStorage.removeItem('token');
    localStorage.removeItem('userEmail');
    setView('login');
    setMessages([]);
  };

  // Chat: Send Message
  const sendMessage = async (e) => {
    e.preventDefault();
    if (!input.trim()) return;

    const userMsg = { role: 'user', content: input };
    setMessages(prev => [...prev, userMsg]);
    setInput('');
    setLoading(true);

    try {
      const res = await fetch(`${API_BASE}/api/v1/message`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ message: input })
      });
      const data = await res.json();
      if (res.ok) {
        setMessages(prev => [...prev, { role: 'bot', content: data.reply }]);
      } else {
        setMessages(prev => [...prev, { role: 'bot', content: "Sorry, I am having trouble connecting." }]);
      }
    } catch (err) {
      setMessages(prev => [...prev, { role: 'bot', content: "Connection to server lost." }]);
    } finally {
      setLoading(false);
    }
  };

  // Styles
  const styles = {
    container: { fontFamily: 'Arial, sans-serif', maxWidth: '600px', margin: '40px auto', padding: '20px', border: '1px solid #ddd', borderRadius: '12px', backgroundColor: '#f9f9f9' },
    header: { display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' },
    inputGroup: { marginBottom: '15px' },
    label: { display: 'block', marginBottom: '5px', fontWeight: 'bold' },
    input: { width: '100%', padding: '10px', boxSizing: 'border-box', borderRadius: '6px', border: '1px solid #ccc' },
    button: { width: '100%', padding: '12px', backgroundColor: '#007bff', color: 'white', border: 'none', borderRadius: '6px', cursor: 'pointer', fontWeight: 'bold' },
    chatBox: { height: '400px', overflowY: 'auto', border: '1px solid #ddd', padding: '15px', borderRadius: '8px', backgroundColor: 'white', marginBottom: '15px' },
    msgUser: { textAlign: 'right', margin: '10px 0' },
    msgBot: { textAlign: 'left', margin: '10px 0' },
    bubbleUser: { backgroundColor: '#007bff', color: 'white', padding: '8px 12px', borderRadius: '15px 15px 0 15px', display: 'inline-block' },
    bubbleBot: { backgroundColor: '#e9ecef', color: '#333', padding: '8px 12px', borderRadius: '15px 15px 15px 0', display: 'inline-block' },
    error: { color: 'red', marginBottom: '10px', fontSize: '14px' },
    link: { color: '#007bff', cursor: 'pointer', textDecoration: 'underline' }
  };

  return (
    <div style={styles.container}>
      <div style={styles.header}>
        <h2>{view === 'chat' ? 'AI Assistant' : 'Welcome'}</h2>
        {token && <button onClick={handleLogout} style={{ ...styles.button, width: 'auto', padding: '5px 10px', backgroundColor: '#dc3545' }}>Logout</button>}
      </div>

      {view === 'login' && (
        <form onSubmit={handleLogin}>
          <h3>Login</h3>
          {error && <div style={styles.error}>{error}</div>}
          <div style={styles.inputGroup}>
            <label style={styles.label}>Email</label>
            <input type="email" style={styles.input} value={email} onChange={e => setEmail(e.target.value)} required />
          </div>
          <div style={styles.inputGroup}>
            <label style={styles.label}>Password</label>
            <input type="password" style={styles.input} value={password} onChange={e => setPassword(e.target.value)} required />
          </div>
          <button type="submit" style={styles.button}>Login</button>
          <p>New here? <span style={styles.link} onClick={() => setView('register')}>Register now</span></p>
        </form>
      )}

      {view === 'register' && (
        <form onSubmit={handleRegister}>
          <h3>Create Account</h3>
          {error && <div style={styles.error}>{error}</div>}
          <div style={styles.inputGroup}>
            <label style={styles.label}>Email</label>
            <input type="email" style={styles.input} value={email} onChange={e => setEmail(e.target.value)} required />
          </div>
          <div style={styles.inputGroup}>
            <label style={styles.label}>Password</label>
            <input type="password" style={styles.input} value={password} onChange={e => setPassword(e.target.value)} required />
          </div>
          <button type="submit" style={styles.button}>Register</button>
          <p>Already have an account? <span style={styles.link} onClick={() => setView('login')}>Login</span></p>
        </form>
      )}

      {view === 'chat' && (
        <div>
          <p style={{ fontSize: '12px', color: '#666' }}>Logged in as: {userEmail}</p>
          <div style={styles.chatBox}>
            {messages.map((m, i) => (
              <div key={i} style={m.role === 'user' ? styles.msgUser : styles.msgBot}>
                <div style={m.role === 'user' ? styles.bubbleUser : styles.bubbleBot}>
                  {m.content}
                </div>
              </div>
            ))}
            {loading && <div style={styles.msgBot}><div style={styles.bubbleBot}>Typing...</div></div>}
            <div ref={chatEndRef} />
          </div>
          <form onSubmit={sendMessage} style={{ display: 'flex', gap: '10px' }}>
            <input 
              style={styles.input} 
              placeholder="Ask anything..." 
              value={input} 
              onChange={e => setInput(e.target.value)} 
            />
            <button type="submit" style={{ ...styles.button, width: '80px' }}>Send</button>
          </form>
        </div>
      )}
    </div>
  );
}