import React, { useState, useEffect } from 'react';
import ApiClient from '../api';
import KPICards from './KPICards';
import TrafficMap from './TrafficMap';
import VehicleSearch from './VehicleSearch';
import TrajectoryPanel from './TrajectoryPanel';
import AlertsPanel from './AlertsPanel';
import TrafficCharts from './TrafficCharts';
import '../App.css';

function Dashboard({ apiBaseUrl }) {
  const [api] = useState(new ApiClient(apiBaseUrl));
  const [kpis, setKpis] = useState({
    vehicleCount: 0,
    avgSpeed: 0,
    flowRate: 0,
    congestionIndex: 0,
  });
  const [selectedPlate, setSelectedPlate] = useState(null);
  const [trajectory, setTrajectory] = useState(null);
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadDashboardData();
    const interval = setInterval(loadDashboardData, 30000);
    return () => clearInterval(interval);
  }, []);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      const [density, flow, speed, congestion, alertsData] = await Promise.all([
        api.getAnalyticsDensity(),
        api.getAnalyticsFlow(),
        api.getAnalyticsSpeed(),
        api.getAnalyticsCongestion(),
        api.getAlerts(),
      ]);

      setKpis({
        vehicleCount: density.data.values?.vehicle_count || 0,
        avgSpeed: speed.data.values?.average_speed_kmh || 0,
        flowRate: flow.data.values?.vehicles_per_minute || 0,
        congestionIndex: congestion.data.values?.congestion_index || 0,
      });

      setAlerts(alertsData.data.alerts || []);
      setError(null);
    } catch (err) {
      console.error('Error loading dashboard data:', err);
      setError('Failed to load dashboard data. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleVehicleSearch = async (plate) => {
    try {
      setLoading(true);
      setSelectedPlate(plate);
      const trajResponse = await api.getTrajectory(plate);
      setTrajectory(trajResponse.data);
      setError(null);
    } catch (err) {
      console.error('Error fetching trajectory:', err);
      setError(`Vehicle plate "${plate}" not found or error loading trajectory.`);
      setTrajectory(null);
    } finally {
      setLoading(false);
    }
  };

  const handleAddBlacklist = async (plate, reason) => {
    try {
      await api.addBlacklist(plate, reason);
      setError(null);
      loadDashboardData();
    } catch (err) {
      console.error('Error adding to blacklist:', err);
      setError('Failed to add plate to blacklist.');
    }
  };

  return (
    <div className="app">
      <header className="header">
        <div className="header-content">
          <h1 className="header-title">ANPR Trajectory Platform</h1>
          <div className="header-status">
            <div className="status-indicator"></div>
            <span>System Online</span>
          </div>
        </div>
      </header>

      <main className="main-content">
        {error && <div className="error-message">{error}</div>}

        <KPICards kpis={kpis} loading={loading} />

        <div className="two-column-grid">
          <TrafficMap trajectory={trajectory} selectedPlate={selectedPlate} />
          <TrafficCharts kpis={kpis} />
        </div>

        <div className="two-column-grid">
          <VehicleSearch onSearch={handleVehicleSearch} loading={loading} />
          <AlertsPanel alerts={alerts} onAddBlacklist={handleAddBlacklist} />
        </div>

        {trajectory && selectedPlate && (
          <TrajectoryPanel plate={selectedPlate} trajectory={trajectory} />
        )}
      </main>

      <footer className="footer">
        <p>&copy; 2026 ANPR Trajectory Platform. Demo Version. Use with proper authorization only.</p>
      </footer>
    </div>
  );
}

export default Dashboard;
