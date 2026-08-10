import { useEffect, useRef, useState } from 'react'

const API_BASE = import.meta.env.VITE_API_URL ?? ''

export default function App() {
  const [topics, setTopics] = useState([])
  const [topic, setTopic] = useState('geoai')
  const [paperCount, setPaperCount] = useState(null)
  const [messages, setMessages] = useState([])
  const [question, setQuestion] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState('')
  const inputRef = useRef(null)

  useEffect(() => {
    fetch(`${API_BASE}/api/topics`).then((res) => res.json()).then(({ topics }) => setTopics(topics))
      .catch(() => setError('The API is unavailable. Start the FastAPI server and try again.'))
    fetch(`${API_BASE}/api/knowledge-base`).then((res) => res.json()).then(({ papers }) => setPaperCount(papers))
      .catch(() => {})
  }, [])

  async function sendQuestion(event) {
    event.preventDefault()
    const text = question.trim()
    if (!text || isLoading) return

    setMessages((current) => [...current, { role: 'user', content: text }])
    setQuestion('')
    setError('')
    setIsLoading(true)
    try {
      const response = await fetch(`${API_BASE}/api/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question: text, topic }),
      })
      const data = await response.json()
      if (!response.ok) throw new Error(data.detail || 'Unable to get an answer.')
      setMessages((current) => [...current, {
        role: 'assistant', content: data.answer, responseTime: data.response_time,
      }])
    } catch (err) {
      setError(err.message || 'Unable to get an answer. Please try again.')
    } finally {
      setIsLoading(false)
      inputRef.current?.focus()
    }
  }

  return <main className="app-shell">
    <aside className="sidebar">
      <div className="brand"><span>◈</span><div><strong>GeoAI</strong><small>Research Assistant</small></div></div>
      <section className="control-group">
        <p className="eyebrow">Knowledge base</p>
        <div className="metric"><strong>{paperCount ?? '—'}</strong><span>research papers indexed</span></div>
      </section>
      <label className="control-group" htmlFor="topic">
        <span className="eyebrow">Research topic</span>
        <select id="topic" value={topic} onChange={(event) => setTopic(event.target.value)}>
          {topics.map((item) => <option key={item} value={item}>{item}</option>)}
        </select>
      </label>
      <p className="sidebar-note">Answers are grounded in the retrieved GeoAI literature.</p>
    </aside>

    <section className="chat-panel">
      <header><div><p className="eyebrow">Literature exploration</p><h1>Ask about GeoAI research</h1></div><span className="status"><i /> Online</span></header>
      <div className="messages" aria-live="polite">
        {messages.length === 0 && <div className="welcome"><div className="welcome-icon">⌁</div><h2>Explore the research landscape</h2><p>Ask about remote sensing, foundation models, change detection, or another indexed topic.</p><div className="suggestions">{['How are Vision Transformers used in Remote Sensing?', 'What are Foundation Models for Earth Observation?', 'What are recent trends in Change Detection?'].map((item) => <button key={item} onClick={() => setQuestion(item)}>{item}</button>)}</div></div>}
        {messages.map((message, index) => <article key={index} className={`message ${message.role}`}><span className="avatar">{message.role === 'user' ? 'You' : 'AI'}</span><div><p>{message.content}</p>{message.responseTime != null && <small>Response time: {message.responseTime.toFixed(2)}s</small>}</div></article>)}
        {isLoading && <article className="message assistant"><span className="avatar">AI</span><p className="thinking"><i /><i /><i /> Searching papers…</p></article>}
      </div>
      {error && <p className="error" role="alert">{error}</p>}
      <form onSubmit={sendQuestion}><input ref={inputRef} value={question} onChange={(event) => setQuestion(event.target.value)} placeholder="Ask a question about GeoAI research…" aria-label="Research question" /><button disabled={isLoading || !question.trim()}>{isLoading ? 'Searching' : 'Send'} <span>→</span></button></form>
    </section>
  </main>
}
