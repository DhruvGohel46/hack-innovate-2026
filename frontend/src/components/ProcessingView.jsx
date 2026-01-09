import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faSpinner, faCheckCircle, faClock } from '@fortawesome/free-solid-svg-icons';

function ProcessingView({ videoFile, config, onComplete }) {
  const [progress, setProgress] = useState(0);
  const [currentStage, setCurrentStage] = useState('Initializing');

  const stages = [
    'Initializing AI Models',
    'Reading Video & Blur Classification',
    'Enhancing Low-Light Frames',
    'AI Deblurring Medium Frames',
    'Running YOLO Detection',
    'OCR Text Extraction',
    'Finalizing Results'
  ];

  useEffect(() => {
    const timer = setInterval(() => {
      setProgress(prev => {
        if (prev >= 100) {
          clearInterval(timer);
          setTimeout(() => onComplete('demo-job-123'), 1000);
          return 100;
        }
        const newProgress = prev + 2;
        const stageIndex = Math.floor((newProgress / 100) * stages.length);
        setCurrentStage(stages[Math.min(stageIndex, stages.length - 1)]);
        return newProgress;
      });
    }, 100);

    return () => clearInterval(timer);
  }, [onComplete, stages]);

  return (
    <div className="processing-container">
      <motion.div
        className="processing-card"
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.5 }}
      >
        <motion.div
          className="spinner-container"
          animate={{ rotate: 360 }}
          transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
        >
          <FontAwesomeIcon icon={faSpinner} className="processing-spinner" />
        </motion.div>

        <motion.h2
          animate={{ opacity: [1, 0.7, 1] }}
          transition={{ duration: 1.5, repeat: Infinity }}
        >
          Processing Video
        </motion.h2>
        
        <motion.p 
          className="processing-stage"
          key={currentStage}
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3 }}
        >
          {currentStage}
        </motion.p>

        <div className="progress-bar-container">
          <motion.div
            className="progress-bar"
            initial={{ width: 0 }}
            animate={{ width: `${progress}%` }}
            transition={{ duration: 0.3 }}
          />
        </div>
        
        <motion.p 
          className="progress-text"
          animate={{ scale: [1, 1.05, 1] }}
          transition={{ duration: 0.5, repeat: Infinity }}
        >
          {progress}% Complete
        </motion.p>

        <div className="stages-list">
          {stages.map((stage, idx) => {
            const stageProgress = (idx / stages.length) * 100;
            const isComplete = progress > stageProgress;
            const isCurrent = currentStage === stage;

            return (
              <motion.div
                key={idx}
                className={`stage-item ${isComplete ? 'complete' : ''} ${isCurrent ? 'current' : ''}`}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: idx * 0.1 }}
                whileHover={{ x: 5, backgroundColor: 'rgba(59,130,246,0.15)' }}
              >
                <motion.div
                  animate={isCurrent ? { rotate: 360 } : {}}
                  transition={{ duration: 1, repeat: isCurrent ? Infinity : 0 }}
                >
                  <FontAwesomeIcon 
                    icon={isComplete ? faCheckCircle : faClock} 
                    className={`stage-icon ${isComplete ? 'success' : ''}`}
                  />
                </motion.div>
                <span>{stage}</span>
              </motion.div>
            );
          })}
        </div>
      </motion.div>
    </div>
  );
}

export default ProcessingView;
