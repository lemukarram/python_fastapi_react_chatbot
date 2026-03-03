import React, { useState, useEffect, useRef } from 'react';
import { ShieldCheck, Users, MessageSquare, BookOpen, Upload, Trash2, ArrowLeft, Mic, MicOff } from 'lucide-react';

const API_BASE = "http://127.0.0.1:8000";

export default function App() {
  // ── Auth state ─────────────────────────────────────────────────────────────
  const [token, setToken] = useState(localStorage.getItem('token') || '');
  const [userEmail, setUserEmail] = useState(localStorage.getItem('userEmail') || '');
  const [isAdmin, setIsAdmin] = useState(localStorage.getItem('isAdmin') === 'true');
  const [view, setView] = useState(token ? 'chat' : 'login');

  // ── Auth form state ─────────────────────────────────────────────────────────
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  // ── Chat state ──────────────────────────────────────────────────────────────
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);

  // ── Voice state ─────────────────────────────────────────────────────────────
  const [voiceSupported, setVoiceSupported] = useState(false); // hides UI on unsupported browsers
  const [isListening,    setIsListening]    = useState(false); // mic is capturing
  const [isSpeaking,     setIsSpeaking]     = useState(false); // TTS is playing
  const [isMuted,        setIsMuted]        = useState(false); // user silenced TTS
  const [voiceMode,      setVoiceMode]      = useState(false); // continuous conversation loop
  const [voiceLang,      setVoiceLang]      = useState('ar-SA'); // STT + TTS language

  // ── Admin panel state ───────────────────────────────────────────────────────
  const [adminTab, setAdminTab] = useState('users');
  const [adminUsers, setAdminUsers] = useState([]);
  const [adminChats, setAdminChats] = useState([]);
  const [adminKnowledge, setAdminKnowledge] = useState([]);
  const [adminLoading, setAdminLoading] = useState(false);
  const [adminError, setAdminError] = useState('');
  const [kbText, setKbText] = useState('');
  const [kbFileLoading, setKbFileLoading] = useState(false);
  const [kbMsg, setKbMsg] = useState(null);

  const chatBoxRef     = useRef(null);
  const recognitionRef = useRef(null);                   // SpeechRecognition instance (lazy-init)
  const synthRef       = useRef(window.speechSynthesis); // shorthand alias for Web Speech Synthesis
  const autoRestartRef = useRef(false);                  // ref (not state) — survives stale closures in TTS callbacks

  useEffect(() => {
    if (token && view === 'chat') fetchHistory();
  }, [token, view]);

  useEffect(() => {
    if (chatBoxRef.current) {
      chatBoxRef.current.scrollTop = chatBoxRef.current.scrollHeight;
    }
  }, [messages]);

  // Detect Web Speech API support once on mount — hides mic button on unsupported browsers (e.g. Firefox)
  useEffect(() => {
    if (window.SpeechRecognition || window.webkitSpeechRecognition) {
      setVoiceSupported(true);
    }
  }, []);

  // ── Auth handlers ───────────────────────────────────────────────────────────
  const fetchHistory = async () => {
    try {
      const res = await fetch(`${API_BASE}/api/v1/history`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (res.ok) setMessages(await res.json());
    } catch { console.error('Failed to load history.'); }
  };

  const handleRegister = async (e) => {
    e.preventDefault();
    setError(''); setSuccess('');
    try {
      const res = await fetch(`${API_BASE}/auth/register`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password }),
      });
      if (res.ok) {
        setSuccess('Registration successful. You can now login.');
        setView('login');
        setPassword('');
      } else {
        const data = await res.json();
        setError(data.detail || 'Registration failed. Please try again.');
      }
    } catch { setError('Cannot connect to server.'); }
  };

  const handleLogin = async (e) => {
    e.preventDefault();
    setError(''); setSuccess('');
    const formData = new URLSearchParams();
    formData.append('username', email);
    formData.append('password', password);
    try {
      const res = await fetch(`${API_BASE}/auth/jwt/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: formData,
      });
      const data = await res.json();
      if (res.ok) {
        const { access_token } = data;
        // Fetch profile to determine admin status — is_superuser is not in the JWT payload
        const meRes = await fetch(`${API_BASE}/users/me`, {
          headers: { Authorization: `Bearer ${access_token}` },
        });
        const meData = await meRes.json();
        const superuser = meData.is_superuser ?? false;

        setToken(access_token);
        setUserEmail(email);
        setIsAdmin(superuser);
        localStorage.setItem('token', access_token);
        localStorage.setItem('userEmail', email);
        localStorage.setItem('isAdmin', String(superuser));
        setView('chat');
      } else {
        setError('Invalid email or password.');
      }
    } catch { setError('Connection error.'); }
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('userEmail');
    localStorage.removeItem('isAdmin');
    setToken(''); setUserEmail(''); setIsAdmin(false);
    setMessages([]);
    setView('login');
  };

  // ── Chat handlers ───────────────────────────────────────────────────────────
  const sendMessage = async (e) => {
    e.preventDefault();
    if (!input.trim()) return;
    setMessages(prev => [...prev, { role: 'user', content: input }]);
    setInput('');
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE}/api/v1/message`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
        body: JSON.stringify({ message: input }),
      });
      const data = await res.json();
      if (res.ok) setMessages(prev => [...prev, { role: 'bot', content: data.reply, sources: data.sources || [] }]);
    } catch {
      setMessages(prev => [...prev, { role: 'bot', content: 'Error connecting to server.' }]);
    } finally { setLoading(false); }
  };

  // ── Voice handlers ──────────────────────────────────────────────────────────

  // STT: lazy SpeechRecognition init — called on first mic click (not in useEffect)
  // so it fires after a user gesture, which is required by browsers for mic access.
  const initRecognition = () => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) return null;
    const rec = new SpeechRecognition();
    rec.lang            = voiceLang; // configurable via language selector in the UI
    rec.interimResults  = false;   // only fire onresult with final transcript
    rec.maxAlternatives = 1;
    rec.continuous      = false;   // stop automatically after one utterance (most reliable cross-browser)

    rec.onstart = () => {
      setIsListening(true);
      synthRef.current.cancel(); // stop any TTS when mic activates
      setIsSpeaking(false);
    };

    rec.onresult = (event) => {
      const transcript = event.results[0][0].transcript.trim();
      if (transcript) {
        setInput(transcript);         // show transcript in the text input box
        sendVoiceMessage(transcript); // auto-submit to the chat API
      }
    };

    rec.onerror = (event) => {
      setIsListening(false);
      if (event.error === 'not-allowed' || event.error === 'service-not-allowed') {
        setVoiceSupported(false); // mic permission denied — hide voice UI permanently
      }
      if (event.error === 'no-speech' && autoRestartRef.current) {
        setTimeout(() => startListening(), 300); // user was silent — retry if in voice mode
      }
    };

    rec.onend = () => { setIsListening(false); };
    return rec;
  };

  const startListening = () => {
    synthRef.current.cancel();
    setIsSpeaking(false);
    if (!recognitionRef.current) recognitionRef.current = initRecognition();
    if (!recognitionRef.current) return;
    try { recognitionRef.current.start(); } catch (err) { /* InvalidStateError: already started — ignore */ }
  };

  const stopListening = () => {
    if (recognitionRef.current) try { recognitionRef.current.stop(); } catch (err) { /* ignore */ }
    setIsListening(false);
  };

  // Voice: send a transcript directly without a form event
  // NOTE: mirrors sendMessage network logic — if sendMessage is refactored (e.g. for streaming),
  // update this function in parallel.
  const sendVoiceMessage = async (transcript) => {
    if (!transcript.trim()) return;
    const captured = transcript; // capture value before any state updates clear it
    setMessages(prev => [...prev, { role: 'user', content: captured }]);
    setInput('');
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE}/api/v1/message`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
        body: JSON.stringify({ message: captured }),
      });
      const data = await res.json();
      if (res.ok) {
        setMessages(prev => [...prev, { role: 'bot', content: data.reply, sources: data.sources || [] }]);
        speakText(data.reply);
      }
    } catch {
      setMessages(prev => [...prev, { role: 'bot', content: 'Error connecting to server.' }]);
    } finally { setLoading(false); }
  };

  // TTS: speak the bot reply aloud using the browser's Web Speech Synthesis API
  const speakText = (text) => {
    if (isMuted) {
      if (autoRestartRef.current) startListening(); // muted but voice mode on — keep the loop alive
      return;
    }
    synthRef.current.cancel();
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang   = voiceLang;
    utterance.rate   = 0.95; // slightly slower than default for clarity
    utterance.pitch  = 1;
    utterance.volume = 1;

    // Prefer a voice matching the selected language; fall back to browser default
    const voices    = synthRef.current.getVoices();
    const langCode  = voiceLang.split('-')[0]; // e.g. 'ar' from 'ar-SA'
    const bestVoice = voices.find(v => v.lang === voiceLang) || voices.find(v => v.lang.startsWith(langCode));
    if (bestVoice) utterance.voice = bestVoice;

    utterance.onstart = () => setIsSpeaking(true);
    utterance.onend   = () => {
      setIsSpeaking(false);
      // autoRestartRef (not state) is used here because utterance callbacks capture stale state values
      if (autoRestartRef.current) setTimeout(() => startListening(), 400); // 400ms gap prevents mic picking up TTS tail
    };
    utterance.onerror = (ev) => {
      if (ev.error !== 'interrupted') console.warn('TTS error:', ev.error); // 'interrupted' fires on cancel() — not a real error
      setIsSpeaking(false);
    };
    synthRef.current.speak(utterance);
  };

  const cancelSpeech = () => { synthRef.current.cancel(); setIsSpeaking(false); };

  const toggleMute = () => {
    if (!isMuted && isSpeaking) cancelSpeech();
    setIsMuted(prev => !prev);
  };

  const handleLangChange = (e) => {
    setVoiceLang(e.target.value);
    recognitionRef.current = null; // force re-init with new language on next mic click
  };

  const toggleVoiceMode = () => {
    const next = !voiceMode;
    setVoiceMode(next);
    autoRestartRef.current = next; // keep ref in sync so TTS onend callback sees the current value
    if (!next) { stopListening(); cancelSpeech(); }
  };

  // ── Admin handlers ──────────────────────────────────────────────────────────
  const authHeader = { Authorization: `Bearer ${token}` };

  const fetchAdminUsers = async () => {
    const res = await fetch(`${API_BASE}/api/v1/admin/users`, { headers: authHeader });
    if (res.ok) setAdminUsers(await res.json());
  };
  const fetchAdminChats = async () => {
    const res = await fetch(`${API_BASE}/api/v1/admin/chats`, { headers: authHeader });
    if (res.ok) setAdminChats(await res.json());
  };
  const fetchAdminKnowledge = async () => {
    const res = await fetch(`${API_BASE}/api/v1/admin/knowledge`, { headers: authHeader });
    if (res.ok) setAdminKnowledge(await res.json());
  };

  const openAdminPanel = async () => {
    setAdminLoading(true); setAdminError(''); setKbMsg(null);
    try {
      await Promise.all([fetchAdminUsers(), fetchAdminChats(), fetchAdminKnowledge()]);
    } catch { setAdminError('Failed to load admin data.'); }
    finally { setAdminLoading(false); }
    setView('admin');
  };

  const deleteKnowledgeEntry = async (id) => {
    await fetch(`${API_BASE}/api/v1/admin/knowledge/${id}`, {
      method: 'DELETE', headers: authHeader,
    });
    setAdminKnowledge(prev => prev.filter(k => k.id !== id));
  };

  const handleKbTextIngest = async (e) => {
    e.preventDefault();
    const chunks = kbText.split(/\n\n+/).map(c => c.trim()).filter(Boolean);
    setKbMsg(null);
    try {
      const res = await fetch(`${API_BASE}/api/v1/ingest`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', ...authHeader },
        body: JSON.stringify({ texts: chunks }),
      });
      const data = await res.json();
      if (res.ok) { setKbMsg({ type: 'success', text: data.message }); setKbText(''); await fetchAdminKnowledge(); }
      else setKbMsg({ type: 'error', text: data.detail || 'Failed.' });
    } catch { setKbMsg({ type: 'error', text: 'Cannot connect to server.' }); }
  };

  const handleKbFileUpload = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setKbFileLoading(true); setKbMsg(null);
    const form = new FormData();
    form.append('file', file);
    try {
      const res = await fetch(`${API_BASE}/api/v1/admin/knowledge/upload`, {
        method: 'POST', headers: authHeader, body: form,
      });
      const data = await res.json();
      if (res.ok) { setKbMsg({ type: 'success', text: data.message }); await fetchAdminKnowledge(); }
      else setKbMsg({ type: 'error', text: data.detail || 'Upload failed.' });
    } catch { setKbMsg({ type: 'error', text: 'Cannot connect to server.' }); }
    finally { setKbFileLoading(false); e.target.value = ''; }
  };

  // ── Inline styles (chat + auth panels — unchanged from original) ────────────
  const styles = {
    container: { fontFamily: 'sans-serif', maxWidth: '720px', margin: '20px auto', padding: '20px', backgroundColor: '#fff', border: '1px solid #eee', borderRadius: '12px' },
    chatBox: { height: '400px', overflowY: 'auto', marginBottom: '15px', padding: '10px', backgroundColor: '#fdfdfd', border: '1px solid #f0f0f0', borderRadius: '8px' },
    user: { backgroundColor: '#007bff', color: '#ffffff', float: 'right', clear: 'both', borderRadius: '8px', maxWidth: '80%', padding: '8px 12px', margin: '8px 5px' },
    bot: { backgroundColor: '#f1f1f1', color: '#333', float: 'left', clear: 'both', borderRadius: '8px', maxWidth: '80%', padding: '8px 12px', margin: '8px 5px' },
    input: { width: '80%', padding: '10px', borderRadius: '6px', border: '1px solid #ccc', boxSizing: 'border-box' },
    btn: { padding: '10px 20px', borderRadius: '6px', backgroundColor: '#007bff', color: 'white', border: 'none', cursor: 'pointer' },
    toggleLink: { color: '#007bff', cursor: 'pointer', textDecoration: 'underline', marginTop: '15px', display: 'block', fontSize: '14px' },
    textarea: { width: '100%', padding: '10px', borderRadius: '6px', border: '1px solid #ccc', boxSizing: 'border-box', fontSize: '13px', resize: 'vertical', minHeight: '110px' },
    micBtn: {
      width: '42px', height: '42px', borderRadius: '50%', border: 'none',
      cursor: 'pointer', display: 'flex', alignItems: 'center',
      justifyContent: 'center', flexShrink: 0, transition: 'background-color 0.2s, box-shadow 0.2s',
    },
    micBtnIdle:      { backgroundColor: '#e5e7eb', color: '#374151' },
    micBtnListening: { backgroundColor: '#ef4444', color: '#ffffff' },
    muteBtn: {
      padding: '4px 10px', borderRadius: '12px', border: '1px solid #d1d5db',
      fontSize: '11px', cursor: 'pointer', backgroundColor: 'transparent', color: '#6b7280',
    },
  };

  return (
    <div style={styles.container}>

      {/* ── Header ─────────────────────────────────────────────────────────── */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px' }}>
        <h2 style={{ margin: 0 }}>RSG Tender BOT</h2>
        {token && (
          <div style={{ display: 'flex', gap: '8px' }}>
            {isAdmin && view !== 'admin' && (
              <button
                onClick={openAdminPanel}
                style={{ ...styles.btn, backgroundColor: '#b45309', fontSize: '13px', padding: '8px 14px', display: 'flex', alignItems: 'center', gap: '5px' }}
              >
                <ShieldCheck size={14} /> Admin Panel
              </button>
            )}
            <button onClick={handleLogout} style={{ ...styles.btn, backgroundColor: '#dc3545' }}>Logout</button>
          </div>
        )}
      </div>

      {/* ── Global alerts ──────────────────────────────────────────────────── */}
      {success && <p style={{ color: 'green', backgroundColor: '#eaffea', padding: '10px', borderRadius: '6px' }}>{success}</p>}
      {error   && <p style={{ color: 'red',   backgroundColor: '#ffeaea', padding: '10px', borderRadius: '6px' }}>{error}</p>}

      {/* ── Login ──────────────────────────────────────────────────────────── */}
      {view === 'login' && (
        <form onSubmit={handleLogin}>
          <h3>Login</h3>
          <input type="email" placeholder="Email" style={{ ...styles.input, width: '100%', marginBottom: '10px' }} value={email} onChange={e => setEmail(e.target.value)} required />
          <input type="password" placeholder="Password" style={{ ...styles.input, width: '100%', marginBottom: '10px' }} value={password} onChange={e => setPassword(e.target.value)} required />
          <button type="submit" style={{ ...styles.btn, width: '100%' }}>Login</button>
          <span style={styles.toggleLink} onClick={() => { setView('register'); setError(''); }}>Don't have an account? Register here.</span>
        </form>
      )}

      {/* ── Register ───────────────────────────────────────────────────────── */}
      {view === 'register' && (
        <form onSubmit={handleRegister}>
          <h3>Create Account</h3>
          <input type="email" placeholder="Email" style={{ ...styles.input, width: '100%', marginBottom: '10px' }} value={email} onChange={e => setEmail(e.target.value)} required />
          <input type="password" placeholder="Password" style={{ ...styles.input, width: '100%', marginBottom: '10px' }} value={password} onChange={e => setPassword(e.target.value)} required />
          <button type="submit" style={{ ...styles.btn, width: '100%', backgroundColor: '#28a745' }}>Register</button>
          <span style={styles.toggleLink} onClick={() => { setView('login'); setError(''); }}>Already have an account? Login here.</span>
        </form>
      )}

      {/* ── Chat view ──────────────────────────────────────────────────────── */}
      {view === 'chat' && (
        <div>
          <p style={{ fontSize: '12px', color: '#666' }}>Logged in as: {userEmail}</p>

          <div ref={chatBoxRef} style={styles.chatBox}>
            {messages.map((m, i) => (
              <div key={i} style={m.role === 'user' ? styles.user : styles.bot}>
                <div style={{ whiteSpace: 'pre-wrap' }}>{m.content}</div>
                {m.role === 'bot' && m.sources && m.sources.length > 0 && (
                  <div style={{ marginTop: '8px', paddingTop: '8px', borderTop: '1px solid #ddd' }}>
                    <p style={{ fontSize: '11px', color: '#888', margin: '0 0 4px 0' }}>Sources from knowledge base:</p>
                    {m.sources.map((src, si) => (
                      <p key={si} style={{ fontSize: '11px', color: '#555', backgroundColor: '#f9f9f9', borderLeft: '3px solid #007bff', padding: '4px 8px', margin: '3px 0', borderRadius: '2px', whiteSpace: 'pre-wrap' }}>
                        {src}
                      </p>
                    ))}
                  </div>
                )}
              </div>
            ))}
            {loading && <div style={styles.bot}>Typing...</div>}
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
            {/* Row 1: text input + Send button + mic button */}
            <form onSubmit={sendMessage} style={{ display: 'flex', gap: '5px', alignItems: 'center' }}>
              <input
                style={{ ...styles.input, flexGrow: 1 }}
                value={input}
                onChange={e => setInput(e.target.value)}
                placeholder={isListening ? 'Listening...' : 'Type a message...'}
              />
              <button type="submit" style={styles.btn} disabled={loading}>Send</button>
              {voiceSupported && (
                <button
                  type="button"
                  title={isListening ? 'Stop listening' : 'Start voice input'}
                  onClick={isListening ? stopListening : startListening}
                  style={{ ...styles.micBtn, ...(isListening ? styles.micBtnListening : styles.micBtnIdle) }}
                  className={`mic-btn${isListening ? ' mic-pulsing' : ''}`}
                >
                  {isListening ? <MicOff size={18} /> : <Mic size={18} />}
                </button>
              )}
            </form>

            {/* Row 2: voice controls bar — only rendered if browser supports Web Speech API */}
            {voiceSupported && (
              <div style={{ display: 'flex', gap: '10px', alignItems: 'center', fontSize: '12px', color: '#6b7280', flexWrap: 'wrap' }}>
                {/* Language selector */}
                <select
                  value={voiceLang}
                  onChange={handleLangChange}
                  style={{ fontSize: '12px', padding: '3px 6px', borderRadius: '6px', border: '1px solid #d1d5db', color: '#374151', cursor: 'pointer', backgroundColor: '#fff' }}
                >
                  <option value="ar-SA">🇸🇦 Arabic (SA)</option>
                  <option value="en-US">🇺🇸 English (US)</option>
                  <option value="en-GB">🇬🇧 English (UK)</option>
                </select>

                <label style={{ display: 'flex', alignItems: 'center', gap: '4px', cursor: 'pointer', userSelect: 'none' }}>
                  <input type="checkbox" checked={voiceMode} onChange={toggleVoiceMode} style={{ cursor: 'pointer' }} />
                  Auto-listen after reply
                </label>
                <button type="button" onClick={toggleMute} style={styles.muteBtn}>
                  {isMuted ? '🔇 Unmute' : '🔊 Mute voice'}
                </button>
                {isListening && <span style={{ color: '#ef4444', fontWeight: '500' }}>● Listening...</span>}
                {isSpeaking && !isMuted && <span style={{ color: '#2563eb', fontWeight: '500' }}>● Speaking...</span>}
              </div>
            )}
          </div>

        </div>
      )}

      {/* ── Admin Panel ────────────────────────────────────────────────────── */}
      {view === 'admin' && (
        <div>
          {/* Back button */}
          <button onClick={() => setView('chat')}
            style={{ background: 'none', border: 'none', cursor: 'pointer', color: '#007bff', fontSize: '13px', display: 'flex', alignItems: 'center', gap: '4px', marginBottom: '12px', padding: 0 }}>
            <ArrowLeft size={14} /> Back to Chat
          </button>

          <h3 style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '16px' }}>
            <ShieldCheck size={20} color="#b45309" /> Admin Panel
          </h3>

          {/* Tabs */}
          <div style={{ display: 'flex', gap: '6px', marginBottom: '16px', borderBottom: '2px solid #e5e7eb', paddingBottom: '8px' }}>
            {[
              { key: 'users',     label: 'Users',          Icon: Users },
              { key: 'chats',     label: 'Chats',          Icon: MessageSquare },
              { key: 'knowledge', label: 'Knowledge Base', Icon: BookOpen },
            ].map(({ key, label, Icon }) => (
              <button key={key} onClick={() => setAdminTab(key)} style={{
                display: 'flex', alignItems: 'center', gap: '5px',
                padding: '7px 14px', borderRadius: '6px', border: 'none', cursor: 'pointer', fontSize: '13px', fontWeight: '500',
                backgroundColor: adminTab === key ? '#2563eb' : '#f3f4f6',
                color: adminTab === key ? '#fff' : '#374151',
              }}>
                <Icon size={13} /> {label}
              </button>
            ))}
          </div>

          {adminLoading && <p style={{ color: '#6b7280', fontSize: '13px' }}>Loading...</p>}
          {adminError  && <p style={{ color: '#dc2626', backgroundColor: '#fef2f2', padding: '8px', borderRadius: '6px', fontSize: '13px' }}>{adminError}</p>}

          {/* ── Users Tab ──────────────────────────────────────────────────── */}
          {adminTab === 'users' && !adminLoading && (
            <div style={{ overflowX: 'auto' }}>
              <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '13px' }}>
                <thead>
                  <tr style={{ backgroundColor: '#f3f4f6', textAlign: 'left' }}>
                    {['Email', 'Active', 'Role', 'Messages'].map(h => (
                      <th key={h} style={{ padding: '8px 10px', border: '1px solid #e5e7eb' }}>{h}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {adminUsers.map(u => (
                    <tr key={u.id} style={{ borderBottom: '1px solid #f3f4f6' }}>
                      <td style={{ padding: '8px 10px', border: '1px solid #e5e7eb' }}>{u.email}</td>
                      <td style={{ padding: '8px 10px', border: '1px solid #e5e7eb' }}>{u.is_active ? 'Yes' : 'No'}</td>
                      <td style={{ padding: '8px 10px', border: '1px solid #e5e7eb' }}>
                        {u.is_superuser
                          ? <span style={{ color: '#b45309', fontWeight: '600', display: 'flex', alignItems: 'center', gap: '4px' }}><ShieldCheck size={12} /> Admin</span>
                          : <span style={{ color: '#6b7280' }}>User</span>}
                      </td>
                      <td style={{ padding: '8px 10px', border: '1px solid #e5e7eb' }}>{u.message_count}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
              {adminUsers.length === 0 && <p style={{ color: '#9ca3af', fontSize: '13px', marginTop: '8px' }}>No users found.</p>}
            </div>
          )}

          {/* ── Chats Tab ──────────────────────────────────────────────────── */}
          {adminTab === 'chats' && !adminLoading && (
            <div style={{ overflowX: 'auto' }}>
              <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '13px' }}>
                <thead>
                  <tr style={{ backgroundColor: '#f3f4f6', textAlign: 'left' }}>
                    {['User', 'Role', 'Message', 'Date'].map(h => (
                      <th key={h} style={{ padding: '8px 10px', border: '1px solid #e5e7eb' }}>{h}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {adminChats.map(c => (
                    <tr key={c.id} style={{ borderBottom: '1px solid #f3f4f6' }}>
                      <td style={{ padding: '8px 10px', border: '1px solid #e5e7eb', fontSize: '12px' }}>{c.user_email}</td>
                      <td style={{ padding: '8px 10px', border: '1px solid #e5e7eb' }}>
                        <span style={{ color: c.role === 'user' ? '#2563eb' : '#16a34a', fontWeight: '500' }}>{c.role}</span>
                      </td>
                      <td style={{ padding: '8px 10px', border: '1px solid #e5e7eb', maxWidth: '260px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}
                        title={c.content}>{c.content}</td>
                      <td style={{ padding: '8px 10px', border: '1px solid #e5e7eb', whiteSpace: 'nowrap', fontSize: '11px' }}>
                        {new Date(c.created_at).toLocaleString()}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
              {adminChats.length === 0 && <p style={{ color: '#9ca3af', fontSize: '13px', marginTop: '8px' }}>No messages yet.</p>}
            </div>
          )}

          {/* ── Knowledge Base Tab ─────────────────────────────────────────── */}
          {adminTab === 'knowledge' && !adminLoading && (
            <div>
              {/* Feedback */}
              {kbMsg && (
                <p style={{ marginBottom: '12px', padding: '8px 12px', borderRadius: '6px', fontSize: '13px',
                  color: kbMsg.type === 'success' ? 'green' : 'red',
                  backgroundColor: kbMsg.type === 'success' ? '#eaffea' : '#ffeaea' }}>
                  {kbMsg.text}
                </p>
              )}

              {/* Add text chunks */}
              <div style={{ marginBottom: '14px', padding: '12px', backgroundColor: '#eef2ff', border: '1px solid #c7d2fe', borderRadius: '8px' }}>
                <h4 style={{ margin: '0 0 8px 0', fontSize: '13px', color: '#3730a3' }}>Add Text Chunks</h4>
                <form onSubmit={handleKbTextIngest}>
                  <textarea style={styles.textarea} value={kbText} onChange={e => setKbText(e.target.value)}
                    placeholder="Paste text. Separate chunks with a blank line." />
                  <div style={{ display: 'flex', justifyContent: 'flex-end', marginTop: '8px' }}>
                    <button type="submit" disabled={!kbText.trim()}
                      style={{ ...styles.btn, backgroundColor: '#4f46e5', fontSize: '13px', padding: '7px 16px', opacity: !kbText.trim() ? 0.5 : 1 }}>
                      Save Chunks
                    </button>
                  </div>
                </form>
              </div>

              {/* File upload */}
              <div style={{ marginBottom: '14px', padding: '12px', backgroundColor: '#f0fdf4', border: '1px solid #bbf7d0', borderRadius: '8px' }}>
                <h4 style={{ margin: '0 0 8px 0', fontSize: '13px', color: '#166534', display: 'flex', alignItems: 'center', gap: '5px' }}>
                  <Upload size={13} /> Upload .txt or .pdf
                </h4>
                <input type="file" accept=".txt,.pdf" onChange={handleKbFileUpload} disabled={kbFileLoading} style={{ fontSize: '13px' }} />
                {kbFileLoading && <p style={{ fontSize: '12px', color: '#6b7280', marginTop: '4px' }}>Uploading and embedding...</p>}
              </div>

              {/* KB entries list */}
              <div>
                <p style={{ fontSize: '12px', color: '#6b7280', marginBottom: '8px' }}>
                  {adminKnowledge.length} entr{adminKnowledge.length === 1 ? 'y' : 'ies'} in knowledge base
                </p>
                {adminKnowledge.map(kb => (
                  <div key={kb.id} style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between',
                    padding: '8px 10px', marginBottom: '6px', border: '1px solid #e5e7eb', borderRadius: '6px', backgroundColor: '#fff' }}>
                    <p style={{ fontSize: '12px', color: '#374151', margin: 0, flex: 1, marginRight: '10px' }}>{kb.content_preview}</p>
                    <button onClick={() => deleteKnowledgeEntry(kb.id)}
                      style={{ background: 'none', border: 'none', cursor: 'pointer', color: '#ef4444', flexShrink: 0, padding: '2px' }}
                      title="Delete entry">
                      <Trash2 size={15} />
                    </button>
                  </div>
                ))}
                {adminKnowledge.length === 0 && <p style={{ color: '#9ca3af', fontSize: '13px' }}>No knowledge base entries yet.</p>}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
