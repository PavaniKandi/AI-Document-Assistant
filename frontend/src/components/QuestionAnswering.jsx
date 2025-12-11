import React, { useState } from 'react'
import axios from 'axios'
import './QuestionAnswering.css'

function QuestionAnswering({ documentId }) {
  const [question, setQuestion] = useState('')
  const [answer, setAnswer] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [history, setHistory] = useState([])

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
      setHistory([...history, { question, answer: response.data.answer }])
      setQuestion('')
    } catch (err) {
      setError(err.response?.data?.error || err.message || 'Failed to get answer')
      console.error('Ask error:', err)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="qa-container">
      <div className="qa-section">
        <h2>Ask Questions About Your Document</h2>
        
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
            {loading ? '⏳ Thinking...' : '🔍 Ask'}
          </button>
        </form>

        {error && <div className="error-message">{error}</div>}

        {answer && (
          <div className="answer-section">
            <h3>Answer</h3>
            <div className="answer-box">
              {answer}
            </div>
          </div>
        )}
      </div>

      {history.length > 0 && (
        <div className="history-section">
          <h3>History</h3>
          <div className="history-list">
            {history.map((item, index) => (
              <div key={index} className="history-item">
                <p className="history-question"><strong>Q:</strong> {item.question}</p>
                <p className="history-answer"><strong>A:</strong> {item.answer}</p>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

export default QuestionAnswering
