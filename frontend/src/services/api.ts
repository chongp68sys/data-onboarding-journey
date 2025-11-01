import axios from 'axios';

const API_BASE_URL = 'http://localhost:8001';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Health check endpoint
export const healthCheck = async () => {
  try {
    const response = await api.get('/health');
    return response.data;
  } catch (error) {
    console.error('Health check failed:', error);
    throw error;
  }
};

// Get workflow status
export const getWorkflowStatus = async () => {
  try {
    const response = await api.get('/api/v1/workflows/status');
    return response.data;
  } catch (error) {
    console.error('Failed to get workflow status:', error);
    throw error;
  }
};

// Execute workflow
export const executeWorkflow = async (workflowData: any) => {
  try {
    const response = await api.post('/api/v1/workflows/execute', workflowData);
    return response.data;
  } catch (error) {
    console.error('Failed to execute workflow:', error);
    throw error;
  }
};

export default api;