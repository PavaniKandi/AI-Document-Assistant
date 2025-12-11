import React, { useState } from 'react'
import './DocumentUpload.css'

function DocumentUpload({ onUpload, loading }) {
  const [dragging, setDragging] = useState(false)

  const handleDragOver = (e) => {
    e.preventDefault()
    setDragging(true)
  }

  const handleDragLeave = () => {
    setDragging(false)
  }

  const handleDrop = (e) => {
    e.preventDefault()
    setDragging(false)
    const file = e.dataTransfer.files[0]
    if (file) {
      onUpload(file)
    }
  }

  const handleFileSelect = (e) => {
    const file = e.target.files[0]
    if (file) {
      onUpload(file)
    }
  }

  return (
    <div className="upload-container">
      <div
        className={`upload-area ${dragging ? 'dragging' : ''}`}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
      >
        <div className="upload-content">
          <div className="upload-icon">📁</div>
          <h2>Upload Your Document</h2>
          <p>Drag and drop your PDF, TXT, or DOCX file here</p>
          <p className="or-text">or</p>
          
          <label className="file-input-label">
            <input
              type="file"
              accept=".pdf,.txt,.docx,.doc"
              onChange={handleFileSelect}
              disabled={loading}
              className="file-input"
            />
            <span className="browse-btn">{loading ? 'Uploading...' : 'Browse Files'}</span>
          </label>
          
          <p className="file-types">Supported: PDF, TXT, DOCX</p>
        </div>
      </div>
    </div>
  )
}

export default DocumentUpload
