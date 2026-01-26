import React, { useState, useEffect } from 'react';
import { API_BASE_URL, API_VERSION } from '../config/api';

const DemoPage = () => {
  const [userIdInput, setUserIdInput] = useState('');
  const [selectedUser, setSelectedUser] = useState(null);
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [analyzing, setAnalyzing] = useState(false);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState('clusters');

  // Run analysis on selected user
  const runAnalysis = async (userId) => {
    setAnalyzing(true);
    setError(null);
    setProfile(null);
    try {
      const response = await fetch(
        `${API_BASE_URL}${API_VERSION}/analyze-behaviors-from-storage?user_id=${userId}`,
        { method: 'POST' }
      );
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Analysis failed');
      }
      
      const profileData = await response.json();
      setProfile(profileData);
      setSelectedUser(userId);
    } catch (err) {
      setError(err.message);
    } finally {
      setAnalyzing(false);
    }
  };

  // Load existing profile
  const loadProfile = async (userId) => {
    setLoading(true);
    setError(null);
    setProfile(null);
    try {
      const response = await fetch(`${API_BASE_URL}${API_VERSION}/get-user-profile/${userId}`);
      
      if (!response.ok) {
        throw new Error('Profile not found');
      }
      
      const profileData = await response.json();
      setProfile(profileData);
      setSelectedUser(userId);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const getTierColor = (tier) => {
    switch (tier) {
      case 'PRIMARY': return 'bg-green-100 text-green-800 border-green-300';
      case 'SECONDARY': return 'bg-blue-100 text-blue-800 border-blue-300';
      case 'NOISE': return 'bg-gray-100 text-gray-600 border-gray-300';
      default: return 'bg-gray-100 text-gray-800 border-gray-300';
    }
  };

  const renderClusters = () => {
    if (!profile?.behavior_clusters) return null;

    return (
      <div className="space-y-4">
        {profile.behavior_clusters.map((cluster, index) => (
          <div 
            key={index} 
            className={`border-2 rounded-lg p-6 ${getTierColor(cluster.tier)}`}
          >
            <div className="flex justify-between items-start mb-4">
              <div className="flex-1">
                <h3 className="text-xl font-bold mb-2">{cluster.canonical_label}</h3>
                <div className="flex gap-4 text-sm">
                  <span className="font-semibold">Tier: {cluster.tier}</span>
                  <span>Strength: {cluster.cluster_strength?.toFixed(2)}</span>
                  <span>Confidence: {cluster.confidence?.toFixed(2)}</span>
                  <span>Observations: {cluster.observed_count}</span>
                </div>
              </div>
            </div>

            {/* Temporal Metrics */}
            {cluster.temporal_metrics && (
              <div className="mb-4 p-4 bg-white/50 rounded">
                <h4 className="font-semibold mb-2">Temporal Metrics</h4>
                <div className="grid grid-cols-3 gap-4 text-sm">
                  <div>
                    <span className="text-gray-600">First Seen:</span>
                    <div className="font-mono">{new Date(cluster.temporal_metrics.first_seen * 1000).toLocaleDateString()}</div>
                  </div>
                  <div>
                    <span className="text-gray-600">Last Seen:</span>
                    <div className="font-mono">{new Date(cluster.temporal_metrics.last_seen * 1000).toLocaleDateString()}</div>
                  </div>
                  <div>
                    <span className="text-gray-600">Recency Score:</span>
                    <div className="font-mono">{cluster.temporal_metrics.recency_score?.toFixed(2)}</div>
                  </div>
                </div>
              </div>
            )}

            {/* Sample Observations */}
            {cluster.observations && cluster.observations.length > 0 && (
              <div className="mt-4">
                <h4 className="font-semibold mb-2">Sample Observations ({cluster.observations.length}):</h4>
                <div className="space-y-2">
                  {cluster.observations.slice(0, 3).map((obs, obsIndex) => (
                    <div key={obsIndex} className="p-3 bg-white/70 rounded text-sm">
                      <div className="font-mono text-gray-700">{obs.behavior_text}</div>
                      <div className="flex gap-4 mt-1 text-xs text-gray-600">
                        <span>Weight: {obs.behavior_weight?.toFixed(2)}</span>
                        <span>ABW: {obs.adjusted_behavior_weight?.toFixed(2)}</span>
                        <span>Credibility: {obs.credibility?.toFixed(2)}</span>
                      </div>
                    </div>
                  ))}
                  {cluster.observations.length > 3 && (
                    <div className="text-sm text-gray-600 italic">
                      ... and {cluster.observations.length - 3} more
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>
        ))}
      </div>
    );
  };

  const renderArchetype = () => {
    if (!profile?.archetype) return null;

    return (
      <div className="bg-gradient-to-br from-purple-50 to-pink-50 border-2 border-purple-200 rounded-lg p-6">
        <h3 className="text-2xl font-bold text-purple-900 mb-4">
          {profile.archetype.archetype_name}
        </h3>
        <p className="text-gray-700 mb-6">{profile.archetype.description}</p>
        
        <div className="grid grid-cols-2 gap-6">
          {/* Strengths */}
          <div className="bg-white/80 rounded p-4">
            <h4 className="font-semibold text-green-800 mb-3">💪 Strengths</h4>
            <ul className="space-y-2">
              {profile.archetype.strengths?.map((strength, idx) => (
                <li key={idx} className="text-sm flex items-start">
                  <span className="text-green-600 mr-2">✓</span>
                  <span>{strength}</span>
                </li>
              ))}
            </ul>
          </div>

          {/* Growth Areas */}
          <div className="bg-white/80 rounded p-4">
            <h4 className="font-semibold text-orange-800 mb-3">🎯 Growth Areas</h4>
            <ul className="space-y-2">
              {profile.archetype.growth_areas?.map((area, idx) => (
                <li key={idx} className="text-sm flex items-start">
                  <span className="text-orange-600 mr-2">→</span>
                  <span>{area}</span>
                </li>
              ))}
            </ul>
          </div>
        </div>

        {/* Recommendations */}
        <div className="mt-6 bg-white/80 rounded p-4">
          <h4 className="font-semibold text-blue-800 mb-3">💡 Recommendations</h4>
          <ul className="space-y-2">
            {profile.archetype.recommendations?.map((rec, idx) => (
              <li key={idx} className="text-sm flex items-start">
                <span className="text-blue-600 mr-2">•</span>
                <span>{rec}</span>
              </li>
            ))}
          </ul>
        </div>
      </div>
    );
  };

  const renderStats = () => {
    if (!profile) return null;

    return (
      <div className="grid grid-cols-4 gap-4">
        <div className="bg-white border rounded-lg p-4 shadow-sm">
          <div className="text-3xl font-bold text-blue-600">
            {profile.behavior_clusters?.length || 0}
          </div>
          <div className="text-sm text-gray-600">Total Clusters</div>
        </div>
        <div className="bg-white border rounded-lg p-4 shadow-sm">
          <div className="text-3xl font-bold text-green-600">
            {profile.behavior_clusters?.filter(c => c.tier === 'PRIMARY').length || 0}
          </div>
          <div className="text-sm text-gray-600">Primary Behaviors</div>
        </div>
        <div className="bg-white border rounded-lg p-4 shadow-sm">
          <div className="text-3xl font-bold text-blue-600">
            {profile.behavior_clusters?.filter(c => c.tier === 'SECONDARY').length || 0}
          </div>
          <div className="text-sm text-gray-600">Secondary Behaviors</div>
        </div>
        <div className="bg-white border rounded-lg p-4 shadow-sm">
          <div className="text-3xl font-bold text-gray-600">
            {profile.behavior_clusters?.filter(c => c.tier === 'NOISE').length || 0}
          </div>
          <div className="text-sm text-gray-600">Noise</div>
        </div>
      </div>
    );
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50">
      <div className="container mx-auto px-6 py-8">
        {/* Header */}
        <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
          <h1 className="text-4xl font-bold text-gray-800 mb-2">
            🧠 CBIE Demo - Behavior Analysis
          </h1>
          <p className="text-gray-600">
            Core Behavior Identification Engine - Test Data Analysis Interface
          </p>
        </div>

        {/* User Input */}
        <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
          <h2 className="text-2xl font-bold mb-4">Enter User ID to Analyze</h2>
          
          {error && (
            <div className="bg-red-50 border border-red-200 rounded p-4 mb-4">
              <p className="text-red-800">{error}</p>
            </div>
          )}

          <div className="flex gap-4 items-end">
            <div className="flex-1">
              <label className="block text-sm font-semibold text-gray-700 mb-2">
                User ID
              </label>
              <input
                type="text"
                value={userIdInput}
                onChange={(e) => setUserIdInput(e.target.value)}
                placeholder="e.g., user_c9af23, user_44816e, user_71a41e"
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                onKeyPress={(e) => {
                  if (e.key === 'Enter' && userIdInput.trim()) {
                    runAnalysis(userIdInput.trim());
                  }
                }}
              />
              <p className="text-xs text-gray-500 mt-1">
                Enter the user ID from generated test data (e.g., from behaviour_gen_v4.py output)
              </p>
            </div>
            
            <button
              onClick={() => userIdInput.trim() && runAnalysis(userIdInput.trim())}
              disabled={analyzing || !userIdInput.trim()}
              className="bg-blue-600 hover:bg-blue-700 text-white font-semibold py-3 px-8 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed transition-colors h-12"
            >
              {analyzing ? '⏳ Analyzing...' : '▶ Run Analysis'}
            </button>
            
            <button
              onClick={() => userIdInput.trim() && loadProfile(userIdInput.trim())}
              disabled={loading || !userIdInput.trim()}
              className="bg-green-600 hover:bg-green-700 text-white font-semibold py-3 px-8 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed transition-colors h-12"
            >
              {loading ? '⏳ Loading...' : '📊 Load Profile'}
            </button>
          </div>

          {selectedUser && (
            <div className="mt-4 p-3 bg-blue-50 border border-blue-200 rounded-lg">
              <p className="text-sm text-blue-800">
                <span className="font-semibold">Current User:</span> {selectedUser}
              </p>
            </div>
          )}
        </div>

        {/* Results Section */}
        {profile && (
          <div className="space-y-6">
            {/* Stats */}
            {renderStats()}

            {/* Tabs */}
            <div className="bg-white rounded-lg shadow-lg overflow-hidden">
              <div className="flex border-b">
                <button
                  onClick={() => setActiveTab('clusters')}
                  className={`flex-1 py-4 px-6 font-semibold transition-colors ${
                    activeTab === 'clusters'
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                  }`}
                >
                  📊 Behavior Clusters
                </button>
                <button
                  onClick={() => setActiveTab('archetype')}
                  className={`flex-1 py-4 px-6 font-semibold transition-colors ${
                    activeTab === 'archetype'
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                  }`}
                >
                  👤 Archetype Profile
                </button>
                <button
                  onClick={() => setActiveTab('raw')}
                  className={`flex-1 py-4 px-6 font-semibold transition-colors ${
                    activeTab === 'raw'
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                  }`}
                >
                  🔍 Raw Data
                </button>
              </div>

              <div className="p-6">
                {activeTab === 'clusters' && renderClusters()}
                {activeTab === 'archetype' && renderArchetype()}
                {activeTab === 'raw' && (
                  <pre className="bg-gray-50 p-4 rounded overflow-auto max-h-[600px] text-xs">
                    {JSON.stringify(profile, null, 2)}
                  </pre>
                )}
              </div>
            </div>
          </div>
        )}

        {/* Loading State */}
        {(analyzing || loading) && !profile && (
          <div className="bg-white rounded-lg shadow-lg p-12 text-center">
            <div className="animate-spin rounded-full h-16 w-16 border-b-4 border-blue-600 mx-auto mb-4"></div>
            <p className="text-xl font-semibold text-gray-700">
              {analyzing ? 'Running behavior analysis...' : 'Loading profile...'}
            </p>
            <p className="text-gray-600 mt-2">This may take a few moments</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default DemoPage;
