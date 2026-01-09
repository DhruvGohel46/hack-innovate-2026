import React, { useState } from 'react';
import { motion } from 'framer-motion';
import MetricsCard from './MetricsCard';
import ResultsTable from './ResultsTable';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faFileVideo, faFileCsv, faDownload } from '@fortawesome/free-solid-svg-icons';

function Dashboard({ jobId }) {
  const [results] = useState({
    wagonCount: 12,
    framesProcessed: 1248,
    avgBlurScore: 0.18,
    ocrAccuracy: 96.2,
    fps: 52,
    detections: [
      { frame: 45, timestamp: '1.50', wagonId: 'WG-10245', confidence: '0.94', blurClass: 'Low' },
      { frame: 128, timestamp: '4.27', wagonId: 'WG-10382', confidence: '0.91', blurClass: 'Medium' },
      { frame: 234, timestamp: '7.80', wagonId: 'WG-10519', confidence: '0.89', blurClass: 'Low' },
      { frame: 456, timestamp: '15.20', wagonId: 'WG-10656', confidence: '0.92', blurClass: 'Medium' },
      { frame: 589, timestamp: '19.63', wagonId: 'WG-10793', confidence: '0.95', blurClass: 'Low' },
    ]
  });

  const handleDownload = (type) => {
    alert(`${type} download would start here (connect to backend API)`);
  };

  return (
    <motion.div
      className="dashboard"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.6 }}
    >
      <motion.h2
        initial={{ x: -20, opacity: 0 }}
        animate={{ x: 0, opacity: 1 }}
      >
        Analysis Results
      </motion.h2>

      <div className="metrics-grid">
        <MetricsCard 
          title="Wagons Detected" 
          value={results.wagonCount} 
          delta="+2"
          icon="train"
        />
        <MetricsCard 
          title="Frames Processed" 
          value={results.framesProcessed} 
          delta="100%"
          icon="image"
        />
        <MetricsCard 
          title="Avg Blur Score" 
          value={results.avgBlurScore.toFixed(2)} 
          delta="↓ 65%"
          icon="eye"
        />
        <MetricsCard 
          title="OCR Accuracy" 
          value={`${results.ocrAccuracy}%`} 
          delta="↑ 2.1%"
          icon="check"
        />
        <MetricsCard 
          title="Processing FPS" 
          value={results.fps} 
          delta="Real-time"
          icon="tachometer-alt"
        />
      </div>

      <div className="download-section">
        <motion.button
          className="download-btn primary"
          onClick={() => handleDownload('Video')}
          whileHover={{ scale: 1.05, boxShadow: '0 8px 25px rgba(59,130,246,0.5)' }}
          whileTap={{ scale: 0.95 }}
        >
          <FontAwesomeIcon icon={faFileVideo} />
          Download Processed Video
        </motion.button>

        <motion.button
          className="download-btn secondary"
          onClick={() => handleDownload('CSV Report')}
          whileHover={{ scale: 1.05, boxShadow: '0 8px 25px rgba(59,130,246,0.3)' }}
          whileTap={{ scale: 0.95 }}
        >
          <FontAwesomeIcon icon={faFileCsv} />
          Download CSV Report
        </motion.button>
      </div>

      <ResultsTable data={results.detections} />
    </motion.div>
  );
}

export default Dashboard;

