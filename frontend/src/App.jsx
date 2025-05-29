// Using .jsx as Vite typically uses .jsx for files with JSX
import React, { useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Navbar from './components/Navbar';
import PrivateRoute from './components/PrivateRoute';
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import DashboardPage from './pages/DashboardPage';
import BaseDetailPage from './pages/BaseDetailPage'; // Import new page
import TableDetailPage from './pages/TableDetailPage'; // Import new page
import useAuthStore from './store/authStore';
import authService from './services/authService';


function App() {
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated);
  const user = useAuthStore((state) => state.user);
  const token = useAuthStore((state) => state.token);
  const logout = useAuthStore((state) => state.logout);


  useEffect(() => {
    const checkUser = async () => {
      if (token && isAuthenticated && !user?.id) { 
        try {
          await authService.getCurrentUser(); 
        } catch (error) {
          console.error("Session check failed, logging out:", error);
           authService.logout(); 
        }
      } else if (!token && isAuthenticated) {
        logout();
      }
    };
    checkUser();
  }, [isAuthenticated, user, token, logout]);


  return (
    <Router>
      <Navbar />
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />
        
        <Route path="/" element={<PrivateRoute />}>
          <Route index element={<DashboardPage />} /> 
          <Route path="dashboard" element={<DashboardPage />} /> 
          <Route path="bases/:baseId" element={<BaseDetailPage />} /> 
          <Route path="tables/:tableId" element={<TableDetailPage />} /> 
        </Route>
        
        <Route path="*" element={<Navigate to={isAuthenticated ? "/" : "/login"} replace />} />
      </Routes>
    </Router>
  );
}

export default App;
