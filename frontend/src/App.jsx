// src/App.jsx
import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';

// Import components
import LandingPage from './components/LandingPage';     // New landing page
import Signin from './components/Signin';
import Signup from './components/Signup';               // If you have it
import ProfileSetupStep1 from './components/ProfileSetupStep1';
import ProfileSetupStep2 from './components/ProfileSetupStep2';
import Dashboard from './components/Dashboard';
import DemoPage from './components/DemoPage';           // Demo page for testing

function App() {
  return (
    <AuthProvider>
      <Router>
        <Routes>
          {/* Default route - Landing Page */}
          <Route path="/" element={<LandingPage />} />
          
          {/* Demo Page - For testing with generated data */}
          <Route path="/demo" element={<DemoPage />} />
          
          {/* Auth pages */}
          <Route path="/signin" element={<Signin />} />
          <Route path="/signup" element={<Signup />} />
          
          {/* Onboarding / Profile Setup Flow */}
          <Route path="/profile-setup/step1" element={<ProfileSetupStep1 />} />
          <Route path="/profile-setup/step2" element={<ProfileSetupStep2 />} />
          
          {/* Main Dashboard */}
          <Route path="/dashboard" element={<Dashboard />} />
          
          {/* Optional: Catch-all redirect to landing page */}
          <Route path="*" element={<LandingPage />} />
        </Routes>
      </Router>
    </AuthProvider>
  );
}

export default App;