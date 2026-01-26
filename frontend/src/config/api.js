// API configuration
export const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
export const API_VERSION = '/api/v1';

export const API_ENDPOINTS = {
  // Profile endpoints
  getUserProfile: (userId) => `${API_BASE_URL}${API_VERSION}/get-user-profile/${userId}`,
  listCoreBehaviors: (userId) => `${API_BASE_URL}${API_VERSION}/list-core-behaviors/${userId}`,
  analyzeFromStorage: (userId) => `${API_BASE_URL}${API_VERSION}/analyze-behaviors-from-storage?user_id=${userId}`,
  
  // LLM Context endpoint
  getLLMContext: (userId, params) => {
    const queryParams = new URLSearchParams(params).toString();
    return `${API_BASE_URL}${API_VERSION}/profile/${userId}/llm-context${queryParams ? '?' + queryParams : ''}`;
  },
  
  // Analysis summary for visualizations
  getAnalysisSummary: (userId) => `${API_BASE_URL}${API_VERSION}/profile/${userId}/analysis-summary`,
  
  // Test users endpoint
  getTestUsers: () => `${API_BASE_URL}${API_VERSION}/test-users`,
  
  // Health check
  health: `${API_BASE_URL}${API_VERSION}/health`,
};

// Helper function to handle API errors
export const handleApiError = async (response) => {
  if (!response.ok) {
    let errorMessage = `Request failed: ${response.statusText}`;
    try {
      const errorData = await response.json();
      errorMessage = errorData.detail || errorData.message || errorMessage;
    } catch (e) {
      // If JSON parsing fails, use default error message
    }
    throw new Error(errorMessage);
  }
  return response.json();
};

// Helper function to make GET requests
export const apiGet = async (url) => {
  try {
    const response = await fetch(url, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });
    return await handleApiError(response);
  } catch (error) {
    console.error('API GET Error:', error);
    throw error;
  }
};

// Helper function to make POST requests
export const apiPost = async (url, data = null) => {
  try {
    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: data ? JSON.stringify(data) : null,
    });
    return await handleApiError(response);
  } catch (error) {
    console.error('API POST Error:', error);
    throw error;
  }
};

export default API_BASE_URL;

