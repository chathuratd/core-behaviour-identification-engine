import React, { useState, useEffect } from 'react';
import { API_ENDPOINTS, apiGet } from '../config/api';
import { CheckCircle, XCircle, Loader2, AlertTriangle } from 'lucide-react';

/**
 * API Health Check Component
 * Tests backend connectivity and displays available test users
 */
const ApiHealthCheck = () => {
  const [healthStatus, setHealthStatus] = useState('checking');
  const [testUsers, setTestUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    checkHealth();
    fetchTestUsers();
  }, []);

  const checkHealth = async () => {
    try {
      const data = await apiGet(API_ENDPOINTS.health);
      if (data.status === 'healthy') {
        setHealthStatus('healthy');
      } else {
        setHealthStatus('unhealthy');
      }
    } catch (err) {
      setHealthStatus('error');
      setError(err.message);
    }
  };

  const fetchTestUsers = async () => {
    try {
      setLoading(true);
      const data = await apiGet(API_ENDPOINTS.getTestUsers());
      setTestUsers(data.users || []);
    } catch (err) {
      console.error('Failed to fetch test users:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const selectUser = (userId) => {
    localStorage.setItem('userId', userId);
    alert(`User ${userId} selected! Refresh the page to see their profile.`);
  };

  return (
    <div className="fixed bottom-4 right-4 max-w-md bg-white rounded-2xl shadow-2xl border border-slate-200 p-6 z-50">
      <h3 className="text-lg font-bold text-slate-900 mb-4">API Health Check</h3>
      
      {/* Health Status */}
      <div className="flex items-center gap-3 mb-4 p-3 bg-slate-50 rounded-lg">
        {healthStatus === 'checking' && (
          <>
            <Loader2 className="w-5 h-5 text-blue-600 animate-spin" />
            <span className="text-sm font-medium text-slate-700">Checking backend...</span>
          </>
        )}
        {healthStatus === 'healthy' && (
          <>
            <CheckCircle className="w-5 h-5 text-green-600" />
            <span className="text-sm font-medium text-green-700">Backend is healthy</span>
          </>
        )}
        {healthStatus === 'unhealthy' && (
          <>
            <AlertTriangle className="w-5 h-5 text-yellow-600" />
            <span className="text-sm font-medium text-yellow-700">Backend is unhealthy</span>
          </>
        )}
        {healthStatus === 'error' && (
          <>
            <XCircle className="w-5 h-5 text-red-600" />
            <span className="text-sm font-medium text-red-700">Cannot reach backend</span>
          </>
        )}
      </div>

      {/* Error Message */}
      {error && (
        <div className="mb-4 p-3 bg-red-50 rounded-lg border border-red-200">
          <p className="text-xs font-medium text-red-700">{error}</p>
        </div>
      )}

      {/* Test Users */}
      <div className="mb-2">
        <h4 className="text-sm font-bold text-slate-700 mb-2">Test Users Available:</h4>
        {loading ? (
          <div className="flex items-center gap-2 text-sm text-slate-500">
            <Loader2 className="w-4 h-4 animate-spin" />
            Loading users...
          </div>
        ) : testUsers.length > 0 ? (
          <div className="space-y-2 max-h-48 overflow-y-auto">
            {testUsers.map((user) => (
              <div
                key={user.user_id}
                className="flex items-center justify-between p-2 bg-slate-50 rounded-lg hover:bg-indigo-50 transition-colors cursor-pointer"
                onClick={() => selectUser(user.user_id)}
              >
                <div className="flex-1">
                  <p className="text-xs font-mono text-slate-700">{user.user_id}</p>
                  <p className="text-[10px] text-slate-500">
                    {user.prompt_count} prompts, {user.behavior_count} behaviors
                  </p>
                </div>
                <button
                  className="text-xs font-bold text-indigo-600 hover:text-indigo-700 px-2 py-1"
                  onClick={(e) => {
                    e.stopPropagation();
                    selectUser(user.user_id);
                  }}
                >
                  Select
                </button>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-xs text-slate-500">No test users found in database</p>
        )}
      </div>

      {/* Current User */}
      <div className="mt-4 pt-4 border-t border-slate-200">
        <p className="text-[10px] font-bold text-slate-500 uppercase tracking-wider mb-1">
          Current User:
        </p>
        <p className="text-xs font-mono text-slate-700 bg-slate-100 px-2 py-1 rounded">
          {localStorage.getItem('userId') || 'Not set'}
        </p>
      </div>

      {/* Refresh Button */}
      <button
        onClick={() => {
          checkHealth();
          fetchTestUsers();
        }}
        className="mt-3 w-full bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-bold py-2 px-4 rounded-lg transition-colors"
      >
        Refresh
      </button>
    </div>
  );
};

export default ApiHealthCheck;
