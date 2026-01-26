// src/components/ProfileSetupStep1.jsx
import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  BookOpen, 
  Code, 
  PenTool, 
  GraduationCap, 
  User,
  ChevronRight
} from 'lucide-react';

const ProfileSetupStep1 = () => {
  const [selections, setSelections] = useState({
    intent: 'Academic research'
  });

  const navigate = useNavigate();

  const intentOptions = [
    { label: 'Academic research', icon: <BookOpen size={24} /> },
    { label: 'Software development', icon: <Code size={24} /> },
    { label: 'Writing & content', icon: <PenTool size={24} /> },
    { label: 'Learning & studying', icon: <GraduationCap size={24} /> },
    { label: 'General assistance', icon: <User size={24} /> },
  ];

  return (
    <div className="min-h-screen flex font-sans">
      {/* Left Hero */}
      <div className="hidden lg:flex lg:w-1/2 bg-gradient-to-br from-slate-900 via-indigo-900/90 to-slate-900 text-white relative overflow-hidden rounded-r-[3rem] shadow-2xl">
        <div className="absolute inset-0 bg-gradient-to-t from-black/60 to-transparent"></div>
        <div className="relative z-10 p-16 flex flex-col justify-center">
          <h1 className="text-6xl font-black tracking-tight leading-tight mb-8">
            Personalize<br />Your AI<br />Experience
          </h1>
          <p className="text-xl text-indigo-100 font-medium max-w-lg">
            Tell us how you use AI — we’ll tailor responses, tone, and depth from day one.
          </p>
        </div>
      </div>

      {/* Right Form */}
      <div className="flex-1 flex items-center justify-center bg-slate-50 px-8">
        <div className="w-full max-w-2xl">
          <div className="bg-white rounded-[3rem] p-12 shadow-2xl border border-slate-100">
            <div className="text-center mb-10">
              <h2 className="text-4xl font-black text-slate-900">Set up your initial profile</h2>
              <p className="text-slate-500 mt-3">Step 1 of 2 • Personalizing your AI experience</p>
            </div>

            {/* Question 1 */}
            <div className="mb-10">
              <h3 className="text-lg font-bold text-slate-800 mb-6">What will you mainly use AI tools for?</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {intentOptions.map((opt) => (
                  <button
                    key={opt.label}
                    onClick={() => setSelections({ ...selections, intent: opt.label })}
                    className={`flex items-center gap-4 p-6 rounded-2xl border-2 transition-all ${
                      selections.intent === opt.label
                        ? 'border-indigo-600 bg-indigo-50 text-indigo-700 shadow-md'
                        : 'border-slate-200 bg-white hover:border-slate-300'
                    }`}
                  >
                    <div className="w-12 h-12 bg-indigo-100 rounded-xl flex items-center justify-center text-indigo-600">
                      {opt.icon}
                    </div>
                    <span className="font-semibold">{opt.label}</span>
                  </button>
                ))}
              </div>
            </div>

            <div className="mt-12 flex justify-center">
              <button
                onClick={() => navigate('/profile-setup/step2')}
                className="px-12 py-5 bg-gradient-to-r from-indigo-600 to-indigo-700 text-white text-lg font-black rounded-full shadow-xl hover:shadow-2xl hover:scale-105 transition-all duration-300 flex items-center gap-3"
              >
                Continue
                <ChevronRight size={24} strokeWidth={3} />
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ProfileSetupStep1;