import React, { useState, useEffect, useRef } from 'react';

const API_BASE = "http://127.0.0.1:8000";

export default function App() {
  const [token, setToken] = useState(localStorage.getItem('token') || '');
  const [userEmail, setUserEmail] = useState(localStorage.getItem('userEmail') || '');
  const [view, setView] = useState(token ? 'chat' : 'login');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const chatEndRef = useRef(null);

  // Load history when entering chat view
  useEffect(() => {
    if (token && view === 'chat') {
      fetchHistory();
    }
  }, [token, view]);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const fetchHistory = async () => {
    try {
      const res = await fetch(`${API_BASE}/api/v1/history`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (res.ok) {
        const data = await res.json();
        setMessages(data);
      }
    } catch (err) {
      console.error("Failed to load history.");
    }
  };

  const handleRegister = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');
    try {
      const res = await fetch(`${API_BASE}/auth/register`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password })
      });
      if (res.ok) {
        setSuccess("Registration successful. You can now login.");
        setView('login');
        setPassword(''); // Clear password for security
      } else {
        const data = await res.json();
        setError(data.detail || "Registration failed. Please try again.");
      }
    } catch (err) {
      setError("Cannot connect to server.");
    }
  };

  const handleLogin = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');
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
        setError("Invalid email or password.");
      }
    } catch (err) {
      setError("Connection error.");
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('userEmail');
    setToken('');
    setUserEmail('');
    setMessages([]);
    setView('login');
  };

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
      }
    } catch (err) {
      setMessages(prev => [...prev, { role: 'bot', content: "Error connecting to server." }]);
    } finally {
      setLoading(false);
    }
  };

  const styles = {
    container: { fontFamily: 'sans-serif', maxWidth: '600px', margin: '20px auto', padding: '20px', backgroundColor: '#fff', border: '1px solid #eee', borderRadius: '12px' },
    chatBox: { height: '400px', overflowY: 'auto', marginBottom: '15px', padding: '10px', backgroundColor: '#fdfdfd', border: '1px solid #f0f0f0', borderRadius: '8px' },
    user: { backgroundColor: '#007bff', color: '#ffffff', float: 'right', clear: 'both', borderRadius: '8px', maxWidth: '80%', padding: '8px 12px', margin: '8px 5px' },
    bot: { backgroundColor: '#f1f1f1', color: '#333', float: 'left', clear: 'both', borderRadius: '8px', maxWidth: '80%', padding: '8px 12px', margin: '8px 5px' },
    input: { width: '80%', padding: '10px', borderRadius: '6px', border: '1px solid #ccc', boxSizing: 'border-box' },
    btn: { padding: '10px 20px', borderRadius: '6px', backgroundColor: '#007bff', color: 'white', border: 'none', cursor: 'pointer' },
    toggleLink: { color: '#007bff', cursor: 'pointer', textDecoration: 'underline', marginTop: '15px', display: 'block', fontSize: '14px' }
  };

  return (
    <div style={styles.container}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px' }}>
        <h2 style={{ margin: 0 }}>RSG Tender BOT</h2>
        {token && <button onClick={handleLogout} style={{ ...styles.btn, backgroundColor: '#dc3545' }}>Logout</button>}
      </div>

      {success && <p style={{ color: 'green', backgroundColor: '#eaffea', padding: '10px', borderRadius: '6px' }}>{success}</p>}
      {error && <p style={{ color: 'red', backgroundColor: '#ffeaea', padding: '10px', borderRadius: '6px' }}>{error}</p>}

      {view === 'login' && (
        <form onSubmit={handleLogin}>
          <h3>Login</h3>
          <input type="email" placeholder="Email" style={{ ...styles.input, width: '100%', marginBottom: '10px' }} value={email} onChange={e => setEmail(e.target.value)} required />
          <input type="password" placeholder="Password" style={{ ...styles.input, width: '100%', marginBottom: '10px' }} value={password} onChange={e => setPassword(e.target.value)} required />
          <button type="submit" style={{ ...styles.btn, width: '100%' }}>Login</button>
          <span style={styles.toggleLink} onClick={() => { setView('register'); setError(''); }}>Don't have an account? Register here.</span>
        </form>
      )}

      {view === 'register' && (
        <form onSubmit={handleRegister}>
          <h3>Create Account</h3>
          <input type="email" placeholder="Email" style={{ ...styles.input, width: '100%', marginBottom: '10px' }} value={email} onChange={e => setEmail(e.target.value)} required />
          <input type="password" placeholder="Password" style={{ ...styles.input, width: '100%', marginBottom: '10px' }} value={password} onChange={e => setPassword(e.target.value)} required />
          <button type="submit" style={{ ...styles.btn, width: '100%', backgroundColor: '#28a745' }}>Register</button>
          <span style={styles.toggleLink} onClick={() => { setView('login'); setError(''); }}>Already have an account? Login here.</span>
        </form>
      )}

      {view === 'chat' && (
        <div>
          <p style={{ fontSize: '12px', color: '#666' }}>Logged in as: {userEmail}</p>
          <div style={styles.chatBox}>
            {messages.map((m, i) => (
              <div key={i} style={m.role === 'user' ? styles.user : styles.bot}>
                <div style={{ whiteSpace: 'pre-wrap' }}>{m.content}</div>
              </div>
            ))}
            {loading && <div style={styles.bot}>Typing...</div>}
            <div ref={chatEndRef} />
          </div>
          <form onSubmit={sendMessage} style={{ display: 'flex', gap: '5px' }}>
            <input style={{ ...styles.input, flexGrow: 1 }} value={input} onChange={e => setInput(e.target.value)} placeholder="Type a message..." />
            <button type="submit" style={styles.btn}>Send</button>
          </form>
        </div>
      )}
    </div>
  );
}