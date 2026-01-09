import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import {
  faTrain, faCloudUploadAlt, faSpinner, faCheckCircle,
  faImage, faEye,
  faFileVideo, faFileCsv
} from '@fortawesome/free-solid-svg-icons';
import './App.css';

// Simplified all-in-one App
function App() {
  const [view, setView] = useState('upload');
  const [file, setFile] = useState(null);
  const [progress, setProgress] = useState(0);

  const handleFileSelect = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile) setFile(selectedFile);
  };

  const startProcessing = () => {
    setView('processing');
    const interval = setInterval(() => {
      setProgress(prev => {
        if (prev >= 100) {
          clearInterval(interval);
          setTimeout(() => setView('results'), 500);
          return 100;
        }
        return prev + 5;
      });
    }, 150);
  };

  return (
    <div className="app-container">
      {/* Main Content */}
      <main className="main-content">
        <motion.header
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="header"
        >
          <div className="header-content">
            <FontAwesomeIcon icon={faTrain} className="header-icon" />
            <h1>RailVision AI</h1>
            <span className="tagline">Advanced Wagon Monitoring System</span>
          </div>
        </motion.header>

        <AnimatePresence mode="wait">
          {/* Upload View */}
          {view === 'upload' && (
            <motion.div
              key="upload"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="upload-container"
            >
              <div className="upload-card">
                <h2>Upload Wagon Footage</h2>
                <p className="upload-subtitle">Select your video file</p>

                <div className="dropzone">
                  <FontAwesomeIcon
                    icon={file ? faCheckCircle : faCloudUploadAlt}
                    className={`upload-icon ${file ? 'success' : ''}`}
                  />
                  <input
                    type="file"
                    accept="video/*"
                    onChange={handleFileSelect}
                    style={{ display: 'none' }}
                    id="fileInput"
                  />
                  <label htmlFor="fileInput" style={{ cursor: 'pointer' }}>
                    {file ? (
                      <>
                        <p className="file-name">{file.name}</p>
                        <p className="file-size">{(file.size / 1024 / 1024).toFixed(2)} MB</p>
                      </>
                    ) : (
                      <>
                        <p>Click to select video</p>
                        <p className="supported-formats">MP4, AVI, MOV, MKV</p>
                      </>
                    )}
                  </label>
                </div>

                {file && (
                  <motion.button
                    className="upload-button"
                    onClick={startProcessing}
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    whileHover={{ scale: 1.05 }}
                  >
                    Start Analysis
                  </motion.button>
                )}
              </div>
            </motion.div>
          )}

          {/* Processing View */}
          {view === 'processing' && (
            <motion.div
              key="processing"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="processing-container"
            >
              <div className="processing-card">
                <motion.div
                  animate={{ rotate: 360 }}
                  transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
                >
                  <FontAwesomeIcon icon={faSpinner} className="processing-spinner" />
                </motion.div>
                <h2>Processing Video</h2>
                <p className="processing-stage">AI Analysis in Progress...</p>

                <div className="progress-bar-container">
                  <motion.div
                    className="progress-bar"
                    style={{ width: `${progress}%` }}
                  />
                </div>
                <p className="progress-text">{progress}% Complete</p>
              </div>
            </motion.div>
          )}

          {/* Results View */}
          {view === 'results' && (
            <motion.div
              key="results"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="dashboard"
            >
              <h2>Analysis Results</h2>

              <div className="metrics-grid">
                <motion.div
                  className="metrics-card"
                  whileHover={{ scale: 1.05 }}
                >
                  <div className="metrics-icon">
                    <FontAwesomeIcon icon={faTrain} />
                  </div>
                  <div className="metrics-content">
                    <p className="metrics-title">Wagons Detected</p>
                    <h3 className="metrics-value">12</h3>
                    <span className="metrics-delta">+2</span>
                  </div>
                </motion.div>

                <motion.div
                  className="metrics-card"
                  whileHover={{ scale: 1.05 }}
                >
                  <div className="metrics-icon">
                    <FontAwesomeIcon icon={faImage} />
                  </div>
                  <div className="metrics-content">
                    <p className="metrics-title">Frames Processed</p>
                    <h3 className="metrics-value">1248</h3>
                    <span className="metrics-delta">100%</span>
                  </div>
                </motion.div>

                <motion.div
                  className="metrics-card"
                  whileHover={{ scale: 1.05 }}
                >
                  <div className="metrics-icon">
                    <FontAwesomeIcon icon={faEye} />
                  </div>
                  <div className="metrics-content">
                    <p className="metrics-title">OCR Accuracy</p>
                    <h3 className="metrics-value">96.2%</h3>
                    <span className="metrics-delta">↑ 2.1%</span>
                  </div>
                </motion.div>
              </div>

              {/* Blurred Frames Section */}
              <motion.div
                className="results-section"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.2 }}
              >
                <h3>Blurred Frames Detected</h3>
                <div className="frames-grid">
                  <div className="frame-item">
                    <div className="frame-placeholder">Frame 45</div>
                    <p>Blur Score: 0.85</p>
                  </div>
                  <div className="frame-item">
                    <div className="frame-placeholder">Frame 128</div>
                    <p>Blur Score: 0.78</p>
                  </div>
                  <div className="frame-item">
                    <div className="frame-placeholder">Frame 234</div>
                    <p>Blur Score: 0.92</p>
                  </div>
                </div>
              </motion.div>

              {/* Deblurred Frames Section */}
              <motion.div
                className="results-section"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.4 }}
              >
                <h3>Deblurred Frames</h3>
                <div className="frames-grid">
                  <div className="frame-item">
                    <div className="frame-placeholder deblurred">Frame 45</div>
                    <p>Deblurred Successfully</p>
                  </div>
                  <div className="frame-item">
                    <div className="frame-placeholder deblurred">Frame 128</div>
                    <p>Deblurred Successfully</p>
                  </div>
                  <div className="frame-item">
                    <div className="frame-placeholder deblurred">Frame 234</div>
                    <p>Deblurred Successfully</p>
                  </div>
                </div>
              </motion.div>

              {/* Extracted Text Section */}
              <motion.div
                className="results-section"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.6 }}
              >
                <h3>Extracted Text (OCR)</h3>
                <div className="ocr-results">
                  <div className="ocr-item">
                    <strong>Wagon ID:</strong> WG-10245
                    <br />
                    <strong>Confidence:</strong> 94%
                  </div>
                  <div className="ocr-item">
                    <strong>Wagon ID:</strong> WG-10382
                    <br />
                    <strong>Confidence:</strong> 91%
                  </div>
                  <div className="ocr-item">
                    <strong>Wagon ID:</strong> WG-10519
                    <br />
                    <strong>Confidence:</strong> 89%
                  </div>
                </div>
              </motion.div>

              <div className="download-section">
                <motion.button
                  className="download-btn primary"
                  whileHover={{ scale: 1.05 }}
                  onClick={() => alert('Video download')}
                >
                  <FontAwesomeIcon icon={faFileVideo} />
                  Download Video
                </motion.button>
                <motion.button
                  className="download-btn secondary"
                  whileHover={{ scale: 1.05 }}
                  onClick={() => alert('CSV download')}
                >
                  <FontAwesomeIcon icon={faFileCsv} />
                  Download Report
                </motion.button>
              </div>

              <button
                onClick={() => { setView('upload'); setFile(null); setProgress(0); }}
                style={{
                  marginTop: '2rem',
                  padding: '0.75rem 1.5rem',
                  background: 'rgba(59,130,246,0.2)',
                  color: '#60A5FA',
                  border: '1px solid #3B82F6',
                  borderRadius: '8px',
                  cursor: 'pointer',
                  fontSize: '1rem'
                }}
              >
                Upload New Video
              </button>
            </motion.div>
          )}
        </AnimatePresence>
      </main>
    </div>
  );
}

export default App;
