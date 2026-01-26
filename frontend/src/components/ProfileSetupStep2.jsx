// src/components/ProfileSetupStep2.jsx
import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { ShieldCheck, Target, Layers, Check } from 'lucide-react';

const ProfileSetupStep2 = () => {
  const [profile, setProfile] = useState({
    name: "Academic Research-Oriented User",
    usage: "Academic Research"
  });

  const navigate = useNavigate();

  return (
    <div className="min-h-screen flex font-sans">
      {/* Left Hero */}
      <div className="hidden lg:flex lg:w-1/2 bg-gradient-to-br from-slate-900 via-indigo-900/90 to-slate-900 text-white relative overflow-hidden rounded-r-[3rem] shadow-2xl">
        <div className="absolute inset-0 bg-gradient-to-t from-black/60 to-transparent"></div>
        <div className="relative z-10 p-16 flex flex-col justify-center">
          <h1 className="text-6xl font-black tracking-tight leading-tight mb-8">
            Your AI<br />Profile is<br />Ready
          </h1>
          <p className="text-xl text-indigo-100 font-medium max-w-lg">
            This identity will evolve as you use AI tools — always under your control.
          </p>
        </div>
      </div>

      {/* Right Side */}
      <div className="flex-1 flex items-center justify-center bg-slate-50 px-8">
        <div className="w-full max-w-2xl">
          <div className="bg-white rounded-[3rem] p-12 shadow-2xl border border-slate-100">
            <div className="text-center mb-10">
              <h2 className="text-4xl font-black text-slate-900">Review your initial profile</h2>
              <p className="text-slate-500 mt-3">Step 2 of 2 • Final confirmation</p>
            </div>

            <div className="bg-indigo-900 rounded-3xl p-8 text-white mb-10">
              <div className="flex items-center gap-3 mb-4">
                <Target size={20} className="text-indigo-300" />
                <span className="text-sm font-bold uppercase text-indigo-300">Inferred Persona</span>
              </div>
              <h3 className="text-3xl font-bold mb-3">{profile.name}</h3>
              <p className="text-indigo-200 italic">
                "An analytical profile optimized for deep domain exploration and objective information synthesis."
              </p>
              <div className="mt-6 flex items-center gap-3">
                <span className="text-sm text-indigo-300">Confidence:</span>
                <div className="flex gap-1">
                  <div className="w-8 h-2 bg-emerald-400 rounded-full"></div>
                  <div className="w-8 h-2 bg-emerald-400 rounded-full"></div>
                  <div className="w-8 h-2 bg-indigo-600 rounded-full"></div>
                </div>
                <span className="text-sm font-bold text-emerald-400">Medium-High</span>
              </div>
            </div>

            <div className="mb-10">
              <div>
                <label className="text-sm font-bold text-slate-600 flex items-center gap-2 mb-2">
                  <Layers size={16} /> Primary Intent
                </label>
                <select
                  value={profile.usage}
                  onChange={(e) => setProfile({ ...profile, usage: e.target.value })}
                  className="w-full px-5 py-4 rounded-2xl border border-slate-200 bg-slate-50 text-slate-800 font-semibold"
                >
                  <option>Academic Research</option>
                  <option>Software Development</option>
                  <option>Content Strategy</option>
                </select>
              </div>
            </div>

            <div className="text-center">
              <button
                onClick={() => navigate('/dashboard')}
                className="px-16 py-6 bg-gradient-to-r from-indigo-600 to-indigo-700 text-white text-xl font-black rounded-full shadow-2xl hover:shadow-3xl hover:scale-105 transition-all duration-300 flex items-center gap-4 mx-auto"
              >
                Confirm and Enter Dashboard
                <Check size={28} strokeWidth={3} />
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ProfileSetupStep2;