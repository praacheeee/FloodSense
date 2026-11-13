
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
  const [submitted, setSubmitted] = useState(false)

  const maxLength = 2000

  const handleMessageChange = (value) => {
    setMessage(value.slice(0, maxLength))
    setSubmitted(false)
  }

  const handleSubmit = (event) => {
    event.preventDefault()

    if (!message.trim()) return

    setSubmitted(true)
  }

  const clearMessage = () => {
    setMessage('')
    setSubmitted(false)
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
                  disabled={!message}
                >
                  <Trash2 size={14} />
                  Clear
                </button>
              </div>

              <button
                type="submit"
                className="desk-submit"
                disabled={!message.trim()}
              >
                Prepare for analysis
                <ArrowUpRight size={17} />
              </button>
            </form>

            {submitted && (
              <p className="desk-notice" role="status">
                Your message is ready. The analysis engine will
                be connected to this workspace in the next stage.
              </p>
            )}
          </div>

          <aside className="desk-info-panel">
            <span className="desk-step">02 / ANALYSIS</span>

            <div className="desk-info-icon">
              <Activity size={25} strokeWidth={1.2} />
            </div>

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
              ANALYSIS ENGINE — AWAITING CONNECTION
            </div>
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
