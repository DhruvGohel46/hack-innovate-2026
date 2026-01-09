import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { 
  faTrain, faCloudUploadAlt, faSpinner, faCheckCircle,
  faImage, faFileVideo, faEye, faArrowLeft,
  faTachometerAlt, faChartLine, faTimes
} from '@fortawesome/free-solid-svg-icons';
import { processFrame, processVideo, getProcessingStatus, getResult } from './services/api';
import './App.css';

function App() {
  const [view, setView] = useState('upload');
  const [imageFile, setImageFile] = useState(null);
  const [videoFile, setVideoFile] = useState(null);
  const [fileType, setFileType] = useState(null); // 'image' or 'video'
  const [progress, setProgress] = useState(0);
  const [jobId, setJobId] = useState(null);
  const [results, setResults] = useState(null);
  const [error, setError] = useState(null);
  const [processing, setProcessing] = useState(false);

  const handleImageSelect = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile) {
      if (selectedFile.type.startsWith('image/')) {
        setImageFile(selectedFile);
        setVideoFile(null); // Clear video if image is selected
        setError(null);
      } else {
        setError('Please select a valid image file (PNG, JPG, JPEG)');
        setImageFile(null);
      }
    }
  };

  const handleVideoSelect = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile) {
      if (selectedFile.type.startsWith('video/')) {
        setVideoFile(selectedFile);
        setImageFile(null); // Clear image if video is selected
        setError(null);
      } else {
        setError('Please select a valid video file (MP4, AVI, MOV, MKV)');
        setVideoFile(null);
      }
    }
  };

  const triggerImageInput = () => {
    document.getElementById('imageInput').click();
  };

  const triggerVideoInput = () => {
    document.getElementById('videoInput').click();
  };

  const removeImageFile = (e) => {
    e.stopPropagation();
    setImageFile(null);
    document.getElementById('imageInput').value = '';
  };

  const removeVideoFile = (e) => {
    e.stopPropagation();
    setVideoFile(null);
    document.getElementById('videoInput').value = '';
  };

  const startProcessing = async (type) => {
    const file = type === 'image' ? imageFile : videoFile;
    
    if (!file) {
      setError(`Please select a ${type === 'image' ? 'image' : 'video'} file first`);
      return;
    }

    setFileType(type);
    setProcessing(true);
    setView('processing');
    setProgress(0);
    setError(null);

    try {
      let response;
      if (type === 'image') {
        response = await processFrame(file);
      } else {
        response = await processVideo(file);
      }

      const newJobId = response.data.job_id;
      setJobId(newJobId);

      // Poll for status
      pollStatus(newJobId);
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to start processing');
      setProcessing(false);
      setView('upload');
    }
  };

  const pollStatus = async (jobId) => {
    const maxAttempts = 300; // 5 minutes max (1 second intervals)
    let attempts = 0;

    const interval = setInterval(async () => {
      attempts++;
      
      try {
        const statusResponse = await getProcessingStatus(jobId);
        const status = statusResponse.data.status;

        if (status === 'completed') {
          clearInterval(interval);
          // Get full results
          const resultResponse = await getResult(jobId);
          setResults(resultResponse.data);
          setProgress(100);
          setProcessing(false);
          setTimeout(() => setView('results'), 500);
        } else if (status === 'error') {
          clearInterval(interval);
          setError(statusResponse.data.error || 'Processing failed');
          setProcessing(false);
          setView('upload');
        } else if (status === 'processing') {
          // Simulate progress (we don't have real progress from backend)
          setProgress(prev => Math.min(prev + 2, 95));
        }

        if (attempts >= maxAttempts) {
          clearInterval(interval);
          setError('Processing timeout');
          setProcessing(false);
          setView('upload');
        }
      } catch (err) {
        clearInterval(interval);
        setError(err.response?.data?.error || 'Failed to get status');
        setProcessing(false);
        setView('upload');
      }
    }, 1000);
  };

  const resetView = () => {
    setView('upload');
    setImageFile(null);
    setVideoFile(null);
    setFileType(null);
    setProgress(0);
    setJobId(null);
    setResults(null);
    setError(null);
    setProcessing(false);
    // Reset file inputs
    document.getElementById('imageInput').value = '';
    document.getElementById('videoInput').value = '';
  };

  return (
    <div className="app-container">
      <main className="main-content">
        <motion.header
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="header"
        >
          <div className="header-content">
            <FontAwesomeIcon icon={faTrain} className="header-icon" />
            <h1>Video Restoration AI</h1>
            <span className="tagline">Deblur & Enhance Your Images and Videos</span>
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
              <div className="upload-section">
                <h2>Upload Files</h2>
                <p className="upload-subtitle-main">
                  Select an image frame or video to process and enhance
                </p>

                <div className="upload-options">
                  {/* Image Upload Section */}
                  <div className="upload-option-card">
                    <div className="option-header">
                      <FontAwesomeIcon icon={faImage} className="option-icon" />
                      <h3>Single Frame (Image)</h3>
                    </div>
                    <p className="option-description">
                      Upload a single image to deblur and enhance
                    </p>
                    
                    <input 
                      type="file" 
                      accept="image/*"
                      onChange={handleImageSelect}
                      style={{ display: 'none' }}
                      id="imageInput"
                    />
                    
                    <div 
                      className={`dropzone option-dropzone ${imageFile ? 'has-file' : ''}`}
                      onClick={triggerImageInput}
                    >
                      {imageFile ? (
                        <div className="file-selected">
                          <FontAwesomeIcon icon={faCheckCircle} className="success-icon" />
                          <p className="file-name">{imageFile.name}</p>
                          <p className="file-size">
                            {(imageFile.size / 1024 / 1024).toFixed(2)} MB
                          </p>
                          <button 
                            className="remove-file-btn"
                            onClick={removeImageFile}
                            type="button"
                            title="Remove file"
                          >
                            <FontAwesomeIcon icon={faTimes} /> Remove
                          </button>
                        </div>
                      ) : (
                        <div className="file-empty">
                          <FontAwesomeIcon icon={faCloudUploadAlt} className="upload-icon" />
                          <p>Click to select image</p>
                          <p className="supported-formats">PNG, JPG, JPEG</p>
                        </div>
                      )}
                    </div>

                    {imageFile && (
                      <motion.button
                        className="process-button image-button"
                        onClick={() => startProcessing('image')}
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        whileHover={{ scale: 1.05 }}
                        disabled={processing}
                      >
                        <FontAwesomeIcon icon={faSpinner} spin={processing} />
                        Process Image
                      </motion.button>
                    )}
                  </div>

                  {/* Video Upload Section */}
                  <div className="upload-option-card">
                    <div className="option-header">
                      <FontAwesomeIcon icon={faFileVideo} className="option-icon" />
                      <h3>Video Processing</h3>
                    </div>
                    <p className="option-description">
                      Upload a video to process all frames and view sample results
                    </p>
                    
                    <input 
                      type="file" 
                      accept="video/*"
                      onChange={handleVideoSelect}
                      style={{ display: 'none' }}
                      id="videoInput"
                    />
                    
                    <div 
                      className={`dropzone option-dropzone ${videoFile ? 'has-file' : ''}`}
                      onClick={triggerVideoInput}
                    >
                      {videoFile ? (
                        <div className="file-selected">
                          <FontAwesomeIcon icon={faCheckCircle} className="success-icon" />
                          <p className="file-name">{videoFile.name}</p>
                          <p className="file-size">
                            {(videoFile.size / 1024 / 1024).toFixed(2)} MB
                          </p>
                          <button 
                            className="remove-file-btn"
                            onClick={removeVideoFile}
                            type="button"
                            title="Remove file"
                          >
                            <FontAwesomeIcon icon={faTimes} /> Remove
                          </button>
                        </div>
                      ) : (
                        <div className="file-empty">
                          <FontAwesomeIcon icon={faCloudUploadAlt} className="upload-icon" />
                          <p>Click to select video</p>
                          <p className="supported-formats">MP4, AVI, MOV, MKV</p>
                        </div>
                      )}
                    </div>

                    {videoFile && (
                      <motion.button
                        className="process-button video-button"
                        onClick={() => startProcessing('video')}
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        whileHover={{ scale: 1.05 }}
                        disabled={processing}
                      >
                        <FontAwesomeIcon icon={faSpinner} spin={processing} />
                        Process Video
                      </motion.button>
                    )}
                  </div>
                </div>

                {error && (
                  <motion.div 
                    className="error-message"
                    initial={{ opacity: 0, y: -10 }}
                    animate={{ opacity: 1, y: 0 }}
                  >
                    {error}
                  </motion.div>
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
                <h2>Processing {fileType === 'image' ? 'Image' : 'Video'}</h2>
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
          {view === 'results' && results && (
            <motion.div
              key="results"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="dashboard"
            >
              <button onClick={resetView} className="back-button">
                <FontAwesomeIcon icon={faArrowLeft} /> Back to Upload
              </button>

              <h2>Processing Results</h2>
              
              {fileType === 'image' && results.images && (
                <>
                  {/* Single Frame Results */}
                  <div className="results-section">
                    <h3>Image Comparison</h3>
                    <div className="comparison-container">
                      <div className="comparison-item">
                        <h4>Original (Blur)</h4>
                        <img 
                          src={`data:image/png;base64,${results.images.original}`} 
                          alt="Original"
                          className="comparison-image"
                        />
                        {results.blur_detection && (
                          <div className="blur-info">
                            <p>Blur Level: <strong>{results.blur_detection.level.toUpperCase()}</strong></p>
                            <p>Laplacian Variance: {results.blur_detection.laplacian_variance}</p>
                          </div>
                        )}
                      </div>
                      
                      <div className="comparison-item">
                        <h4>Enhanced</h4>
                        <img 
                          src={`data:image/png;base64,${results.images.enhanced}`} 
                          alt="Enhanced"
                          className="comparison-image"
                        />
                        {results.confidence_level && (
                          <div className="confidence-info">
                            <p><FontAwesomeIcon icon={faTachometerAlt} /> Confidence Level</p>
                            <p className="confidence-value">{results.confidence_level}</p>
                            {results.ocr_result && (
                              <p className="confidence-delta">
                                Improvement: +{results.ocr_result.improvement}
                              </p>
                            )}
                          </div>
                        )}
                      </div>
                    </div>

                    {/* Full Comparison */}
                    {results.images.comparison && (
                      <div className="full-comparison">
                        <h4>Side-by-Side Comparison</h4>
                        <img 
                          src={`data:image/png;base64,${results.images.comparison}`} 
                          alt="Comparison"
                          className="comparison-full"
                        />
                      </div>
                    )}

                    {/* OCR Results */}
                    {results.ocr_result && (
                      <div className="ocr-results-section">
                        <h4>OCR Analysis</h4>
                        <div className="ocr-stats">
                          <div className="ocr-stat">
                            <p>Blur Confidence: {results.ocr_result.blur_confidence}</p>
                          </div>
                          <div className="ocr-stat">
                            <p>Enhanced Confidence: {results.ocr_result.enhanced_confidence}</p>
                          </div>
                          <div className="ocr-stat highlight">
                            <p>Improvement: +{results.ocr_result.improvement}</p>
                          </div>
                        </div>
                      </div>
                    )}
                  </div>
                </>
              )}

              {fileType === 'video' && results.sample_frames && (
                <>
                  {/* Video Results */}
                  <div className="video-summary">
                    <div className="summary-card">
                      <FontAwesomeIcon icon={faFileVideo} />
                      <div>
                        <p className="summary-label">Total Frames</p>
                        <p className="summary-value">{results.total_frames}</p>
                      </div>
                    </div>
                    <div className="summary-card">
                      <FontAwesomeIcon icon={faImage} />
                      <div>
                        <p className="summary-label">Sample Frames Shown</p>
                        <p className="summary-value">{results.processed_frames}</p>
                      </div>
                    </div>
                  </div>

                  {/* Sample Frames */}
                  <div className="results-section">
                    <h3>Sample Frame Comparisons</h3>
                    <div className="frames-grid">
                      {results.sample_frames.map((frame, index) => (
                        <motion.div
                          key={frame.frame_id}
                          className="frame-comparison-card"
                          initial={{ opacity: 0, y: 20 }}
                          animate={{ opacity: 1, y: 0 }}
                          transition={{ delay: index * 0.1 }}
                        >
                          <h4>Frame {frame.frame_number}</h4>
                          <div className="frame-comparison">
                            <div className="frame-side">
                              <p className="frame-label">Before</p>
                              <img 
                                src={`data:image/png;base64,${frame.images.before}`} 
                                alt={`Frame ${frame.frame_number} before`}
                                className="frame-image"
                              />
                              <div className="frame-meta">
                                <span className="blur-badge">{frame.blur_level.toUpperCase()}</span>
                                {frame.ocr_result && (
                                  <span className="confidence-badge">
                                    {frame.ocr_result.blur_confidence}
                                  </span>
                                )}
                              </div>
                            </div>
                            
                            <div className="frame-side">
                              <p className="frame-label">Enhanced</p>
                              <img 
                                src={`data:image/png;base64,${frame.images.enhanced}`} 
                                alt={`Frame ${frame.frame_number} enhanced`}
                                className="frame-image"
                              />
                              <div className="frame-meta">
                                {frame.confidence_level && (
                                  <>
                                    <FontAwesomeIcon icon={faChartLine} />
                                    <span className="confidence-value-badge">
                                      {frame.confidence_level}
                                    </span>
                                  </>
                                )}
                                {frame.ocr_result && (
                                  <span className="improvement-badge">
                                    +{frame.ocr_result.improvement}
                                  </span>
                                )}
                              </div>
                            </div>
                          </div>

                          {/* Full Comparison for this frame */}
                          {frame.images.comparison && (
                            <div className="frame-full-comparison">
                              <img 
                                src={`data:image/png;base64,${frame.images.comparison}`} 
                                alt={`Frame ${frame.frame_number} comparison`}
                                className="frame-comparison-full"
                              />
                            </div>
                          )}

                          {/* OCR Details */}
                          {frame.ocr_result && (
                            <div className="frame-ocr-details">
                              <div className="ocr-detail">
                                <span>Before:</span> {frame.ocr_result.blur_confidence}
                              </div>
                              <div className="ocr-detail">
                                <span>After:</span> {frame.ocr_result.enhanced_confidence}
                              </div>
                              <div className="ocr-detail highlight">
                                <span>Δ:</span> +{frame.ocr_result.improvement}
                              </div>
                            </div>
                          )}
                        </motion.div>
                      ))}
                    </div>
                  </div>
                </>
              )}

              {error && (
                <div className="error-message">{error}</div>
              )}
            </motion.div>
          )}
        </AnimatePresence>
      </main>
    </div>
  );
}

export default App;
