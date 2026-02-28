import { useState, useRef, useEffect } from 'react'
import './App.css'

const API_BASE = import.meta.env.VITE_API_URL || ''

function App() {
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [expandedResponseIndex, setExpandedResponseIndex] = useState(null)
  const chatEndRef = useRef(null)

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, loading])

  const hideError = () => {
    setError('')
  }

  const ask = async (question) => {
    const q = question?.trim()
    if (!q) return
    hideError()
    setMessages((prev) => [...prev, { role: 'user', content: q }])
    setInput('')
    setLoading(true)
    try {
      const res = await fetch(`${API_BASE}/ask`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question: q }),
      })
      const data = await res.json()
      if (!res.ok) {
        const msg = data.detail
          ? Array.isArray(data.detail)
            ? data.detail.map((d) => d.msg).join(' ')
            : data.detail
          : 'Request failed'
        setError(String(msg))
        setMessages((prev) => [
          ...prev,
          { role: 'assistant', content: 'Sorry, something went wrong. Check the error below.', trace: [], intent: null, rawResponse: data },
        ])
        return
      }
      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: data.answer || 'No answer generated.',
          trace: data.trace || [],
          intent: data.intent ?? null,
          rawResponse: data,
        },
      ])
    } catch (e) {
      setError(e.message || 'Network error')
      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: 'Could not reach the server. Is the backend running?',
          trace: [],
          intent: null,
          rawResponse: null,
        },
      ])
    } finally {
      setLoading(false)
    }
  }

  const handleSubmit = (e) => {
    e?.preventDefault()
    ask(input)
  }

  return (
    <>
      <header className="header">
        <h1>Monday.com Business Intelligence Agent</h1>
        <p>
          Ask founder-level questions about pipeline, revenue, and sector performance. Answers use live monday.com data.
        </p>
      </header>
      <main className="chat">
        {messages.map((m, i) => (
          <div key={i} className={`message ${m.role}`}>
            <div className="role">{m.role === 'user' ? 'You' : 'Agent'}</div>
            <div className="content">{m.content}</div>
            {m.trace?.length > 0 && (
              <div className="trace">
                <div className="trace-title">Action / tool-call trace</div>
                <ol>
                  {m.trace.map((step, j) => (
                    <li key={j}>{step}</li>
                  ))}
                </ol>
              </div>
            )}
            {m.intent != null && m.role === 'assistant' && (
              <div className="intent">
                Intent: <code>{JSON.stringify(m.intent)}</code>
              </div>
            )}
            {m.role === 'assistant' && m.rawResponse != null && (
              <div className="api-response-wrap">
                <button
                  type="button"
                  className="btn-api-response"
                  onClick={() => setExpandedResponseIndex(expandedResponseIndex === i ? null : i)}
                >
                  {expandedResponseIndex === i ? 'Hide API response' : 'View API response'}
                </button>
                {expandedResponseIndex === i && (
                  <pre className="api-response-json">{JSON.stringify(m.rawResponse, null, 2)}</pre>
                )}
              </div>
            )}
          </div>
        ))}
        {loading && (
          <div className="message">
            <div className="role">Agent</div>
            <div className="loading">
              <span className="dot" />
              <span className="dot" />
              <span className="dot" />
              Calling monday.com API & processing…
            </div>
          </div>
        )}
        <div ref={chatEndRef} />
      </main>
      <div className="input-area">
        <form className="input-wrap" onSubmit={handleSubmit}>
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault()
                ask(input)
              }
            }}
            placeholder="e.g. How's our pipeline looking for the energy sector this quarter?"
            rows={1}
            disabled={loading}
          />
          <button type="submit" disabled={loading}>
            Ask
          </button>
        </form>
        {error && <p className="error">{error}</p>}
      </div>
    </>
  )
}

export default App
