// ContextLibraryPage.jsx
import React, { useState } from 'react';
import {
  Search,
  Trash2,
  Calendar,
  Briefcase,
  GraduationCap,
  Home
} from 'lucide-react';

const initialBehaviors = [
  {
    id: 1,
    text: 'Prefers formal academic tone with technical precision and LaTeX citations',
    extractedDate: 'Dec 18, 2025',
    session: 'university',
  },
  {
    id: 2,
    text: 'Uses financial terminology (ARR, CAC, LTV) and structures responses with bullet points',
    extractedDate: 'Dec 17, 2025',
    session: 'work',
  },
  {
    id: 3,
    text: 'Encourages creative freedom with open-ended and exploratory responses',
    extractedDate: 'Dec 15, 2025',
    session: 'defaults',
  },
  {
    id: 4,
    text: 'Uses friendly, conversational tone with analogies and simple examples',
    extractedDate: 'Dec 11, 2025',
    session: 'defaults',
  },
  {
    id: 5,
    text: 'Prioritizes depth over brevity and avoids casual language',
    extractedDate: 'Dec 10, 2025',
    session: 'university',
  },
  {
    id: 6,
    text: 'Maintains confidentiality shield and redacts sensitive information',
    extractedDate: 'Dec 9, 2025',
    session: 'work',
  },
  {
    id: 7,
    text: 'Step-by-step teaching style with practical examples',
    extractedDate: 'Dec 8, 2025',
    session: 'university',
  },
  {
    id: 8,
    text: 'Focuses on data-driven insights with structured analysis',
    extractedDate: 'Dec 7, 2025',
    session: 'work',
  },
  {
    id: 9,
    text: 'Allows metaphors and storytelling in responses',
    extractedDate: 'Dec 6, 2025',
    session: 'defaults',
  },
  {
    id: 10,
    text: 'Uses professional executive tone for business contexts',
    extractedDate: 'Dec 5, 2025',
    session: 'work',
  },
];

const ContextLibraryPage = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [behaviors, setBehaviors] = useState(initialBehaviors);

  const getSessionIcon = (session) => {
    switch (session) {
      case 'work':
        return <Briefcase size={16} className="text-indigo-600" />;
      case 'university':
        return <GraduationCap size={16} className="text-indigo-600" />;
      case 'defaults':
        return <Home size={16} className="text-indigo-600" />;
      default:
        return <Home size={16} className="text-indigo-600" />;
    }
  };

  const getSessionLabel = (session) => {
    return session.charAt(0).toUpperCase() + session.slice(1);
  };

  const handleDelete = (id) => {
    setBehaviors(behaviors.filter(behavior => behavior.id !== id));
  };

  const filteredBehaviors = behaviors.filter(behavior =>
    behavior.text.toLowerCase().includes(searchQuery.toLowerCase()) ||
    behavior.session.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-black text-slate-900 tracking-tight">Behavior Library</h1>
        <p className="text-slate-500 font-medium mt-1">
          See a behavior that incorrectly describes you? You can remove it.
        </p>
      </div>

      {/* Search Bar */}
      <div className="relative group max-w-md">
        <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400 group-focus-within:text-indigo-500 transition-colors" size={18} />
        <input
          type="text"
          placeholder="Search behaviors..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="w-full pl-11 pr-4 py-2.5 bg-slate-100 border-transparent border-2 rounded-xl text-sm font-medium focus:outline-none focus:bg-white focus:border-indigo-500/20 focus:ring-4 focus:ring-indigo-500/5 transition-all outline-none"
        />
      </div>

      {/* Scrollable Behaviors List */}
      <div className="bg-white rounded-3xl border-2 border-slate-200 shadow-md">
        <div className="p-6 border-b border-slate-200">
          <h2 className="text-lg font-bold text-slate-900">
            Extracted Behaviors ({filteredBehaviors.length})
          </h2>
        </div>
        
        <div className="overflow-y-auto max-h-[600px] custom-scrollbar">
          {filteredBehaviors.length > 0 ? (
            <div className="divide-y divide-slate-100">
              {filteredBehaviors.map((behavior) => (
                <div
                  key={behavior.id}
                  className="p-6 hover:bg-slate-50 transition-colors group"
                >
                  <div className="flex items-start justify-between gap-4">
                    <div className="flex-1 space-y-3">
                      <p className="text-slate-800 font-medium leading-relaxed">
                        {behavior.text}
                      </p>
                      
                      <div className="flex items-center gap-4 text-sm">
                        <div className="flex items-center gap-1.5 text-slate-500">
                          <Calendar size={14} />
                          <span className="font-medium">{behavior.extractedDate}</span>
                        </div>
                        
                        <div className="flex items-center gap-1.5 px-2.5 py-1 bg-indigo-50 rounded-lg">
                          {getSessionIcon(behavior.session)}
                          <span className="font-semibold text-indigo-700 text-xs">
                            {getSessionLabel(behavior.session)}
                          </span>
                        </div>
                      </div>
                    </div>
                    
                    <button
                      onClick={() => handleDelete(behavior.id)}
                      className="flex items-center gap-2 px-3 py-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors opacity-0 group-hover:opacity-100"
                      title="Delete behavior"
                    >
                      <Trash2 size={18} />
                    </button>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="p-12 text-center text-slate-400">
              <p className="font-medium">No behaviors found matching your search.</p>
            </div>
          )}
        </div>
      </div>

      {/* Bottom Hint */}
      <div className="text-center">
        <p className="text-sm font-medium text-slate-500">
          New behaviors are <span className="text-indigo-600 font-bold">automatically extracted</span> from your conversations
          <br />
          and saved here when patterns are detected across your sessions.
        </p>
      </div>
    </div>
  );
};

export default ContextLibraryPage;
