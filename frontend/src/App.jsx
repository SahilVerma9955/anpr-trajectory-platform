import React, { useState, useEffect } from 'react';
import axios from 'axios';
import Dashboard from './components/Dashboard';
import './App.css';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

function App() {
  const [healthStatus, setHealthStatus] = useState('unknown');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    checkHealth();
  }, []);

  const checkHealth = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/health`, { timeout: 5000 });
      setHealthStatus(response.data.status);
    } catch (error) {
      console.error('Health check failed:', error);
      setHealthStatus('error');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="loading-container">
        <div className="loader"></div>
        <p>Initializing ANPR Platform...</p>
      </div>
    );
  }

  if (healthStatus !== 'ok') {
    return (
      <div className="error-container">
        <h1>Connection Error</h1>
        <p>Unable to connect to the ANPR API at {API_BASE_URL}</p>
        <p>Please ensure the backend is running:</p>
        <code>uvicorn src.api.main:app --reload --port 8000</code>
        <button onClick={checkHealth}>Retry</button>
      </div>
    );
  }

  return <Dashboard apiBaseUrl={API_BASE_URL} />;
}

export default App;
