import { useState } from 'react'
import {
  ArrowLeft,
  ArrowUpRight,
  Activity,
  ShieldCheck,
  Trash2,
  MessageSquareText,
} from 'lucide-react'
import './IntelligenceDesk.css'

function IntelligenceDesk({ onBack }) {
  const [message, setMessage] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [result, setResult] = useState(null)

  const maxLength = 2000

  const handleMessageChange = (value) => {
    setMessage(value.slice(0, maxLength))
    setError(null)
  }

  const handleSubmit = async (event) => {
    event.preventDefault()

    const trimmed = message.trim()
    if (!trimmed || loading) return

    setLoading(true)
    setError(null)

    try {
      const apiBase = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
      const response = await fetch(`${apiBase}/api/analyze`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: trimmed }),
      })

      if (!response.ok) {
        throw new Error(`Server returned HTTP ${response.status}`)
      }

      const data = await response.json()
      setResult(data)
    } catch (err) {
      setError(
        'Unable to connect to analysis engine. Please ensure the backend server is reachable.'
      )
    } finally {
      setLoading(false)
    }
  }

  const clearMessage = () => {
    setMessage('')
    setError(null)
    setResult(null)
  }

  return (
    <main className="desk-page">
      <nav className="desk-navbar">
        <button className="desk-brand" onClick={onBack}>
          FLOODSENSE<span>®</span>
        </button>

        <div className="desk-nav-label">
          INTELLIGENCE / WORKSPACE
        </div>

        <button className="desk-back" onClick={onBack}>
          <ArrowLeft size={15} />
          Back to website
        </button>
      </nav>

      <section className="desk-main">
        <div className="desk-heading">
          <p className="eyebrow">
            FLOODSENSE INTELLIGENCE SYSTEM / 01
          </p>

          <h1>
            Every message
            <br />
            <em>matters.</em>
          </h1>

          <p className="desk-intro">
            Understand the situation behind the message.
            Identify urgency. Bring critical information into focus.
          </p>
        </div>

        <div className="desk-workspace">
          <div className="desk-input-panel">
            <div className="desk-panel-heading">
              <div>
                <span className="desk-step">01 / INPUT</span>
                <h2>Emergency message</h2>
              </div>

              <MessageSquareText size={21} strokeWidth={1.3} />
            </div>

            <form onSubmit={handleSubmit}>
              <label htmlFor="emergency-message">
                MESSAGE CONTENT
              </label>

              <textarea
                id="emergency-message"
                value={message}
                onChange={(event) =>
                  handleMessageChange(event.target.value)
                }
                placeholder="Describe the emergency situation here...

For example: Water levels are rising rapidly near our village. Several families are trapped and need immediate assistance..."
                maxLength={maxLength}
              />

              <div className="desk-input-footer">
                <span>
                  {message.length} / {maxLength} characters
                </span>

                <button
                  type="button"
                  className="desk-clear"
                  onClick={clearMessage}
                  disabled={!message && !result && !error}
                >
                  <Trash2 size={14} />
                  Clear
                </button>
              </div>

              <button
                type="submit"
                className="desk-submit"
                disabled={!message.trim() || loading}
              >
                {loading ? 'Analyzing message...' : 'Analyze message'}
                <ArrowUpRight size={17} />
              </button>
            </form>

            {loading && (
              <p className="desk-notice" role="status">
                Analyzing emergency message through 5-stage FloodSense pipeline...
              </p>
            )}

            {error && (
              <p className="desk-notice" style={{ color: '#b8544d' }} role="alert">
                {error}
              </p>
            )}

            {result && !loading && (
              <p className="desk-notice" role="status">
                Analysis complete:{' '}
                {result.flood_detected
                  ? `${result.severity.level} Severity (${result.priority.tier})`
                  : 'Non-Flood Notice (Not Applicable)'}
                . Triage breakdown populated in the intelligence panel.
              </p>
            )}
          </div>

          <aside className="desk-info-panel">
            <span className="desk-step">02 / ANALYSIS</span>

            <div className="desk-info-icon">
              <Activity size={25} strokeWidth={1.2} />
            </div>

            {result ? (
              <>
                <h2>
                  {result.flood_detected
                    ? `${result.severity.level} Severity`
                    : 'Routine Notice'}
                  <br />
                  <em>{result.priority.tier}</em>
                </h2>

                <p>{result.severity.reasoning}</p>

                <div className="desk-capabilities">
                  <div>
                    <ShieldCheck size={17} />
                    <span>
                      {result.flood_detected
                        ? `Category: ${
                            result.humanitarian_context?.category
                              ? result.humanitarian_context.category.replace(/_/g, ' ')
                              : 'Flood Emergency'
                          }`
                        : 'Status: Non-Flood / Routine'}
                    </span>
                  </div>
                  <div>
                    <Activity size={17} />
                    <span>
                      Severity: {result.severity.level}
                      {result.supporting_indicators?.length > 0
                        ? ` (${result.supporting_indicators.join(', ')})`
                        : ''}
                    </span>
                  </div>
                  <div>
                    <ArrowUpRight size={17} />
                    <span>
                      Priority Score: {result.priority.score} / 100 — {result.priority.tier}
                    </span>
                  </div>
                </div>

                <div className="desk-engine-status">
                  <span className="status-dot" style={{ background: '#78c7e8' }} />
                  ANALYSIS ENGINE — TRIAGE COMPLETED
                </div>
              </>
            ) : (
              <>
                <h2>
                  Clarity begins
                  <br />
                  with context.
                </h2>

                <p>
                  FloodSense is designed to interpret emergency
                  messages and surface information that can help
                  responders understand the situation.
                </p>

                <div className="desk-capabilities">
                  <div>
                    <ShieldCheck size={17} />
                    <span>Emergency classification</span>
                  </div>
                  <div>
                    <Activity size={17} />
                    <span>Severity assessment</span>
                  </div>
                  <div>
                    <ArrowUpRight size={17} />
                    <span>Priority identification</span>
                  </div>
                </div>

                <div className="desk-engine-status">
                  <span className="status-dot" />
                  {loading ? 'ANALYSIS ENGINE — PROCESSING...' : 'ANALYSIS ENGINE — READY'}
                </div>
              </>
            )}
          </aside>
        </div>

        <footer className="desk-footer">
          <span>FLOODSENSE © 2026</span>
          <span>TECHNOLOGY WITH A HUMAN PURPOSE.</span>
        </footer>
      </section>
    </main>
  )
}

export default IntelligenceDesk
