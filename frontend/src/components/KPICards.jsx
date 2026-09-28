import React from 'react';

function KPICards({ kpis, loading }) {
  const cards = [
    {
      label: 'Total Vehicles',
      value: kpis.vehicleCount,
      unit: 'vehicles',
    },
    {
      label: 'Average Speed',
      value: kpis.avgSpeed.toFixed(1),
      unit: 'km/h',
    },
    {
      label: 'Traffic Flow',
      value: kpis.flowRate.toFixed(2),
      unit: 'vehicles/min',
    },
    {
      label: 'Congestion Index',
      value: (kpis.congestionIndex * 100).toFixed(0),
      unit: '%',
    },
  ];

  return (
    <div className="kpi-grid">
      {cards.map((card, idx) => (
        <div key={idx} className="kpi-card">
          <div className="kpi-label">{card.label}</div>
          <div className="kpi-value">{loading ? '—' : card.value}</div>
          <div className="kpi-unit">{card.unit}</div>
        </div>
      ))}
    </div>
  );
}

export default KPICards;
