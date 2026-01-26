// src/components/Signup.jsx
import React from 'react';
import { useNavigate } from 'react-router-dom';
import {
  ShieldCheck,
  ArrowRight,
  Chrome,
  Github,
  Bot,
  Sparkles,
  Lock,
} from 'lucide-react';

const Signup = () => {
  const navigate = useNavigate();

  const handleSignUp = () => {
    // After signup, go directly to profile setup
    navigate('/profile-setup/step1');
  };

  return (
    <div className="min-h-screen flex font-sans">
      {/* Left Hero - Same as Sign In */}
      <div className="hidden lg:flex lg:w-1/2 bg-gradient-to-br from-slate-900 via-indigo-900/90 to-slate-900 text-white relative overflow-hidden rounded-r-[3rem] shadow-2xl">
        <div className="absolute inset-0 bg-gradient-to-t from-black/60 to-transparent"></div>
        
        <div className="relative z-10 flex flex-col justify-between h-full p-16">
          <div>
            <p className="text-indigo-200 text-lg font-medium mb-12 leading-relaxed">
              One secure hub to control how every AI sees and remembers you.
            </p>
            
            <h1 className="text-6xl font-black tracking-tight leading-tight mb-8">
              Control<br />Your AI<br />Context
            </h1>

            <p className="text-xl text-indigo-100 font-medium max-w-lg">
              Manage your preferences across every AI — keep personal data private, align tone and expertise, and stay in full control.
            </p>
          </div>
          
          {/* Same AI Chat Phone Mockup */}
          <div className="relative max-w-md mx-auto">
            <div className="bg-slate-800 rounded-[3rem] p-8 shadow-2xl border border-slate-700">
              <div className="bg-white rounded-[2rem] overflow-hidden shadow-inner">
                <div className="bg-gradient-to-b from-indigo-50 to-slate-50 h-96 flex flex-col">
                  <div className="p-4 border-b border-slate-200 flex items-center gap-3">
                    <div className="w-10 h-10 bg-indigo-600 rounded-xl flex items-center justify-center text-white font-bold">
                      M
                    </div>
                    <div>
                      <div className="font-bold text-slate-900">Memora</div>
                      <div className="text-xs text-emerald-600 flex items-center gap-1">
                        <div className="w-2 h-2 bg-emerald-500 rounded-full animate-pulse"></div>
                        Shield Active
                      </div>
                    </div>
                  </div>

                  <div className="flex-1 p-4 space-y-4 overflow-y-auto">
                    <div className="flex items-start gap-3">
                      <div className="w-8 h-8 bg-slate-200 rounded-full flex items-center justify-center">
                        <Bot size={16} className="text-slate-600" />
                      </div>
                      <div className="bg-white rounded-2xl rounded-tl-none px-4 py-3 shadow-sm max-w-xs">
                        <p className="text-sm text-slate-700">How can I help you today?</p>
                      </div>
                    </div>

                    <div className="flex items-start gap-3 justify-end">
                      <div className="bg-indigo-600 rounded-2xl rounded-tr-none px-4 py-3 shadow-sm max-w-xs">
                        <p className="text-sm text-white">Explain quantum error correction simply.</p>
                      </div>
                    </div>

                    <div className="flex items-start gap-3">
                      <div className="w-8 h-8 bg-slate-200 rounded-full flex items-center justify-center">
                        <Sparkles size={16} className="text-indigo-600" />
                      </div>
                      <div className="bg-white rounded-2xl rounded-tl-none px-4 py-3 shadow-sm max-w-md">
                        <p className="text-sm text-slate-700 font-medium">Using Learning & Studying profile</p>
                        <p className="text-sm text-slate-600 mt-1">Think of quantum errors like typos in a message...</p>
                      </div>
                    </div>
                  </div>

                  <div className="p-4 border-t border-slate-200 flex items-center gap-3">
                    <Lock size={18} className="text-emerald-600" />
                    <input
                      type="text"
                      placeholder="Type your message..."
                      className="flex-1 text-sm bg-slate-100 rounded-full px-4 py-2 focus:outline-none"
                    />
                    <ShieldCheck size={18} className="text-emerald-600" />
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Right Form - Signup Version */}
      <div className="flex-1 flex items-center justify-center bg-slate-50 px-8">
        <div className="w-full max-w-md">
          <div className="text-center mb-12">
            <div className="inline-flex items-center gap-3 mb-8">
              <div className="w-12 h-12 bg-indigo-600 rounded-2xl flex items-center justify-center text-white shadow-xl">
                <ShieldCheck size={28} strokeWidth={2.5} />
              </div>
              <span className="font-extrabold text-3xl tracking-tight text-slate-900">
                Memora
              </span>
            </div>
            <h2 className="text-4xl font-black text-slate-900 mb-4">Create Account</h2>
          </div>

          <div className="bg-white rounded-[3rem] p-12 shadow-2xl border border-slate-100">
            {/* OAuth Buttons */}
            <div className="space-y-4 mb-10">
              <button className="w-full flex items-center justify-center gap-3 py-4 border border-slate-200 rounded-full font-bold text-slate-700 hover:bg-slate-50 transition">
                <Chrome size={22} /> Continue with Google
              </button>
              <button className="w-full flex items-center justify-center gap-3 py-4 border border-slate-200 rounded-full font-bold text-slate-700 hover:bg-slate-50 transition">
                <Github size={22} /> Continue with GitHub
              </button>
            </div>

            <div className="relative my-8">
              <div className="absolute inset-0 flex items-center">
                <div className="w-full border-t border-slate-200"></div>
              </div>
              <div className="relative flex justify-center text-sm">
                <span className="bg-white px-4 text-slate-500 font-bold">Or</span>
              </div>
            </div>

            {/* Signup Form Fields */}
            <form className="space-y-6">
              <input
                type="text"
                placeholder="Full Name"
                className="w-full px-6 py-5 bg-transparent border border-slate-300 rounded-full text-lg focus:outline-none focus:border-indigo-500 focus:ring-4 focus:ring-indigo-100 transition"
              />
              <input
                type="email"
                placeholder="Email Address"
                className="w-full px-6 py-5 bg-transparent border border-slate-300 rounded-full text-lg focus:outline-none focus:border-indigo-500 focus:ring-4 focus:ring-indigo-100 transition"
              />
              <div className="relative">
                <input
                  type="password"
                  placeholder="Password"
                  className="w-full px-6 py-5 bg-transparent border border-slate-300 rounded-full text-lg focus:outline-none focus:border-indigo-500 focus:ring-4 focus:ring-indigo-100 transition"
                />
                <Lock size={20} className="absolute right-6 top-1/2 -translate-y-1/2 text-slate-400" />
              </div>

              <button
                type="button"
                onClick={handleSignUp}
                className="w-full py-5 bg-gradient-to-r from-indigo-600 to-indigo-700 text-white text-lg font-black rounded-full shadow-xl hover:shadow-2xl hover:scale-105 transition-all duration-300 flex items-center justify-center gap-3"
              >
                Create Account
                <ArrowRight size={24} strokeWidth={3} />
              </button>
            </form>

            <p className="text-center mt-10 text-sm text-slate-600">
              Already have an account?{' '}
              <a href="/signin" className="font-bold text-indigo-600 hover:underline">
                Sign In
              </a>
            </p>
          </div>

          <p className="text-center mt-12 text-xs text-slate-400">
            © 2005-2025 Memora Inc. • Contact Us • English ▼
          </p>
        </div>
      </div>
    </div>
  );
};

export default Signup;