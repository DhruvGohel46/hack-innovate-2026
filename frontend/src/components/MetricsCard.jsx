import React from 'react';
import { motion } from 'framer-motion';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import * as icons from '@fortawesome/free-solid-svg-icons';

function MetricsCard({ title, value, delta, icon }) {
  const iconMap = {
    'train': icons.faTrain,
    'image': icons.faImage,
    'eye': icons.faEye,
    'check': icons.faCheckCircle,
    'tachometer-alt': icons.faTachometerAlt
  };

  return (
    <motion.div
      className="metrics-card"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      whileHover={{ 
        scale: 1.05, 
        boxShadow: '0 12px 30px rgba(59,130,246,0.4)',
        y: -5
      }}
      transition={{ duration: 0.3 }}
    >
      <motion.div 
        className="metrics-icon"
        whileHover={{ rotate: 360, scale: 1.2 }}
        transition={{ duration: 0.6 }}
      >
        <FontAwesomeIcon icon={iconMap[icon]} />
      </motion.div>
      <div className="metrics-content">
        <p className="metrics-title">{title}</p>
        <motion.h3 
          className="metrics-value"
          initial={{ scale: 0 }}
          animate={{ scale: 1 }}
          transition={{ type: "spring", stiffness: 200, delay: 0.2 }}
        >
          {value}
        </motion.h3>
        <motion.span 
          className="metrics-delta"
          animate={{ opacity: [0.7, 1, 0.7] }}
          transition={{ duration: 2, repeat: Infinity }}
        >
          {delta}
        </motion.span>
      </div>
    </motion.div>
  );
}

export default MetricsCard;
