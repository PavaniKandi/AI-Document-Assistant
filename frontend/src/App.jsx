import React, { useEffect, useState } from 'react'
import axios from 'axios'
import DocumentUpload from './components/DocumentUpload'
import DocumentHistorySidebar from './components/DocumentHistorySidebar'
import QuestionAnswering from './components/QuestionAnswering'
import QuestionHistoryPanel from './components/QuestionHistoryPanel'
import './App.css'

function App() {
  const [user, setUser] = useState(null)
  const [authMode, setAuthMode] = useState('login')
  const [authEmail, setAuthEmail] = useState('')
  const [authPassword, setAuthPassword] = useState('')
  const [authLoading, setAuthLoading] = useState(true)
  const [documents, setDocuments] = useState([])
  const [documentId, setDocumentId] = useState(null)
  const [documentName, setDocumentName] = useState(null)
  const [history, setHistory] = useState([])
  const [loading, setLoading] = useState(false)
  const [sidebarLoading, setSidebarLoading] = useState(false)
  const [error, setError] = useState(null)

  const loadDocuments = async (preferredDocumentId = null) => {
    if (!user) {
      return
    }

    setSidebarLoading(true)

    try {
      const response = await axios.get('/api/documents', { withCredentials: true })
      const nextDocuments = response.data.documents || []
      setDocuments(nextDocuments)

      const nextSelectedDocument =
        nextDocuments.find((item) => item.document_id === preferredDocumentId) ||
        nextDocuments.find((item) => item.document_id === documentId) ||
        null

      if (nextSelectedDocument) {
        setDocumentId(nextSelectedDocument.document_id)
        setDocumentName(nextSelectedDocument.filename)
      } else {
        setDocumentId(null)
        setDocumentName(null)
        setHistory([])
      }
    } catch (err) {
      setError(err.response?.data?.error || err.message || 'Failed to load documents')
    } finally {
      setSidebarLoading(false)
    }
  }

  const loadHistory = async (nextDocumentId) => {
    if (!nextDocumentId) {
      setHistory([])
      return
    }

    try {
      const response = await axios.get(`/api/history/${nextDocumentId}`, {
        withCredentials: true,
      })
      setHistory(response.data.history || [])
    } catch (err) {
      setHistory([])
      setError(err.response?.data?.error || err.message || 'Failed to load history')
    }
  }

  useEffect(() => {
    const loadSession = async () => {
      try {
        const response = await axios.get('/api/auth/me', { withCredentials: true })
        setUser(response.data.user)
      } catch (err) {
        console.error('Session error:', err)
      } finally {
        setAuthLoading(false)
      }
    }

    loadSession()
  }, [])

  useEffect(() => {
    if (!user) {
      return
    }

    loadDocuments()
  }, [user])

  useEffect(() => {
    loadHistory(documentId)
  }, [documentId])

  const handleAuthSubmit = async (e) => {
    e.preventDefault()
    setError(null)
    setAuthLoading(true)

    try {
      const endpoint = authMode === 'login' ? '/api/auth/login' : '/api/auth/register'
      const response = await axios.post(
        endpoint,
        { email: authEmail, password: authPassword },
        { withCredentials: true }
      )

      setUser(response.data.user)
      setAuthMode('login')
      setAuthPassword('')
      setDocuments([])
      setHistory([])
    } catch (err) {
      setError(err.response?.data?.error || err.message || 'Authentication failed')
    } finally {
      setAuthLoading(false)
    }
  }

  const handleLogout = async () => {
    try {
      await axios.post('/api/auth/logout', {}, { withCredentials: true })
    } catch (err) {
      console.error('Logout error:', err)
    }

    setUser(null)
    setAuthMode('login')
    setAuthEmail('')
    setAuthPassword('')
    setDocuments([])
    setDocumentId(null)
    setDocumentName(null)
    setHistory([])
    setError(null)
  }

  const handleDocumentUpload = async (file) => {
    setLoading(true)
    setError(null)

    const formData = new FormData()
    formData.append('file', file)

    try {
      const response = await axios.post('/api/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
          Accept: 'application/json',
        },
        withCredentials: true,
      })

      setDocumentId(response.data.document_id)
      setDocumentName(response.data.filename)
      setHistory([])
      await loadDocuments(response.data.document_id)
    } catch (err) {
      setError(err.response?.data?.error || err.message || 'Failed to upload document')
    } finally {
      setLoading(false)
    }
  }

  const handleReset = () => {
    setDocumentId(null)
    setDocumentName(null)
    setHistory([])
    setError(null)
  }

  const handleSelectDocument = (document) => {
    setError(null)
    setDocumentId(document.document_id)
    setDocumentName(document.filename)
  }

  const handleHistoryUpdate = async () => {
    await loadHistory(documentId)
    await loadDocuments(documentId)
  }

  if (authLoading) {
    return (
      <div className="app-container auth-page">
        <div className="auth-card">
          <h1>Document Q&amp;A</h1>
          <p className="auth-subtitle">Loading session...</p>
        </div>
      </div>
    )
  }

  if (!user) {
    return (
      <div className="app-container auth-page">
        <div className="auth-card">
          <h1>Document Q&amp;A</h1>
          <p className="auth-subtitle">
            Sign in to upload files and keep your own chat history.
          </p>

          {error && <div className="error-message auth-error">{error}</div>}

          <form onSubmit={handleAuthSubmit} className="auth-form">
            <input
              type="email"
              value={authEmail}
              onChange={(e) => setAuthEmail(e.target.value)}
              placeholder="Email"
              className="auth-input"
              required
            />
            <input
              type="password"
              value={authPassword}
              onChange={(e) => setAuthPassword(e.target.value)}
              placeholder="Password"
              className="auth-input"
              required
            />
            <button type="submit" className="auth-btn">
              {authMode === 'login' ? 'Sign In' : 'Create Account'}
            </button>
          </form>

          <button
            type="button"
            className="auth-toggle"
            onClick={() => {
              setAuthMode(authMode === 'login' ? 'register' : 'login')
              setError(null)
            }}
          >
            {authMode === 'login' ? 'Need an account? Register' : 'Already have an account? Sign in'}
          </button>
        </div>
      </div>
    )
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
              <p className="app-kicker">Document Q&amp;A</p>
              <h1>Workspace</h1>
            </div>
            <div className="app-header-actions">
              <p className="app-current-document">
                Signed in as <strong>{user.email}</strong>
              </p>
              <button onClick={handleLogout} className="reset-btn">Log Out</button>
            </div>
          </div>

          {error && <div className="error-message">{error}</div>}

          {!documentId ? (
            <div className="workspace-empty">
              <DocumentUpload onUpload={handleDocumentUpload} loading={loading} />
            </div>
          ) : (
            <>
              <div className="document-info">
                <p>Active document: <strong>{documentName}</strong></p>
                <button onClick={handleReset} className="reset-btn">New Chat</button>
              </div>
              <QuestionAnswering documentId={documentId} onHistoryUpdate={handleHistoryUpdate} />
            </>
          )}
        </main>

        <QuestionHistoryPanel history={history} documentName={documentName} />
      </div>
    </div>
  )
}

export default App
