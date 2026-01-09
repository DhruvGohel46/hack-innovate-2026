import React from 'react';
import { motion } from 'framer-motion';

function ResultsTable({ data }) {
  return (
    <motion.div
      className="results-table-container"
      initial={{ opacity: 0, y: 30 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.3 }}
    >
      <h3>Detected Wagon IDs</h3>
      <div className="table-wrapper">
        <table className="results-table">
          <thead>
            <tr>
              <th>Frame</th>
              <th>Timestamp</th>
              <th>Wagon ID</th>
              <th>Confidence</th>
              <th>Blur Class</th>
            </tr>
          </thead>
          <tbody>
            {data && data.map((row, idx) => (
              <motion.tr
                key={idx}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: idx * 0.05 }}
                whileHover={{ 
                  backgroundColor: 'rgba(59,130,246,0.15)',
                  scale: 1.01,
                  x: 5
                }}
              >
                <td>{row.frame}</td>
                <td>{row.timestamp}s</td>
                <td className="wagon-id">
                  <motion.span
                    whileHover={{ scale: 1.1, color: '#3B82F6' }}
                  >
                    {row.wagonId}
                  </motion.span>
                </td>
                <td>{row.confidence}</td>
                <td>
                  <motion.span 
                    className={`blur-badge ${row.blurClass.toLowerCase()}`}
                    whileHover={{ scale: 1.1 }}
                    whileTap={{ scale: 0.95 }}
                  >
                    {row.blurClass}
                  </motion.span>
                </td>
              </motion.tr>
            ))}
          </tbody>
        </table>
      </div>
    </motion.div>
  );
}

export default ResultsTable;
