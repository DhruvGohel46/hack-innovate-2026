import React, { useState, useRef } from 'react';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faCloudUploadAlt, faVideo, faCheckCircle, faTimesCircle } from '@fortawesome/free-solid-svg-icons';

function VideoUpload({ onUpload, config }) {
  const [dragActive, setDragActive] = useState(false);
  const [selectedFile, setSelectedFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const fileInputRef = useRef(null);

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(e.type === "dragenter" || e.type === "dragover");
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    
    if (e.dataTransfer.files?.[0]) {
      handleFile(e.dataTransfer.files[0]);
    }
  };

  const handleChange = (e) => {
    e.preventDefault();
    if (e.target.files?.[0]) {
      handleFile(e.target.files[0]);
    }
  };

  const handleFile = (file) => {
    if (file.type.startsWith('video/')) {
      setSelectedFile(file);
    } else {
      alert('Please upload a valid video file');
    }
  };

  const handleUploadClick = async () => {
    if (!selectedFile) return;
    
    setUploading(true);
    setTimeout(() => {
      onUpload(selectedFile);
    }, 800);
  };

  const handleRemoveFile = () => {
    setSelectedFile(null);
    if (fileInputRef.current) fileInputRef.current.value = '';
  };

  return (
    <div className="upload-container">
      <div
        className="upload-card"
      >
        <h2
        >
          Upload Wagon Footage
        </h2>
        <p className="upload-subtitle">Drag and drop your video or click to browse</p>

        <div
          className={`dropzone ${dragActive ? 'active' : ''} ${selectedFile ? 'has-file' : ''}`}
          onDragEnter={handleDrag}
          onDragLeave={handleDrag}
          onDragOver={handleDrag}
          onDrop={handleDrop}
          onClick={() => !selectedFile && fileInputRef.current?.click()}
        >
          <input
            ref={fileInputRef}
            type="file"
            accept="video/*"
            onChange={handleChange}
            style={{ display: 'none' }}
          />

          <div>
            {selectedFile ? (
              <div
              >
                <div
                >
                  <FontAwesomeIcon icon={faCheckCircle} className="upload-icon success" />
                </div>
                <p className="file-name">{selectedFile.name}</p>
                <p className="file-size">{(selectedFile.size / 1024 / 1024).toFixed(2)} MB</p>
                <button
                  className="remove-file-btn"
                  onClick={(e) => { e.stopPropagation(); handleRemoveFile(); }}
                >
                  <FontAwesomeIcon icon={faTimesCircle} /> Remove
                </button>
              </div>
            ) : (
              <div
              >
                <FontAwesomeIcon icon={faCloudUploadAlt} className="upload-icon" />
                <p>Drop video file here</p>
                <p className="supported-formats">Supported: MP4, AVI, MOV, MKV</p>
              </div>
            )}
          </div>
        </div>

        <div>
          {selectedFile && (
            <button
              className="upload-button"
              onClick={handleUploadClick}
              disabled={uploading}
            >
              <FontAwesomeIcon icon={faVideo} />
              {uploading ? ' Processing...' : ' Start Analysis'}
            </button>
          )}
        </div>
      </div>
    </div>
  );
}

export default VideoUpload;
