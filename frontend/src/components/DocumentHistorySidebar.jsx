import React from 'react'
import './DocumentHistorySidebar.css'

function formatTimestamp(value) {
  if (!value) {
    return 'No questions yet'
  }

  const date = new Date(value.replace(' ', 'T'))

  if (Number.isNaN(date.getTime())) {
    return value
  }

  return date.toLocaleString([], {
    month: 'short',
    day: 'numeric',
    hour: 'numeric',
    minute: '2-digit',
  })
}

function DocumentHistorySidebar({
  documents,
  selectedDocumentId,
  onSelectDocument,
  onCreateNew,
  loading,
}) {
  return (
    <aside className="history-sidebar">
      <div className="history-sidebar-header">
        <div>
          <p className="history-sidebar-eyebrow">Navigation</p>
          <h2>Chats</h2>
        </div>
        <button type="button" className="new-chat-btn" onClick={onCreateNew}>
          New Chat
        </button>
      </div>

      <div className="history-sidebar-list">
        {loading ? (
          <p className="history-sidebar-empty">Loading chats...</p>
        ) : documents.length === 0 ? (
          <p className="history-sidebar-empty">
            No chats yet. Upload a document to start one.
          </p>
        ) : (
          documents.map((document) => (
            <button
              key={document.document_id}
              type="button"
              className={`history-document-card ${
                selectedDocumentId === document.document_id ? 'selected' : ''
              }`}
              onClick={() => onSelectDocument(document)}
            >
              <span className="history-document-name">{document.filename}</span>
              <span className="history-document-meta">
                {document.question_count} question{document.question_count === 1 ? '' : 's'}
              </span>
              <span className="history-document-time">
                {formatTimestamp(document.last_question_at || document.created_at)}
              </span>
            </button>
          ))
        )}
      </div>
    </aside>
  )
}

export default DocumentHistorySidebar
