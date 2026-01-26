// Dashboard.jsx
import React, { useState, useCallback, useEffect } from 'react';
import {
  LayoutDashboard,
  Settings,
  ShieldCheck,
  Activity,
  ToggleLeft,
  ToggleRight,
  ExternalLink,
  BrainCircuit,
  Lock,
  MoreVertical,
  Search,
  Bell,
  Zap,
  Database,
  ChevronRight,
  Wifi,
  History,
  Shield,
  Layers,
  Sparkles,
  ArrowUpRight,
  CircleDot,
  Loader2,
  Check
} from 'lucide-react';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import ProfileInsights from './ProfileInsights';
import SessionManagement from './SessionManagement';
import ContextLibraryPage from './ContextLibrary';
import { API_ENDPOINTS } from '../config/api';

const chartData = [
  { name: 'Mon', value: 400 },
  { name: 'Tue', value: 300 },
  { name: 'Wed', value: 600 },
  { name: 'Thu', value: 800 },
  { name: 'Fri', value: 500 },
  { name: 'Sat', value: 900 },
  { name: 'Sun', value: 1100 },
];

const Dashboard = () => {
  const [activeModal, setActiveModal] = useState(null);
  const [currentPage, setCurrentPage] = useState('dashboard');
  const [isSidebarOpen, setSidebarOpen] = useState(true);
  const [profileData, setProfileData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [analyzing, setAnalyzing] = useState(false);
  const [analysisSuccess, setAnalysisSuccess] = useState(false);
  const [tools, setTools] = useState([
    { id: 1, name: 'ChatGPT Plus', connected: true, lastSync: '2m ago', usage: 'High', icon: 'zap' },
    { id: 2, name: 'Claude 3.5 Sonnet', connected: true, lastSync: '1h ago', usage: 'Medium', icon: 'brain' },
    { id: 3, name: 'Google Gemini', connected: false, lastSync: '-', usage: 'None', icon: 'sparkles' },
  ]);

  // Fetch profile data for dashboard statistics
  useEffect(() => {
    if (currentPage === 'dashboard') {
      fetchDashboardData();
    }
  }, [currentPage]);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      const userId = localStorage.getItem('userId') || 'user_665390'; // Replace with actual user ID from auth context
      const response = await fetch(API_ENDPOINTS.getUserProfile(userId));
      
      if (response.ok) {
        const data = await response.json();
        setProfileData(data);
      } else if (response.status === 404) {
        console.log('No profile found yet. User may need to run analysis first.');
        setProfileData(null);
      } else {
        console.error('Error fetching dashboard data:', response.statusText);
      }
    } catch (err) {
      console.error('Error fetching dashboard data:', err);
    } finally {
      setLoading(false);
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
      
      // Refresh dashboard after 1 second
      setTimeout(() => {
        fetchDashboardData();
      }, 1000);
      
    } catch (err) {
      console.error('Error analyzing profile:', err);
      alert('Failed to analyze profile: ' + err.message);
    } finally {
      setAnalyzing(false);
    }
  };

  const toggleTool = useCallback((id) => {
    setTools(prev => prev.map(t => t.id === id ? { ...t, connected: !t.connected } : t));
  }, []);

  // Calculate statistics from profile data
  const stats = profileData ? [
    { 
      label: 'Total Observations', 
      value: profileData.statistics?.total_behaviors_analyzed || 0, 
      change: '+14%', 
      type: 'positive', 
      icon: Activity, 
      color: 'text-indigo-600', 
      bg: 'bg-indigo-50' 
    },
    { 
      label: 'Behavior Clusters', 
      value: profileData.statistics?.clusters_formed || 0, 
      change: '+8%', 
      type: 'positive', 
      icon: Database, 
      color: 'text-blue-600', 
      bg: 'bg-blue-50' 
    },
  ] : [
    { label: 'Total Observations', value: '...', change: '', type: 'positive', icon: Activity, color: 'text-indigo-600', bg: 'bg-indigo-50' },
    { label: 'Behavior Clusters', value: '...', change: '', type: 'positive', icon: Database, color: 'text-blue-600', bg: 'bg-blue-50' },
  ];

  return (
    <div className="flex h-screen overflow-hidden bg-slate-50 font-sans text-slate-900">
      {/* Sidebar */}
      <aside className={`fixed inset-y-0 left-0 z-50 w-72 bg-white border-r border-slate-200 transition-transform duration-300 transform ${isSidebarOpen ? 'translate-x-0' : '-translate-x-full'} lg:relative lg:translate-x-0`}>
        <div className="flex flex-col h-full">
          <div className="p-8">
            <div className="flex items-center gap-3 mb-10 group cursor-pointer">
              <div className="w-11 h-11 bg-indigo-600 rounded-2xl flex items-center justify-center text-white shadow-xl shadow-indigo-200 group-hover:scale-110 transition-transform duration-300">
                <ShieldCheck size={26} strokeWidth={2.5} />
              </div>
              <div>
                <span className="font-extrabold text-2xl tracking-tight text-slate-900 block">Memora</span>
                <span className="text-[10px] font-bold text-slate-400 uppercase tracking-[0.2em]">Enterprise Shield</span>
              </div>
            </div>
            <nav className="space-y-1.5">
              <NavItem icon={<LayoutDashboard size={20} />} label="Dashboard" active={currentPage === 'dashboard'} onClick={() => { setCurrentPage('dashboard'); setActiveModal(null); }} />
              <NavItem icon={<Layers size={20} />} label="Behavior Library" active={currentPage === 'library'} onClick={() => { setCurrentPage('library'); setActiveModal(null); }} />
              <NavItem icon={<BrainCircuit size={20} />} label="Profile Insights" active={currentPage === 'insights'} onClick={() => { setCurrentPage('insights'); setActiveModal(null); }} />
              <NavItem icon={<History size={20} />} label="Session History" active={currentPage === 'sessions'} onClick={() => { setCurrentPage('sessions'); setActiveModal(null); }} />
              <NavItem icon={<Settings size={20} />} label="Settings" />
            </nav>
          </div>
          <div className="mt-auto p-6">
            <div className="p-5 bg-indigo-50/50 rounded-2xl border border-indigo-100">
              <div className="flex justify-between items-center mb-3">
                <span className="text-xs font-bold text-slate-500">Storage Capacity</span>
                <span className="text-xs font-black text-indigo-700">78%</span>
              </div>
              <div className="w-full bg-indigo-100 rounded-full h-2 mb-3 overflow-hidden">
                <div className="bg-gradient-to-r from-indigo-500 to-indigo-700 h-full rounded-full w-[78%] transition-all duration-1000 ease-out"></div>
              </div>
              <p className="text-[10px] text-indigo-400 font-medium">1.2GB of 1.5GB allocated</p>
            </div>
          
            <div className="mt-6 flex items-center justify-between px-2">
              <div className="flex items-center gap-2">
                <div className="w-2.5 h-2.5 rounded-full bg-emerald-500 animate-pulse"></div>
                <span className="text-xs font-bold text-slate-500 uppercase tracking-widest">Network Live</span>
              </div>
              <CircleDot size={14} className="text-slate-300" />
            </div>
          </div>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 flex flex-col min-w-0 overflow-hidden">
        {/* Navbar */}
        <header className="h-20 bg-white border-b border-slate-200 flex items-center justify-between px-8 shrink-0">
          <div className="flex-1 max-w-xl">
            <div className="relative group">
              <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400 group-focus-within:text-indigo-500 transition-colors" size={18} />
              <input
                type="text"
                placeholder={currentPage === 'library' ? 'Search behaviors, prompts...' : 'Find sessions, profiles, or redaction logs...'}
                className="w-full pl-11 pr-4 py-2.5 bg-slate-100 border-transparent border-2 rounded-xl text-sm font-medium focus:outline-none focus:bg-white focus:border-indigo-500/20 focus:ring-4 focus:ring-indigo-500/5 transition-all outline-none"
              />
            </div>
          </div>
          <div className="flex items-center gap-6 ml-4">
             <div className="hidden md:flex flex-col items-end mr-2">
                <span className="text-sm font-bold text-slate-900">Alex Rivera</span>
                <span className="text-[10px] font-bold text-emerald-500 uppercase">Security Lead</span>
             </div>
           
             <button className="relative p-2.5 bg-white hover:bg-slate-50 rounded-xl border border-slate-200 text-slate-500 transition-all hover:shadow-lg">
                <Bell size={20} />
                <span className="absolute top-2.5 right-2.5 w-2 h-2 bg-rose-500 rounded-full ring-2 ring-white"></span>
             </button>
             <div className="h-10 w-px bg-slate-200"></div>
             <div className="flex items-center gap-3">
               <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-slate-800 to-slate-900 flex items-center justify-center text-white font-bold text-sm shadow-lg shadow-slate-200">
                  AR
               </div>
               <button className="p-1.5 hover:bg-slate-100 rounded-lg text-slate-400">
                  <MoreVertical size={18} />
               </button>
             </div>
          </div>
        </header>

        {/* Scrollable Content */}
        <div className="flex-1 overflow-y-auto p-8 bg-slate-50/50">
          <div className="max-w-7xl mx-auto">
            {currentPage === 'dashboard' && (
              <div className="space-y-8">
                {/* Dashboard Content */}
                <div className="flex justify-between items-end">
                  <div>
                    <h1 className="text-3xl font-black text-slate-900 tracking-tight">Enterprise Overview</h1>
                    <p className="text-slate-500 font-medium mt-1">Monitor real-time context isolation and privacy shields.</p>
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  {stats.map((stat, i) => (
                    <div key={i} className="group bg-white p-6 rounded-2xl border border-slate-200 shadow-sm hover:shadow-xl hover:-translate-y-1 transition-all duration-300">
                      <div className="flex justify-between items-start mb-4">
                        <div className={`p-3 rounded-xl ${stat.bg} ${stat.color} group-hover:scale-110 transition-transform`}>
                          <stat.icon size={22} strokeWidth={2.5} />
                        </div>
                        <div className={`flex items-center gap-1 text-xs font-bold px-2.5 py-1 rounded-full ${stat.type === 'positive' ? 'bg-emerald-50 text-emerald-600' : 'bg-slate-50 text-slate-500'}`}>
                          {stat.type === 'positive' && <ArrowUpRight size={14} />}
                          {stat.change}
                        </div>
                      </div>
                      <div className="space-y-1">
                        <p className="text-xs font-bold text-slate-400 uppercase tracking-widest leading-none">{stat.label}</p>
                        <p className="text-3xl font-black text-slate-900 leading-none">{stat.value}</p>
                      </div>
                      <div className="mt-4 pt-4 border-t border-slate-50 flex items-center justify-between">
                         
                         <div className="flex gap-0.5">
                           {[1,2,3,4,5].map(dot => <div key={dot} className={`w-1 h-1 rounded-full ${dot <= 4 ? 'bg-indigo-300' : 'bg-slate-100'}`}></div>)}
                         </div>
                      </div>
                    </div>
                  ))}
                </div>

                <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                  <div className="lg:col-span-2 relative group overflow-hidden bg-white rounded-[2.5rem] p-10 border border-slate-200 shadow-xl shadow-slate-200/40">
                    <div className="absolute top-0 right-0 w-[400px] h-[400px] bg-gradient-to-br from-indigo-50/50 to-transparent rounded-full -mr-40 -mt-40 z-0 opacity-80 group-hover:scale-110 transition-transform duration-1000"></div>
                  
                    <div className="relative z-10 flex flex-col md:flex-row justify-between h-full gap-8">
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-6">
                          <span className="px-4 py-1.5 bg-slate-900 text-white text-[11px] font-black rounded-full uppercase tracking-widest shadow-lg shadow-slate-200">
                            {loading ? 'Loading...' : 'Current Active Profile'}
                          </span>
                          <div className="flex items-center gap-1.5 px-3 py-1.5 bg-emerald-50 text-emerald-600 text-[11px] font-bold rounded-full border border-emerald-100/50">
                            <ShieldCheck size={14} strokeWidth={2.5} /> Active Shield
                          </div>
                        </div>
                      
                        <h2 className="text-4xl font-black text-slate-900 mb-4 tracking-tight leading-tight">
                          {loading ? (
                            <div className="flex items-center gap-3">
                              <Loader2 className="w-8 h-8 animate-spin text-indigo-600" />
                              <span className="text-2xl">Loading Profile...</span>
                            </div>
                          ) : profileData?.archetype ? (
                            <>
                              {profileData.archetype.split(' ').slice(0, 2).join(' ')}
                              <br />
                              <span className="text-indigo-600">
                                {profileData.archetype.split(' ').slice(2).join(' ')}
                              </span>
                            </>
                          ) : (
                            <>Behavioral Profile <br/><span className="text-indigo-600">Analysis</span></>
                          )}
                        </h2>
                        
                        <p className="text-slate-500 text-lg mb-8 max-w-lg leading-relaxed font-medium italic">
                          {loading ? (
                            '"Analyzing your interaction patterns..."'
                          ) : profileData ? (
                            `"${profileData.statistics?.clusters_formed || 0} behavior clusters identified across ${Math.round(profileData.statistics?.analysis_time_span_days || 0)} days of interactions."`
                          ) : (
                            '"Your personalized behavior analysis dashboard."'
                          )}
                        </p>
                      
                        <div className="flex flex-wrap gap-4">
                          <button 
                            onClick={runProfileAnalysis}
                            disabled={analyzing}
                            className={`px-8 py-3.5 rounded-2xl text-sm font-bold shadow-xl transition-all duration-300 flex items-center gap-2 ${
                              analyzing 
                                ? 'bg-slate-400 cursor-not-allowed' 
                                : analysisSuccess
                                ? 'bg-green-600 hover:bg-green-700 shadow-green-100'
                                : 'bg-gradient-to-r from-blue-600 to-cyan-600 hover:from-blue-700 hover:to-cyan-700 shadow-blue-100 hover:shadow-2xl hover:-translate-y-0.5'
                            } text-white`}
                          >
                            {analyzing ? (
                              <>
                                <Loader2 size={18} className="animate-spin" strokeWidth={2.5} />
                                Running Analysis...
                              </>
                            ) : analysisSuccess ? (
                              <>
                                <Check size={18} strokeWidth={2.5} />
                                Analysis Complete!
                              </>
                            ) : (
                              <>
                                <Zap size={18} strokeWidth={2.5} />
                                Run Analysis
                              </>
                            )}
                          </button>
                          <button 
                            onClick={() => setCurrentPage('insights')} 
                            className="bg-indigo-600 text-white px-8 py-3.5 rounded-2xl text-sm font-bold shadow-xl shadow-indigo-100 hover:shadow-2xl hover:bg-indigo-700 hover:-translate-y-0.5 transition-all duration-300 flex items-center gap-2"
                          >
                            View Profile <ChevronRight size={18} strokeWidth={2.5} />
                          </button>
                          <button 
                            onClick={() => setCurrentPage('library')}
                            className="px-8 py-3.5 rounded-2xl text-sm font-bold text-slate-600 hover:bg-slate-50 border border-slate-200 transition-all duration-300 flex items-center gap-2"
                          >
                            View Library <Layers size={16} strokeWidth={2.5} />
                          </button>
                        </div>
                      </div>
                      
                      <div className="flex flex-col items-center justify-center min-w-[200px] space-y-3">
                        {loading ? (
                          <div className="w-40 h-40 flex items-center justify-center">
                            <Loader2 className="w-12 h-12 animate-spin text-indigo-600" />
                          </div>
                        ) : profileData ? (
                          <>
                            <div className="bg-white rounded-2xl p-6 w-full text-center border border-slate-200 shadow-sm group-hover:shadow-xl transition-all">
                              <div className="flex items-center justify-center gap-2 mb-2">
                                <div className="w-2 h-2 rounded-full bg-indigo-500"></div>
                                <span className="text-[10px] font-black text-indigo-600 uppercase tracking-widest">Core</span>
                              </div>
                              <div className="text-4xl font-black text-slate-900 mb-1">
                                {profileData.behavior_clusters?.filter(c => c.tier === 'PRIMARY').length || 0}
                              </div>
                              <div className="text-xs font-bold text-slate-400 uppercase tracking-wider">
                                Defining traits
                              </div>
                            </div>
                            
                            <div className="bg-white rounded-2xl p-6 w-full text-center border border-slate-200 shadow-sm group-hover:shadow-xl transition-all">
                              <div className="flex items-center justify-center gap-2 mb-2">
                                <div className="w-2 h-2 rounded-full bg-blue-500"></div>
                                <span className="text-[10px] font-black text-blue-600 uppercase tracking-widest">Supporting</span>
                              </div>
                              <div className="text-4xl font-black text-slate-900 mb-1">
                                {profileData.behavior_clusters?.filter(c => c.tier === 'SECONDARY').length || 0}
                              </div>
                              <div className="text-xs font-bold text-slate-400 uppercase tracking-wider">
                                Contextual
                              </div>
                            </div>
                            
                            <div className="bg-slate-50 rounded-2xl p-4 w-full text-center border border-slate-200">
                              <div className="text-2xl font-black text-slate-900">
                                {Math.round(profileData.statistics?.analysis_time_span_days || 0)}d
                              </div>
                              <div className="text-xs font-bold text-slate-600 uppercase tracking-wider mt-1">
                                Tracked
                              </div>
                            </div>
                          </>
                        ) : (
                          <div className="w-40 h-40 relative flex items-center justify-center p-4">
                            <ResponsiveContainer width="100%" height="100%">
                               <AreaChart data={chartData}>
                                 <Area type="monotone" dataKey="value" stroke="#4f46e5" fill="#e0e7ff" strokeWidth={4} />
                               </AreaChart>
                            </ResponsiveContainer>
                            <div className="absolute inset-0 flex flex-col items-center justify-center bg-white/40 backdrop-blur-[2px] rounded-full">
                              <span className="text-4xl font-black text-slate-900 tracking-tighter">--</span>
                              <span className="text-[10px] font-bold text-indigo-500 uppercase tracking-widest">No Data</span>
                            </div>
                          </div>
                        )}
                      </div>
                    </div>
                  </div>

                  <div className="bg-gradient-to-br from-indigo-600 to-indigo-900 rounded-[2.5rem] p-10 text-white shadow-2xl shadow-indigo-200 flex flex-col justify-between relative overflow-hidden group">
                    <div className="absolute top-0 right-0 p-10 opacity-5 group-hover:scale-125 transition-transform duration-700">
                      <Database size={180} strokeWidth={1} />
                    </div>
                  
                    <div>
                      <div className="flex justify-between items-start mb-8">
                        <div className="w-14 h-14 bg-white/15 rounded-2xl flex items-center justify-center backdrop-blur-md border border-white/20 shadow-xl group-hover:rotate-12 transition-transform">
                          <Lock size={28} className="text-white"/>
                        </div>
                        <div className="flex flex-col items-end">
                          <span className="text-[10px] font-black text-indigo-200 uppercase tracking-[0.2em]">Vault Status</span>
                          <span className="text-4xl font-black mt-1 tracking-tighter">SECURED</span>
                        </div>
                      </div>
                      <h3 className="font-black text-2xl tracking-tight mb-2">Isolation Matrix</h3>
                      <p className="text-indigo-100/70 text-sm font-medium leading-relaxed">
                        Personal and business data are currently split into 4 isolated context containers.
                      </p>
                    </div>
                    <div className="space-y-4 mt-10">
                       <div className="flex justify-between items-center text-xs font-bold text-indigo-200/60 uppercase">
                          <span>Sync Integrity</span>
                          <span>Verified</span>
                       </div>
                       <button
                        onClick={() => setCurrentPage('sessions')}
                        className="w-full bg-white text-indigo-900 py-4 rounded-2xl text-sm font-black hover:bg-indigo-50 transition-all shadow-xl flex items-center justify-center gap-2 group/btn active:scale-95"
                      >
                        Context Control <ArrowUpRight size={18} className="group-hover/btn:translate-x-0.5 group-hover/btn:-translate-y-0.5 transition-transform" strokeWidth={2.5} />
                      </button>
                    </div>
                  </div>
                </div>

                <div className="space-y-6">
                  <div className="flex justify-between items-center">
                    <h3 className="text-xl font-black flex items-center gap-3">
                      <Wifi size={22} className="text-indigo-500" /> Active AI Interfaces
                    </h3>
                    <button className="text-xs font-bold text-indigo-600 hover:bg-indigo-50 px-3 py-1.5 rounded-lg transition-colors">Manage All Connections</button>
                  </div>
                  
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
                      {tools.map((tool) => (
                        <div key={tool.id} className="group bg-white p-6 rounded-3xl border border-slate-200 shadow-sm hover:shadow-xl hover:border-indigo-100 transition-all">
                          <div className="flex justify-between items-start mb-5">
                            <div className={`w-14 h-14 rounded-2xl flex items-center justify-center border-2 transition-all duration-500 ${tool.connected ? 'bg-indigo-50 border-indigo-100 text-indigo-600 scale-100 shadow-lg shadow-indigo-50' : 'bg-slate-50 border-slate-100 text-slate-300 scale-95 opacity-50'}`}>
                              {tool.icon === 'zap' && <Zap size={28} strokeWidth={2.5} />}
                              {tool.icon === 'brain' && <BrainCircuit size={28} strokeWidth={2.5} />}
                              {tool.icon === 'sparkles' && <Sparkles size={28} strokeWidth={2.5} />}
                            </div>
                            <button onClick={() => toggleTool(tool.id)} className="transition-all transform hover:scale-110 active:scale-90">
                              {tool.connected ?
                                <ToggleRight size={40} className="text-indigo-600 drop-shadow-sm" /> :
                                <ToggleLeft size={40} className="text-slate-300" />
                              }
                            </button>
                          </div>
                        
                          <div className="mb-5">
                            <h4 className="font-extrabold text-lg text-slate-900 tracking-tight">{tool.name}</h4>
                            <div className="flex items-center gap-2 mt-1.5">
                              <div className={`w-2 h-2 rounded-full ${tool.connected ? 'bg-emerald-500 shadow-[0_0_12px_rgba(16,185,129,0.8)] animate-pulse' : 'bg-slate-300'}`}></div>
                              <span className={`text-[11px] font-black uppercase tracking-widest ${tool.connected ? 'text-emerald-600' : 'text-slate-400'}`}>{tool.connected ? 'Live Stream' : 'Offline'}</span>
                            </div>
                          </div>
                          <div className="flex items-center justify-between pt-5 border-t border-slate-50">
                            <div className="flex items-center gap-1.5">
                               <Activity size={12} className="text-slate-400" />
                               <span className="text-[10px] font-bold text-slate-400 uppercase tracking-widest">Usage: {tool.usage}</span>
                            </div>
                            <span className="text-[10px] font-bold text-slate-400 uppercase tracking-widest">Last Sync: {tool.lastSync}</span>
                          </div>
                        </div>
                      ))}
                    
                    <button className="border-2 border-dashed border-slate-200 rounded-3xl flex flex-col items-center justify-center p-8 text-slate-400 hover:bg-slate-50 hover:border-indigo-300 hover:text-indigo-600 transition-all gap-4 min-h-[180px] group">
                      <div className="w-14 h-14 bg-slate-100 rounded-2xl flex items-center justify-center group-hover:bg-indigo-50 transition-colors">
                        <ExternalLink size={24} />
                      </div>
                      <span className="text-sm font-black uppercase tracking-[0.2em]">Add New Interface</span>
                    </button>
                  </div>
                </div>
              </div>
            )}

            {currentPage === 'library' && (
              <ContextLibraryPage />
            )}

            {currentPage === 'insights' && (
              <ProfileInsights />
            )}

            {currentPage === 'sessions' && (
              <SessionManagement />
            )}
          </div>
        </div>
      </main>

      {/* Modals (keep for other features) */}
    </div>
  );
};

