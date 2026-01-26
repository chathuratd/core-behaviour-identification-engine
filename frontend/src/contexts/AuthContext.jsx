import React, { createContext, useContext, useState, useEffect } from 'react';

const AuthContext = createContext(null);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Check if user is already logged in (from localStorage)
    const storedUserId = localStorage.getItem('userId');
    const storedUserEmail = localStorage.getItem('userEmail');
    
    if (storedUserId) {
      setUser({
        userId: storedUserId,
        email: storedUserEmail || 'demo@example.com',
      });
    }
    setLoading(false);
  }, []);

  const login = (email, password) => {
    // TODO: Implement actual authentication with backend
    // For now, using mock authentication
    const userId = 'user_665390'; // Replace with actual user ID from backend
    
    localStorage.setItem('userId', userId);
    localStorage.setItem('userEmail', email);
    
    setUser({
      userId,
      email,
    });
    
    return Promise.resolve({ success: true });
  };

  const signup = (email, password) => {
    // TODO: Implement actual signup with backend
    // For now, using mock signup
    const userId = `user_${Date.now()}`; // Generate unique user ID
    
    localStorage.setItem('userId', userId);
    localStorage.setItem('userEmail', email);
    
    setUser({
      userId,
      email,
    });
    
    return Promise.resolve({ success: true });
  };

  const logout = () => {
    localStorage.removeItem('userId');
    localStorage.removeItem('userEmail');
    setUser(null);
  };

  const value = {
    user,
    loading,
    login,
    signup,
    logout,
    isAuthenticated: !!user,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export default AuthContext;
