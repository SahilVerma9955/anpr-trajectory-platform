import React from 'react';
import { BarChart, Bar, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

function TrafficCharts({ kpis }) {
  const speedData = [
    { name: 'Current', value: kpis.avgSpeed },
    { name: 'Free Flow', value: 50 },
  ];

  const congestionData = [
    { name: 'Congestion', value: (kpis.congestionIndex * 100).toFixed(0) },
    { name: 'Free Flow', value: 100 - (kpis.congestionIndex * 100).toFixed(0) },
  ];

  return (
    <div className="panel">
      <div className="panel-title">Traffic Analytics</div>
      <div className="chart-container" style={{ height: '300px' }}>
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={speedData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="name" />
            <YAxis />
            <Tooltip />
            <Bar dataKey="value" fill="#1e40af" name="Speed (km/h)" />
          </BarChart>
        </ResponsiveContainer>
      </div>
      <p style={{ fontSize: '0.875rem', color: '#6b7280', marginTop: '1rem' }}>
        Current average speed vs. free-flow baseline (50 km/h).
      </p>
    </div>
  );
}

export default TrafficCharts;
