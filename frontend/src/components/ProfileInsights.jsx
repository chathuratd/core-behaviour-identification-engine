import React, { useState, useEffect } from 'react';
import { 
  TrendingUp, 
  Zap,
  Fingerprint,
  Calendar,
  Layers,
  FileText,
  AlertCircle,
  Loader2,
  Eye,
  EyeOff,
  Trash2,
  RefreshCw,
  Clock,
  TrendingDown,
  MessageSquare,
  Copy,
  Check,
  Settings,
  X
} from 'lucide-react';
import { API_ENDPOINTS } from '../config/api';

const ProfileInsights = () => {
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [expandedClusters, setExpandedClusters] = useState(new Set());
  const [showCoreBehaviors, setShowCoreBehaviors] = useState(false);
  const [showSupportingBehaviors, setShowSupportingBehaviors] = useState(false);
  const [showLLMModal, setShowLLMModal] = useState(false);
  const [llmContext, setLlmContext] = useState(null);
  const [llmLoading, setLlmLoading] = useState(false);
  const [copied, setCopied] = useState(false);
  const [analyzing, setAnalyzing] = useState(false);
  const [analysisSuccess, setAnalysisSuccess] = useState(false);
  const [llmParams, setLlmParams] = useState({
    min_strength: 30.0,
    min_confidence: 0.40,
    max_behaviors: 5,
    include_archetype: true
  });

  // Fetch profile data from API
  useEffect(() => {
    fetchProfile();
  }, []);

  const fetchProfile = async () => {
    try {
      setLoading(true);
      setError(null);
      
      // TODO: Replace with actual user ID from auth context
      // For now, using hardcoded user ID for demo purposes
      const userId = localStorage.getItem('userId') || 'user_665390';
      const response = await fetch(API_ENDPOINTS.getUserProfile(userId));
      
      if (!response.ok) {
        if (response.status === 404) {
          throw new Error('Profile not found. Please run analysis first.');
        }
        throw new Error(`Failed to fetch profile: ${response.statusText}`);
      }
      
      const data = await response.json();
      setProfile(data);
    } catch (err) {
      console.error('Error fetching profile:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const toggleCluster = (clusterId) => {
    setExpandedClusters(prev => {
      const newSet = new Set(prev);
      if (newSet.has(clusterId)) {
        newSet.delete(clusterId);
      } else {
        newSet.add(clusterId);
      }
      return newSet;
    });
  };

  const fetchLLMContext = async () => {
    try {
      setLlmLoading(true);
      const userId = localStorage.getItem('userId') || 'user_665390';
      const response = await fetch(API_ENDPOINTS.getLLMContext(userId, llmParams));
      
      if (!response.ok) {
        if (response.status === 404) {
          throw new Error('Profile not found. Please run analysis first.');
        }
        throw new Error(`Failed to fetch LLM context: ${response.statusText}`);
      }
      
      const data = await response.json();
      setLlmContext(data);
    } catch (err) {
      console.error('Error fetching LLM context:', err);
      alert('Failed to generate LLM context: ' + err.message);
    } finally {
      setLlmLoading(false);
    }
  };

  const handleCopyContext = () => {
    if (llmContext?.context) {
      navigator.clipboard.writeText(llmContext.context);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  const openLLMModal = () => {
    setShowLLMModal(true);
    if (!llmContext) {
      fetchLLMContext();
    }
  };

  const runProfileAnalysis = async () => {
    try {
      setAnalyzing(true);
      setAnalysisSuccess(false);
      const userId = localStorage.getItem('userId') || 'user_665390';
      
      const response = await fetch(API_ENDPOINTS.analyzeFromStorage(userId), {
        method: 'POST',
      });
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `Analysis failed: ${response.statusText}`);
      }
      
      const data = await response.json();
      console.log('Analysis complete:', data);
      
      // Show success message
      setAnalysisSuccess(true);
      setTimeout(() => setAnalysisSuccess(false), 3000);
      
      // Refresh profile after 1 second
      setTimeout(() => {
        fetchProfile();
      }, 1000);
      
    } catch (err) {
      console.error('Error analyzing profile:', err);
      alert('Failed to analyze profile: ' + err.message);
    } finally {
      setAnalyzing(false);
    }
  };

  const formatDate = (timestamp) => {
    return new Date(timestamp * 1000).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric'
    });
  };

  const formatTimeAgo = (timestamp) => {
    const seconds = Math.floor(Date.now() / 1000 - timestamp);
    if (seconds < 60) return 'just now';
    if (seconds < 3600) return `${Math.floor(seconds / 60)}m ago`;
    if (seconds < 86400) return `${Math.floor(seconds / 3600)}h ago`;
    return `${Math.floor(seconds / 86400)}d ago`;
  };

  const getTierColor = (tier) => {
    switch (tier) {
      case 'PRIMARY':
        return {
          bg: 'bg-indigo-50',
          text: 'text-indigo-700',
          border: 'border-indigo-100',
          badge: 'bg-gradient-to-r from-indigo-600 to-indigo-700',
          label: 'Core',
          dotColor: 'bg-yellow-400'
        };
      case 'SECONDARY':
        return {
          bg: 'bg-blue-50',
          text: 'text-blue-700',
          border: 'border-blue-100',
          badge: 'bg-gradient-to-r from-blue-600 to-blue-700',
          label: 'Supporting',
          dotColor: 'bg-blue-300'
        };
      case 'NOISE':
        return {
          bg: 'bg-slate-50',
          text: 'text-slate-600',
          border: 'border-slate-100',
          badge: 'bg-slate-400',
          label: 'Weak',
          dotColor: 'bg-slate-300'
        };
      default:
        return {
          bg: 'bg-slate-50',
          text: 'text-slate-600',
          border: 'border-slate-100',
          badge: 'bg-slate-400',
          label: 'Unknown',
          dotColor: 'bg-slate-300'
        };
    }
  };

  // Loading state
  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-center space-y-4">
          <Loader2 className="w-12 h-12 text-indigo-600 animate-spin mx-auto" />
          <p className="text-slate-500 font-medium">Loading your behavior profile...</p>
        </div>
      </div>
    );
  }

  // Error state
  if (error) {
    return (
      <div className="bg-red-50 border-2 border-red-200 rounded-3xl p-8">
        <div className="flex items-start gap-4">
          <AlertCircle className="w-6 h-6 text-red-600 flex-shrink-0 mt-1" />
          <div>
            <h3 className="text-lg font-bold text-red-900 mb-2">Failed to Load Profile</h3>
            <p className="text-red-700 mb-4">{error}</p>
            <button
              onClick={fetchProfile}
              className="flex items-center gap-2 px-4 py-2 bg-red-600 text-white rounded-xl font-bold hover:bg-red-700 transition-colors"
            >
              <RefreshCw size={16} />
              Retry
            </button>
          </div>
        </div>
      </div>
    );
  }

  // No profile found
  if (!profile) {
    return (
      <div className="bg-slate-50 border-2 border-slate-200 rounded-3xl p-12 text-center">
        <Fingerprint className="w-16 h-16 text-slate-300 mx-auto mb-4" />
        <h3 className="text-xl font-bold text-slate-700 mb-2">No Profile Found</h3>
        <p className="text-slate-500">Start interacting to build your behavioral profile.</p>
      </div>
    );
  }

  // Group clusters by tier
  const primaryClusters = profile.behavior_clusters?.filter(c => c.tier === 'PRIMARY') || [];
  const secondaryClusters = profile.behavior_clusters?.filter(c => c.tier === 'SECONDARY') || [];
  const noiseClusters = profile.behavior_clusters?.filter(c => c.tier === 'NOISE') || [];

  const ClusterCard = ({ cluster }) => {
    const colors = getTierColor(cluster.tier);
    const isExpanded = expandedClusters.has(cluster.cluster_id);
    
    return (
      <div 
        className="bg-white border border-slate-200 rounded-2xl shadow-sm hover:shadow-xl hover:-translate-y-1 transition-all duration-300 cursor-pointer group overflow-hidden"
        onClick={() => toggleCluster(cluster.cluster_id)}
      >
        {/* Header */}
        <div className={`${colors.bg} border-b ${colors.border} p-4`}>
          <div className="flex items-start justify-between gap-3 mb-3">
            <div className="flex-1">
              <h4 className={`text-lg font-black ${colors.text} leading-tight tracking-tight`}>
                {cluster.canonical_label}
              </h4>
              {cluster.cluster_name && (
                <p className="text-xs text-slate-500 mt-1 font-medium italic">
                  {cluster.cluster_name}
                </p>
              )}
            </div>
            <div className="text-right flex-shrink-0 bg-white/60 backdrop-blur-sm rounded-xl px-3 py-1.5">
              <div className="text-2xl font-black text-slate-900 leading-none">
                {Math.round(cluster.cluster_strength * 100)}
              </div>
              <div className="text-[9px] font-bold text-slate-400 uppercase tracking-widest">strength</div>
            </div>
          </div>
          <div className="text-[9px] font-bold text-slate-400 uppercase tracking-widest">
            {cluster.cluster_size} OBSERVATIONS
          </div>
        </div>

        {/* Body with stats */}
        <div className="p-4 space-y-3">
          {/* Confidence Bar */}
          <div className="bg-slate-50 rounded-xl p-3">
            <div className="flex items-center justify-between mb-2">
              <span className="text-[10px] font-black text-slate-600 uppercase tracking-widest">Confidence</span>
              <span className="text-xl font-black text-slate-900">
                {Math.round(cluster.confidence * 100)}%
              </span>
            </div>
            <div className="bg-slate-200 h-1.5 rounded-full overflow-hidden">
              <div 
                className={`${cluster.confidence >= 0.75 ? 'bg-emerald-500' : cluster.confidence >= 0.60 ? 'bg-blue-500' : 'bg-slate-400'} h-full rounded-full transition-all duration-500`}
                style={{ width: `${cluster.confidence * 100}%` }}
              />
            </div>
          </div>

          {/* Activity Info */}
          <div className="grid grid-cols-2 gap-2">
            <div className="bg-slate-50 rounded-xl p-3">
              <div className="flex items-center gap-1.5 mb-1">
                <div className="w-1.5 h-1.5 rounded-full bg-green-500 animate-pulse"></div>
                <span className="text-[9px] font-black text-slate-600 uppercase tracking-widest">Active</span>
              </div>
              <div className="text-base font-black text-slate-900">
                {cluster.days_active ? `${Math.round(cluster.days_active)}d` : '<1d'}
              </div>
            </div>
            
            <div className="bg-slate-50 rounded-xl p-3">
              <div className="flex items-center gap-1.5 mb-1">
                <Clock size={10} className="text-slate-400" />
                <span className="text-[9px] font-black text-slate-600 uppercase tracking-widest">Last Seen</span>
              </div>
              <div className="text-base font-black text-slate-900">
                {formatTimeAgo(cluster.last_seen)}
              </div>
            </div>
          </div>

          {/* Timeline */}
          <div className="text-[10px] text-slate-500 pt-2 border-t border-slate-100 flex items-center gap-1">
            <Calendar size={10} className="text-slate-400" />
            <span className="font-bold">First: {formatDate(cluster.first_seen)}</span>
          </div>
        </div>

        {/* Expanded variations */}
        {isExpanded && cluster.wording_variations && cluster.wording_variations.length > 0 && (
          <div className="border-t border-slate-200 bg-slate-50 p-4">
            <div className="flex items-center justify-between mb-3">
              <p className="text-[10px] font-black text-slate-700 uppercase tracking-widest">
                Wording Variations
              </p>
              <span className="px-2 py-0.5 bg-slate-900 text-white text-[9px] font-black rounded-full">
                {cluster.wording_variations.length}
              </span>
            </div>
            <div className="space-y-2 max-h-40 overflow-y-auto">
              {cluster.wording_variations.map((variation, idx) => (
                <div key={idx} className="bg-white rounded-lg px-3 py-2 text-xs text-slate-700 font-medium shadow-sm border border-slate-100">
                  "{variation}"
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Footer hint */}
        <div className="px-4 py-2 bg-slate-50 border-t border-slate-100 text-center">
          <p className="text-[9px] font-bold text-slate-400 uppercase tracking-widest">
            {isExpanded ? 'Click to collapse' : 'Click to expand variations'}
          </p>
        </div>
      </div>
    );
  };

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-black text-slate-900 tracking-tight">Profile Insights</h1>
        <p className="text-slate-500 font-medium mt-1">
          Live analysis of your behavioral identity
        </p>
      </div>
          
      {/* Section 1: Hero Summary */}
      <div className="bg-white rounded-2xl border border-slate-200 shadow-xl shadow-slate-200/40 overflow-hidden">
        {/* Top bar with user info and actions */}
        <div className="px-6 py-4 bg-slate-50 border-b border-slate-200 flex items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <span className="flex items-center gap-1.5 text-slate-500 text-xs font-mono bg-white px-3 py-1.5 rounded-lg border border-slate-200">
              <Fingerprint size={12} /> {profile.user_id}
            </span>
            <button 
              onClick={fetchProfile}
              className="p-1.5 rounded-lg text-slate-400 hover:bg-slate-200 hover:text-slate-600 transition-all"
              title="Refresh profile"
            >
              <RefreshCw size={14} />
            </button>
          </div>
          <div className="flex items-center gap-2">
            <button 
              onClick={openLLMModal}
              className="flex items-center gap-1.5 px-3 py-1.5 bg-white border-2 border-purple-500 text-purple-600 hover:bg-purple-50 text-xs font-bold rounded-lg transition-all"
              title="View LLM Context"
            >
              <MessageSquare size={14} strokeWidth={2.5} />
              LLM Context
            </button>
            <button 
              onClick={runProfileAnalysis}
              disabled={analyzing}
              className={`flex items-center gap-1.5 px-3 py-1.5 text-xs font-bold rounded-lg transition-all ${
                analyzing 
                  ? 'bg-slate-300 cursor-not-allowed text-slate-500' 
                  : analysisSuccess
                  ? 'bg-green-500 hover:bg-green-600 text-white'
                  : 'bg-blue-600 hover:bg-blue-700 text-white'
              }`}
              title="Analyze behaviors and generate profile"
            >
              {analyzing ? (
                <>
                  <Loader2 size={14} className="animate-spin" strokeWidth={2.5} />
                  Analyzing...
                </>
              ) : analysisSuccess ? (
                <>
                  <Check size={14} strokeWidth={2.5} />
                  Success!
                </>
              ) : (
                <>
                  <Zap size={14} strokeWidth={2.5} />
                  Analyze Profile
                </>
              )}
            </button>
          </div>
        </div>

        {/* Main content */}
        <div className="p-6 flex flex-col md:flex-row justify-between items-center gap-6">
          <div className="flex-1">
            <h2 className="text-2xl font-black text-slate-900 mb-1.5 tracking-tight">
              {profile.archetype || 'Behavioral Profile'}
            </h2>
            <p className="text-sm text-slate-600">
              Analyzing your interaction patterns across <span className="font-bold text-slate-900">{profile.statistics?.total_behaviors_analyzed || 0}</span> observed behaviors
              and <span className="font-bold text-slate-900">{profile.statistics?.total_prompts_analyzed || 0}</span> prompts.
            </p>
          </div>
          
          {/* Stats sidebar */}
          <div className="w-full md:w-64 bg-gradient-to-br from-slate-50 to-slate-100/50 p-4 rounded-xl border border-slate-200">
            <div className="flex items-center justify-between mb-3 pb-2 border-b border-slate-200">
              <span className="text-[10px] font-black text-slate-600 uppercase tracking-widest">Analysis Span</span>
              <span className="text-sm font-black text-indigo-600">
                {Math.round(profile.statistics?.analysis_time_span_days || 0)} days
              </span>
            </div>
            <div className="grid grid-cols-2 gap-2">
              <div className="bg-white rounded-lg p-3 text-center border border-slate-100">
                <div className="text-xl font-black text-indigo-600">
                  {profile.statistics?.clusters_formed || 0}
                </div>
                <div className="text-[9px] text-slate-500 font-bold uppercase tracking-wider">Clusters</div>
              </div>
              <div className="bg-white rounded-lg p-3 text-center border border-slate-100">
                <div className="text-xl font-black text-blue-600">
                  {profile.statistics?.total_behaviors_analyzed || 0}
                </div>
                <div className="text-[9px] text-slate-500 font-bold uppercase tracking-wider">Behaviors</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Section 2: Core Behavior Clusters - Always show */}
      <div className="bg-white rounded-2xl border border-slate-200 shadow-xl shadow-slate-200/40 overflow-hidden">
        <div 
          className="p-8 border-b border-slate-100 bg-gradient-to-br from-indigo-50/50 to-transparent cursor-pointer hover:bg-indigo-50/80 transition-colors"
          onClick={() => setShowCoreBehaviors(!showCoreBehaviors)}
        >
          <div className="flex items-start justify-between">
            <div className="flex-1">
              <h2 className="text-2xl font-black text-slate-900 flex items-center gap-3 mb-2 tracking-tight">
                <div className="p-2.5 rounded-xl bg-indigo-100 text-indigo-600">
                  <Zap size={22} strokeWidth={2.5} className="fill-indigo-600" />
                </div>
                Core Behaviors
              </h2>
              <p className="text-sm font-medium text-indigo-700/80 ml-12">
                Your dominant, defining behavioral patterns
              </p>
            </div>
            <div className="flex items-center gap-3">
              <div className="px-4 py-1.5 bg-slate-900 text-white text-xs font-black rounded-full uppercase tracking-widest shadow-lg">
                {primaryClusters.length}
              </div>
              <button className="p-2 rounded-xl hover:bg-indigo-100 transition-colors text-indigo-600">
                {showCoreBehaviors ? <EyeOff size={20} /> : <Eye size={20} />}
              </button>
            </div>
          </div>
        </div>
        
        {showCoreBehaviors && (
          <>
            {primaryClusters.length > 0 ? (
              <div className="p-8 grid grid-cols-1 md:grid-cols-2 gap-6">
                {primaryClusters.map((cluster) => (
                  <ClusterCard key={cluster.cluster_id} cluster={cluster} />
                ))}
              </div>
            ) : (
              <div className="p-8 text-center">
                <div className="max-w-md mx-auto">
                  <div className="w-16 h-16 rounded-full bg-indigo-50 flex items-center justify-center mx-auto mb-4">
                    <Zap size={28} className="text-indigo-300" />
                  </div>
                  <h3 className="text-lg font-bold text-slate-700 mb-2">No Core Behaviors Yet</h3>
                  <p className="text-sm text-slate-500">
                    Core behaviors emerge when patterns are strong (≥60%) and confident (≥75%). 
                    Keep interacting to build more data!
                  </p>
                </div>
              </div>
            )}
          </>
        )}
      </div>

      {/* Section 3: Supporting Behavior Clusters */}
      {secondaryClusters.length > 0 && (
        <div className="bg-white rounded-2xl border border-slate-200 shadow-xl shadow-slate-200/40 overflow-hidden">
          <div 
            className="p-8 border-b border-slate-100 bg-gradient-to-br from-blue-50/50 to-transparent cursor-pointer hover:bg-blue-50/80 transition-colors"
            onClick={() => setShowSupportingBehaviors(!showSupportingBehaviors)}
          >
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <h2 className="text-2xl font-black text-slate-900 flex items-center gap-3 mb-2 tracking-tight">
                  <div className="p-2.5 rounded-xl bg-blue-100 text-blue-600">
                    <Layers size={22} strokeWidth={2.5} />
                  </div>
                  Supporting Behaviors
                </h2>
                <p className="text-sm font-medium text-blue-700/80 ml-12">
                  Contextual patterns that complement your core traits
                </p>
              </div>
              <div className="flex items-center gap-3">
                <div className="px-4 py-1.5 bg-slate-900 text-white text-xs font-black rounded-full uppercase tracking-widest shadow-lg">
                  {secondaryClusters.length}
                </div>
                <button className="p-2 rounded-xl hover:bg-blue-100 transition-colors text-blue-600">
                  {showSupportingBehaviors ? <EyeOff size={20} /> : <Eye size={20} />}
                </button>
              </div>
            </div>
          </div>
          
          {showSupportingBehaviors && (
            <div className="p-8 grid grid-cols-1 md:grid-cols-2 gap-6">
              {secondaryClusters.map((cluster) => (
                <ClusterCard key={cluster.cluster_id} cluster={cluster} />
              ))}
            </div>
          )}
        </div>
      )}

      {/* Section 4: Evolution Timeline */}
      {profile.behavior_clusters && profile.behavior_clusters.length > 0 && (
        <div className="bg-white p-8 rounded-3xl border border-slate-200 shadow-sm">
          <h3 className="text-lg font-bold mb-8 flex items-center gap-2">
            <TrendingUp size={20} className="text-indigo-500" /> Behavior Evolution Timeline
          </h3>
          <div className="relative border-l-2 border-slate-100 ml-3 space-y-8">
            {profile.behavior_clusters
              .filter(c => c.tier !== 'NOISE')
              .sort((a, b) => b.last_seen - a.last_seen)
              .slice(0, 5)
              .map((cluster, idx) => (
                <div key={cluster.cluster_id} className="relative pl-8">
                  <div className={`absolute -left-[9px] top-1 w-4 h-4 rounded-full bg-white border-4 ${
                    idx === 0 ? 'border-indigo-600' : 'border-slate-300'
                  } shadow-sm`}></div>
                  <p className="text-sm font-bold text-slate-900">
                    {formatTimeAgo(cluster.last_seen)}
                  </p>
                  <p className="text-sm text-slate-500 mt-1">
                    Updated: "{cluster.canonical_label}" 
                    <span className="ml-2 text-xs font-bold text-slate-400">
                      ({cluster.cluster_size} observations)
                    </span>
                  </p>
                </div>
              ))}
          </div>
        </div>
      )}

      {/* Section 5: Noise/Outliers (Collapsible) */}
      {noiseClusters.length > 0 && (
        <details className="bg-white rounded-3xl border border-slate-200 shadow-sm overflow-hidden">
          <summary className="p-6 cursor-pointer hover:bg-slate-50 transition-colors">
            <div className="flex items-center justify-between">
              <h3 className="text-lg font-bold text-slate-700 flex items-center gap-2">
                <TrendingDown size={20} className="text-slate-400" /> 
                Noise & Outliers
                <span className="text-sm font-normal text-slate-400">
                  ({noiseClusters.length} low-confidence clusters)
                </span>
              </h3>
            </div>
          </summary>
          <div className="p-6 pt-0 grid grid-cols-1 md:grid-cols-2 gap-4">
            {noiseClusters.map((cluster) => (
              <ClusterCard key={cluster.cluster_id} cluster={cluster} />
            ))}
          </div>
        </details>
      )}

      {/* Empty state */}
      {(!profile.behavior_clusters || profile.behavior_clusters.length === 0) && (
        <div className="bg-slate-50 border-2 border-slate-200 rounded-3xl p-12 text-center">
          <Fingerprint className="w-16 h-16 text-slate-300 mx-auto mb-4" />
          <h3 className="text-xl font-bold text-slate-700 mb-2">No Behaviors Detected</h3>
          <p className="text-slate-500">
            Continue interacting to build your behavioral profile.
          </p>
        </div>
      )}

      {/* LLM Context Modal */}
      {showLLMModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black bg-opacity-50 backdrop-blur-sm" onClick={() => setShowLLMModal(false)}>
          <div className="bg-white rounded-2xl shadow-2xl max-w-4xl w-full max-h-[90vh] overflow-hidden flex flex-col" onClick={e => e.stopPropagation()}>
            {/* Modal Header */}
            <div className="bg-gradient-to-r from-purple-600 to-indigo-600 text-white p-6">
              <div className="flex items-center justify-between mb-2">
                <h3 className="text-2xl font-bold flex items-center gap-2">
                  <MessageSquare size={24} />
                  LLM Context
                </h3>
                <button 
                  onClick={() => setShowLLMModal(false)}
                  className="p-2 hover:bg-white hover:bg-opacity-20 rounded-lg transition-colors"
                >
                  <X size={20} />
                </button>
              </div>
              <p className="text-purple-100 text-sm">
                Use this context to personalize AI responses based on user behavior patterns
              </p>
            </div>

            {/* Modal Body */}
            <div className="flex-1 overflow-y-auto p-6">
              {llmLoading ? (
                <div className="flex flex-col items-center justify-center py-12">
                  <Loader2 className="w-12 h-12 text-indigo-600 animate-spin mb-4" />
                  <p className="text-slate-600">Generating LLM context...</p>
                </div>
              ) : llmContext ? (
                <div className="space-y-6">
                  {/* Context Output */}
                  <div className="bg-slate-50 rounded-xl p-6 border border-slate-200">
                    <div className="flex items-center justify-between mb-4">
                      <h4 className="text-sm font-bold text-slate-700 uppercase tracking-wide">Generated Context</h4>
                      <button
                        onClick={handleCopyContext}
                        className={`flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs font-bold transition-all ${
                          copied 
                            ? 'bg-green-600 text-white' 
                            : 'bg-indigo-600 hover:bg-indigo-700 text-white'
                        }`}
                      >
                        {copied ? (
                          <>
                            <Check size={14} />
                            Copied!
                          </>
                        ) : (
                          <>
                            <Copy size={14} />
                            Copy
                          </>
                        )}
                      </button>
                    </div>
                    <pre className="text-sm text-slate-800 whitespace-pre-wrap font-mono bg-white p-4 rounded-lg border border-slate-200 max-h-96 overflow-y-auto">
                      {llmContext.context}
                    </pre>
                  </div>

                  {/* Metadata */}
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    <div className="bg-indigo-50 rounded-xl p-4 border border-indigo-200">
                      <div className="text-xs font-bold text-indigo-600 uppercase mb-1">Total Clusters</div>
                      <div className="text-2xl font-black text-indigo-900">
                        {llmContext.metadata.total_clusters}
                      </div>
                    </div>
                    <div className="bg-purple-50 rounded-xl p-4 border border-purple-200">
                      <div className="text-xs font-bold text-purple-600 uppercase mb-1">Included</div>
                      <div className="text-2xl font-black text-purple-900">
                        {llmContext.metadata.included_behaviors}
                      </div>
                    </div>
                    <div className="bg-blue-50 rounded-xl p-4 border border-blue-200">
                      <div className="text-xs font-bold text-blue-600 uppercase mb-1">Avg Strength</div>
                      <div className="text-2xl font-black text-blue-900">
                        {Math.round(llmContext.metadata.summary.average_strength * 100)}%
                      </div>
                    </div>
                    <div className="bg-green-50 rounded-xl p-4 border border-green-200">
                      <div className="text-xs font-bold text-green-600 uppercase mb-1">Confidence</div>
                      <div className="text-2xl font-black text-green-900">
                        {Math.round(llmContext.metadata.summary.average_confidence * 100)}%
                      </div>
                    </div>
                  </div>

                  {/* Settings */}
                  <details className="bg-white rounded-xl border border-slate-200">
                    <summary className="p-4 cursor-pointer hover:bg-slate-50 rounded-xl transition-colors">
                      <h4 className="text-sm font-bold text-slate-700 flex items-center gap-2 inline-flex">
                        <Settings size={16} />
                        Advanced Settings
                      </h4>
                    </summary>
                    <div className="p-4 pt-0 space-y-4">
                      <div>
                        <label className="block text-xs font-bold text-slate-600 mb-2">
                          Min Strength: {llmParams.min_strength}%
                        </label>
                        <input
                          type="range"
                          min="0"
                          max="100"
                          step="5"
                          value={llmParams.min_strength}
                          onChange={(e) => setLlmParams({...llmParams, min_strength: parseFloat(e.target.value)})}
                          className="w-full"
                        />
                      </div>
                      <div>
                        <label className="block text-xs font-bold text-slate-600 mb-2">
                          Min Confidence: {Math.round(llmParams.min_confidence * 100)}%
                        </label>
                        <input
                          type="range"
                          min="0"
                          max="1"
                          step="0.05"
                          value={llmParams.min_confidence}
                          onChange={(e) => setLlmParams({...llmParams, min_confidence: parseFloat(e.target.value)})}
                          className="w-full"
                        />
                      </div>
                      <div>
                        <label className="block text-xs font-bold text-slate-600 mb-2">
                          Max Behaviors: {llmParams.max_behaviors}
                        </label>
                        <input
                          type="range"
                          min="1"
                          max="20"
                          step="1"
                          value={llmParams.max_behaviors}
                          onChange={(e) => setLlmParams({...llmParams, max_behaviors: parseInt(e.target.value)})}
                          className="w-full"
                        />
                      </div>
                      <div className="flex items-center gap-2">
                        <input
                          type="checkbox"
                          id="include-archetype"
                          checked={llmParams.include_archetype}
                          onChange={(e) => setLlmParams({...llmParams, include_archetype: e.target.checked})}
                          className="w-4 h-4"
                        />
                        <label htmlFor="include-archetype" className="text-sm text-slate-700 font-medium">
                          Include Archetype
                        </label>
                      </div>
                      <button
                        onClick={fetchLLMContext}
                        className="w-full bg-indigo-600 hover:bg-indigo-700 text-white font-bold py-2 px-4 rounded-lg transition-colors flex items-center justify-center gap-2"
                      >
                        <RefreshCw size={16} />
                        Regenerate Context
                      </button>
                    </div>
                  </details>

                  {/* Usage Example */}
                  <div className="bg-amber-50 border border-amber-200 rounded-xl p-4">
                    <h4 className="text-sm font-bold text-amber-900 mb-2">💡 Usage Example</h4>
                    <p className="text-xs text-amber-800 mb-3">
                      Inject this context into your LLM system prompt to personalize responses:
                    </p>
                    <pre className="text-xs bg-white p-3 rounded border border-amber-200 text-slate-700 overflow-x-auto">
{`// System Prompt
const systemPrompt = \`
You are a helpful AI assistant.

\${llmContext.context}

Adapt your responses to match these preferences.
\`;`}
                    </pre>
                  </div>
                </div>
              ) : (
                <div className="text-center py-12">
                  <AlertCircle className="w-12 h-12 text-red-400 mx-auto mb-4" />
                  <p className="text-slate-600">Failed to load LLM context</p>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ProfileInsights;