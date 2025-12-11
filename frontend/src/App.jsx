import React, { useState } from 'react'
import axios from 'axios'
import DocumentUpload from './components/DocumentUpload'
import QuestionAnswering from './components/QuestionAnswering'
import './App.css'

function App() {
  const [documentId, setDocumentId] = useState(null)
  const [documentName, setDocumentName] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

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
    setError(null)
  }

  return (
    <div className="app-container">
      <h1>📄 Document Q&A Assistant</h1>
      
      {error && <div className="error-message">{error}</div>}
      
      {!documentId ? (
        <DocumentUpload onUpload={handleDocumentUpload} loading={loading} />
      ) : (
        <>
          <div className="document-info">
            <p>✅ Loaded: <strong>{documentName}</strong></p>
            <button onClick={handleReset} className="reset-btn">Load Different Document</button>
          </div>
          <QuestionAnswering documentId={documentId} />
        </>
      )}
    </div>
  )
}

export default App
