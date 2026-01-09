import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: { 'Content-Type': 'application/json' },
});

// Upload video file to backend for processing
export const uploadVideo = async (file, config) => {
  const formData = new FormData();
  formData.append('video', file);
  formData.append('config', JSON.stringify(config));
  return apiClient.post('/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  });
};

// Start video processing pipeline with settings
export const startProcessing = async (videoId, settings) => {
  return apiClient.post('/process/start', { videoId, settings });
};

// Get real-time processing status and progress percentage
export const getProcessingStatus = async (jobId) => {
  return apiClient.get(`/process/status/${jobId}`);
};

// Fetch all detected wagon data from completed job
export const getDetectionResults = async (jobId) => {
  return apiClient.get(`/results/${jobId}`);
};

// Download processed and deblurred video file
export const downloadProcessedVideo = async (jobId) => {
  return apiClient.get(`/download/video/${jobId}`, { responseType: 'blob' });
};

// Download detection report as CSV file
export const downloadReport = async (jobId) => {
  return apiClient.get(`/download/report/${jobId}`, { responseType: 'blob' });
};

// Get system health status and GPU information
export const getSystemStatus = async () => {
  return apiClient.get('/system/status');
};

// Cancel ongoing processing job immediately
export const cancelJob = async (jobId) => {
  return apiClient.post(`/process/cancel/${jobId}`);
};

export default {
  uploadVideo,
  startProcessing,
  getProcessingStatus,
  getDetectionResults,
  downloadProcessedVideo,
  downloadReport,
  getSystemStatus,
  cancelJob
};
