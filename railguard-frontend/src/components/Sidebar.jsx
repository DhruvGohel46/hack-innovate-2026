import React from 'react';
import { motion } from 'framer-motion';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { 
  faCog, faLightbulb, faBolt, faFont, faBullseye,
  faMicrochip, faCheckCircle, faExclamationTriangle
} from '@fortawesome/free-solid-svg-icons';

function Sidebar({ config, setConfig, systemStatus }) {
  
  const handleConfigChange = (key, value) => {
    setConfig(prev => ({ ...prev, [key]: value }));
  };

  const modules = [
    { key: 'enableBlurDetect', label: 'Blur Detection', icon: faBullseye },
    { key: 'enableEnhance', label: 'Night Enhancement', icon: faLightbulb },
    { key: 'enableDeblur', label: 'AI Deblurring', icon: faBolt },
    { key: 'enableOCR', label: 'OCR Extraction', icon: faFont }
  ];

  return (
    <motion.aside 
      className="sidebar"
      initial={{ x: -300 }}
      animate={{ x: 0 }}
      transition={{ type: "spring", stiffness: 100, damping: 20 }}
    >
      <div className="sidebar-header">
        <h2>RailGuard AI</h2>
        <p className="sidebar-subtitle">Configuration Panel</p>
      </div>

      <div className="sidebar-section">
        <h3><FontAwesomeIcon icon={faCog} /> Pipeline Modules</h3>
        
        {modules.map((item, idx) => (
          <motion.label 
            key={item.key}
            className="checkbox-container"
            whileHover={{ scale: 1.02, x: 5 }}
            whileTap={{ scale: 0.98 }}
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: idx * 0.1 }}
          >
            <input 
              type="checkbox"
              checked={config[item.key]}
              onChange={(e) => handleConfigChange(item.key, e.target.checked)}
            />
            <span className="checkbox-label">
              <FontAwesomeIcon icon={item.icon} /> {item.label}
            </span>
            <motion.div 
              className="checkbox-indicator"
              animate={{ 
                backgroundColor: config[item.key] ? '#3B82F6' : '#374151',
                scale: config[item.key] ? 1.2 : 1
              }}
              transition={{ duration: 0.2 }}
            />
          </motion.label>
        ))}
      </div>

      <div className="sidebar-section">
        <h3><FontAwesomeIcon icon={faCog} /> Advanced Settings</h3>
        
        <div className="slider-group">
          <label>Low Blur Threshold: <strong>{config.blurThresholdLow}</strong></label>
          <motion.input 
            type="range"
            min="100"
            max="300"
            value={config.blurThresholdLow}
            onChange={(e) => handleConfigChange('blurThresholdLow', parseInt(e.target.value))}
            className="slider"
            whileHover={{ scale: 1.02 }}
          />
        </div>

        <div className="slider-group">
          <label>High Blur Threshold: <strong>{config.blurThresholdHigh}</strong></label>
          <motion.input 
            type="range"
            min="10"
            max="100"
            value={config.blurThresholdHigh}
            onChange={(e) => handleConfigChange('blurThresholdHigh', parseInt(e.target.value))}
            className="slider"
            whileHover={{ scale: 1.02 }}
          />
        </div>

        <div className="slider-group">
          <label>Confidence: <strong>{config.confidence.toFixed(2)}</strong></label>
          <motion.input 
            type="range"
            min="0"
            max="1"
            step="0.05"
            value={config.confidence}
            onChange={(e) => handleConfigChange('confidence', parseFloat(e.target.value))}
            className="slider"
            whileHover={{ scale: 1.02 }}
          />
        </div>
      </div>

      <motion.div 
        className="system-status"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.5 }}
      >
        <h3><FontAwesomeIcon icon={faMicrochip} /> System Status</h3>
        <motion.div 
          className="status-item"
          animate={{ opacity: [1, 0.7, 1] }}
          transition={{ duration: 2, repeat: Infinity }}
        >
          <FontAwesomeIcon 
            icon={systemStatus ? faCheckCircle : faExclamationTriangle} 
            className={`status-icon ${systemStatus ? 'success' : 'warning'}`}
          />
          <span>GPU: {systemStatus?.gpu || 'RTX 3050'} Ready</span>
        </motion.div>
      </motion.div>
    </motion.aside>
  );
}

export default Sidebar;
