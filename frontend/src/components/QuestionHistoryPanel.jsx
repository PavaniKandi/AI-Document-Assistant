import React from 'react'
import './QuestionHistoryPanel.css'

function formatHistoryTime(value) {
  if (!value) {
    return null
  }

  const date = new Date(value.replace(' ', 'T'))

  if (Number.isNaN(date.getTime())) {
    return value
  }

  return date.toLocaleString([], {
    month: 'short',
    day: 'numeric',
    hour: 'numeric',
    minute: '2-digit'
  })
}

function QuestionHistoryPanel({ history, documentName }) {
  return (
    <aside className="question-history-panel">
      <div className="question-history-header">
        <p className="question-history-eyebrow">Selected Chat</p>
        <h3>History</h3>
        <p className="question-history-subtitle">
          {documentName || 'Select a chat from the left rail to inspect its answers.'}
        </p>
      </div>

      {history.length === 0 ? (
        <div className="question-history-empty">
          <p>No saved questions yet.</p>
          <p>Ask something in the middle panel and it will appear here.</p>
        </div>
      ) : (
        <div className="question-history-list">
          {history.map((item, index) => (
            <div key={`${item.question}-${index}`} className="question-history-item">
              <p className="question-history-question"><strong>Q:</strong> {item.question}</p>
              <p className="question-history-answer"><strong>A:</strong> {item.answer}</p>
              {item.created_at && (
                <p className="question-history-time">{formatHistoryTime(item.created_at)}</p>
              )}
            </div>
          ))}
        </div>
      )}
    </aside>
  )
}

export default QuestionHistoryPanel