// Sub-components
const NavItem = ({ icon, label, active, onClick }) => (
  <button
    onClick={onClick}
    className={`w-full flex items-center gap-3.5 px-6 py-4 rounded-2xl font-bold text-sm transition-all group ${
      active
        ? 'bg-indigo-600 text-white shadow-xl shadow-indigo-100 translate-x-1'
        : 'text-slate-500 hover:bg-slate-50 hover:text-slate-900'
    }`}
  >
    <div className={`${active ? 'text-white' : 'text-slate-400 group-hover:text-indigo-500 transition-colors'}`}>
      {icon}
    </div>
    <span className="tracking-tight">{label}</span>
    {active && <div className="ml-auto w-1.5 h-1.5 bg-white rounded-full"></div>}
  </button>
);

const ActivityLogItem = ({ title, desc, time, type }) => {
  const styles = {
    security: { color: 'text-rose-500', bg: 'bg-rose-50', icon: ShieldCheck },
    context: { color: 'text-indigo-500', bg: 'bg-indigo-50', icon: Database },
    connection: { color: 'text-blue-500', bg: 'bg-blue-50', icon: Wifi },
    analysis: { color: 'text-amber-500', bg: 'bg-amber-50', icon: BrainCircuit },
  };
  const { color, bg, icon: Icon } = styles[type];

  return (
    <div className="relative pl-10">
      <div className={`absolute left-0 top-1 w-6 h-6 rounded-full border-[3px] border-white shadow-md flex items-center justify-center ${bg} ${color} z-10 transition-transform hover:scale-125 cursor-help`}>
        <Icon size={10} strokeWidth={3} />
      </div>
      <div>
        <h4 className="text-[13px] font-black text-slate-900 tracking-tight">{title}</h4>
        <p className="text-[12px] text-slate-500 font-medium leading-relaxed mt-0.5">{desc}</p>
        <span className="text-[9px] font-black text-slate-300 mt-2 block uppercase tracking-widest">{time}</span>
      </div>
    </div>
  );
};

export default Dashboard;