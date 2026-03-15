import React, { useEffect, useState } from 'react'
import axios from 'axios'
import DocumentUpload from './components/DocumentUpload'
import DocumentHistorySidebar from './components/DocumentHistorySidebar'
import QuestionAnswering from './components/QuestionAnswering'
import QuestionHistoryPanel from './components/QuestionHistoryPanel'
import './App.css'

function App() {
  const [documentId, setDocumentId] = useState(null)
  const [documentName, setDocumentName] = useState(null)
  const [documentHistory, setDocumentHistory] = useState([])
  const [documents, setDocuments] = useState([])
  const [loading, setLoading] = useState(false)
  const [sidebarLoading, setSidebarLoading] = useState(true)
  const [error, setError] = useState(null)

  const loadDocuments = async (preferredDocumentId = null) => {
    setSidebarLoading(true)

    try {
      const response = await axios.get('/api/documents')
      const savedDocuments = response.data.documents || []
      setDocuments(savedDocuments)

      const nextSelectedDocument =
        savedDocuments.find((item) => item.document_id === preferredDocumentId) ||
        savedDocuments.find((item) => item.document_id === documentId) ||
        null

      if (nextSelectedDocument) {
        setDocumentId(nextSelectedDocument.document_id)
        setDocumentName(nextSelectedDocument.filename)
      } else if (!preferredDocumentId) {
        setDocumentId(null)
        setDocumentName(null)
        setDocumentHistory([])
      }
    } catch (err) {
      setError(err.response?.data?.error || err.message || 'Failed to load documents')
      console.error('Documents error:', err)
    } finally {
      setSidebarLoading(false)
    }
  }

  const loadHistory = async (nextDocumentId) => {
    try {
      const response = await axios.get(`/api/history/${nextDocumentId}`)
      setDocumentHistory(response.data.history || [])
    } catch (err) {
      setDocumentHistory([])
      setError(err.response?.data?.error || err.message || 'Failed to load history')
      console.error('History error:', err)
    }
  }

  useEffect(() => {
    loadDocuments()
  }, [])

  useEffect(() => {
    if (!documentId) {
      return
    }

    loadHistory(documentId)
  }, [documentId])

  const handleDocumentUpload = async (file) => {
    setLoading(true)
    setError(null)

    const formData = new FormData()
    formData.append('file', file)

    try {
      const response = await axios.post('/api/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
          'Accept': 'application/json'
        },
        withCredentials: false
      })
      
      setDocumentId(response.data.document_id)
      setDocumentName(response.data.filename)
      setDocumentHistory([])
      await loadDocuments(response.data.document_id)
      setError(null)
    } catch (err) {
      setError(err.response?.data?.error || err.message || 'Failed to upload document')
      console.error('Upload error:', err)
    } finally {
      setLoading(false)
    }
  }

  const handleReset = () => {
    setDocumentId(null)
    setDocumentName(null)
    setDocumentHistory([])
    setError(null)
  }

  const handleSelectDocument = async (document) => {
    setError(null)
    setDocumentId(document.document_id)
    setDocumentName(document.filename)
  }

  const handleHistoryUpdate = async () => {
    await loadHistory(documentId)
    await loadDocuments(documentId)
  }

  return (
    <div className="app-container">
      <div className="app-shell">
        <DocumentHistorySidebar
          documents={documents}
          selectedDocumentId={documentId}
          onSelectDocument={handleSelectDocument}
          onCreateNew={handleReset}
          loading={sidebarLoading}
        />

        <main className="app-main">
          <div className="app-header">
            <div>
              <p className="app-kicker">Document Q&A</p>
              <h1>Workspace</h1>
            </div>
            {documentName && (
              <p className="app-current-document">
                Active chat: <strong>{documentName}</strong>
              </p>
            )}
          </div>

          {error && <div className="error-message">{error}</div>}

          {!documentId ? (
            <div className="workspace-empty">
              <DocumentUpload onUpload={handleDocumentUpload} loading={loading} />
            </div>
          ) : (
            <>
              <div className="document-info">
                <p>Ask questions about the selected document.</p>
                <button onClick={handleReset} className="reset-btn">New Chat</button>
              </div>
              <QuestionAnswering
                documentId={documentId}
                onHistoryUpdate={handleHistoryUpdate}
              />
            </>
          )}
        </main>

        <QuestionHistoryPanel history={documentHistory} documentName={documentName} />
      </div>
    </div>
  )
}

export default App
