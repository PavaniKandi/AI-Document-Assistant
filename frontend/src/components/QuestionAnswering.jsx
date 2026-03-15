import React, { useState } from 'react'
import axios from 'axios'
import './QuestionAnswering.css'

function QuestionAnswering({ documentId, onHistoryUpdate }) {
  const [question, setQuestion] = useState('')
  const [answer, setAnswer] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const handleAsk = async (e) => {
    e.preventDefault()
    
    if (!question.trim()) return

    setLoading(true)
    setError(null)

    try {
      const response = await axios.post('/api/ask', {
        document_id: documentId,
        question: question
      }, {
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        },
        withCredentials: false
      })

      setAnswer(response.data.answer)
      onHistoryUpdate()
      setQuestion('')
    } catch (err) {
      setError(err.response?.data?.error || err.message || 'Failed to get answer')
      console.error('Ask error:', err)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="qa-shell">
      <div className="qa-section">
        <h2>Ask Questions About Your Document</h2>
        <p className="qa-intro">
          Ask direct questions, summarize content, or test whether the document contains a
          specific detail.
        </p>

        <form onSubmit={handleAsk} className="question-form">
          <input
            type="text"
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            placeholder="What would you like to know about this document?"
            disabled={loading}
            className="question-input"
          />
          <button type="submit" disabled={loading || !question.trim()} className="ask-btn">
            {loading ? 'Thinking...' : 'Ask'}
          </button>
        </form>

        {error && <div className="error-message">{error}</div>}

        {answer ? (
          <div className="answer-section">
            <h3>Latest Answer</h3>
            <div className="answer-box">
              {answer}
            </div>
          </div>
        ) : (
          <div className="answer-placeholder">
            Your latest answer will appear here after you ask a question.
          </div>
        )}
      </div>
    </div>
  )
}

export default QuestionAnswering
