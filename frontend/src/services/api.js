import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000/api';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: { 'Content-Type': 'application/json' },
});

// Process a single frame image
export const processFrame = async (file) => {
  const formData = new FormData();
  formData.append('image', file);
  return apiClient.post('/process/frame', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  });
};

// Process a video file
export const processVideo = async (file) => {
  const formData = new FormData();
  formData.append('video', file);
  return apiClient.post('/process/video', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  });
};

// Get processing status for a job
export const getProcessingStatus = async (jobId) => {
  return apiClient.get(`/status/${jobId}`);
};

// Get processing results for a job
export const getResult = async (jobId) => {
  return apiClient.get(`/result/${jobId}`);
};

// Health check
export const healthCheck = async () => {
  return apiClient.get('/health');
};

export default {
  processFrame,
  processVideo,
  getProcessingStatus,
  getResult,
  healthCheck
};
