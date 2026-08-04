import { useState, useRef, useEffect } from 'react'
import { Send, Shield, Lock, User, FileText, Database, LogOut } from 'lucide-react'
import ReactMarkdown from 'react-markdown'
import './index.css'

const API_URL = 'http://127.0.0.1:8000'

function App() {
  const [token, setToken] = useState(localStorage.getItem('jwt_token'))
  const [role, setRole] = useState(localStorage.getItem('jwt_role'))
  
  const handleLogin = (jwt, userRole) => {
    localStorage.setItem('jwt_token', jwt)
    localStorage.setItem('jwt_role', userRole)
    setToken(jwt)
    setRole(userRole)
  }

  const handleLogout = () => {
    localStorage.removeItem('jwt_token')
    localStorage.removeItem('jwt_role')
    setToken(null)
    setRole(null)
  }

  return (
    <div className="glass-panel">
      {!token ? (
        <LoginScreen onLogin={handleLogin} />
      ) : (
        <ChatScreen token={token} role={role} onLogout={handleLogout} />
      )}
    </div>
  )
}

function LoginScreen({ onLogin }) {
  const [username, setUsername] = useState('alice_hr')
  const [password, setPassword] = useState('password123')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError('')
    
    try {
      const res = await fetch(`${API_URL}/token`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password })
      })
      
      const data = await res.json()
      if (!res.ok) throw new Error(data.detail || 'Login failed')
      
      onLogin(data.access_token, data.role)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="login-container">
      <div className="login-header">
        <Shield size={48} color="#3b82f6" style={{ margin: '0 auto 1rem' }} />
        <h1>Secure Enterprise RAG</h1>
        <p>Zero-Trust Authentication Gateway</p>
      </div>
      
      <form onSubmit={handleSubmit}>
        <div className="input-group">
          <label><User size={14} /> Username</label>
          <select 
            className="input-field" 
            value={username} 
            onChange={(e) => setUsername(e.target.value)}
          >
            <option value="alice_hr">Alice (HR Manager)</option>
            <option value="bob_eng">Bob (Software Engineer)</option>
          </select>
        </div>
        
        <div className="input-group">
          <label><Lock size={14} /> Password</label>
          <input 
            type="password" 
            className="input-field" 
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
        </div>
        
        {error && <div className="error-message">{error}</div>}
        
        <button type="submit" className="btn" disabled={loading} style={{ marginTop: '1.5rem' }}>
          {loading ? 'Authenticating...' : 'Secure Login'}
        </button>
      </form>
    </div>
  )
}

function ChatScreen({ token, role, onLogout }) {
  const [messages, setMessages] = useState([
    { 
      role: 'ai', 
      content: `Welcome to the Secure Knowledge Base. Your access level is verified as **${role}**. What would you like to know?`,
      sources: null
    }
  ])
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const messagesEndRef = useRef(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const handleSend = async () => {
    if (!input.trim()) return
    
    const userMsg = input
    setInput('')
    setMessages(prev => [...prev, { role: 'user', content: userMsg }])
    setIsLoading(true)

    try {
      const res = await fetch(`${API_URL}/query?token=${token}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question: userMsg })
      })
      
      if (res.status === 401) {
        onLogout()
        return
      }
      
      const data = await res.json()
      
      setMessages(prev => [...prev, { 
        role: 'ai', 
        content: data.answer,
        sources: data.sources_accessed 
      }])
    } catch (err) {
      setMessages(prev => [...prev, { 
        role: 'ai', 
        content: "Network error connecting to the secure enclave." 
      }])
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="chat-container">
      <div className="chat-header">
        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
          <Shield size={24} color="#3b82f6" />
          <span style={{ fontWeight: 600 }}>Secure RAG Session</span>
          <span className="role-badge">{role.replace('_', ' ')}</span>
        </div>
        <button onClick={onLogout} className="logout-btn">
          <LogOut size={16} style={{ verticalAlign: 'middle', marginRight: '4px' }} />
          Logout
        </button>
      </div>

      <div className="messages-area">
        {messages.map((msg, idx) => (
          <div key={idx} className={`message ${msg.role}`}>
            <div className={`avatar ${msg.role}`}>
              {msg.role === 'ai' ? <Database size={18} /> : <User size={18} />}
            </div>
            <div className="message-content">
              <ReactMarkdown className="markdown-body">
                {msg.content}
              </ReactMarkdown>
              
              {msg.sources && msg.sources.length > 0 && (
                <div className="sources-box">
                  <h4><FileText size={12} style={{ verticalAlign: 'middle', marginRight: '4px' }}/> Secured Sources Accessed</h4>
                  {msg.sources.map((src, i) => (
                    <span key={i} className={`source-tag ${src.role === 'HR_Manager' ? 'hr' : 'eng'}`}>
                      <Lock size={10} /> {src.source} ({src.role})
                    </span>
                  ))}
                </div>
              )}
            </div>
          </div>
        ))}
        {isLoading && (
          <div className="message ai">
            <div className="avatar ai"><Database size={18} /></div>
            <div className="message-content typing-indicator">
              <div className="dot"></div><div className="dot"></div><div className="dot"></div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      <div className="chat-input-area">
        <input 
          className="chat-input" 
          placeholder="Ask a question..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && handleSend()}
        />
        <button className="send-btn" onClick={handleSend} disabled={isLoading || !input.trim()}>
          <Send size={18} />
        </button>
      </div>
    </div>
  )
}

export default App
