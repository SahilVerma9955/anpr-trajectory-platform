import React from 'react';

function AlertsPanel({ alerts, onAddBlacklist }) {
  const [plateToAdd, setPlateToAdd] = React.useState('');
  const [reasonToAdd, setReasonToAdd] = React.useState('');

  const handleAddClick = async () => {
    if (plateToAdd.trim()) {
      await onAddBlacklist(plateToAdd.toUpperCase(), reasonToAdd || 'manual');
      setPlateToAdd('');
      setReasonToAdd('');
    }
  };

  return (
    <div className="panel">
      <div className="panel-title">Active Alerts & Watchlist</div>

      {alerts && alerts.length > 0 ? (
        <div>
          {alerts.slice(0, 5).map((alert, idx) => (
            <div key={idx} className={`alert-item ${alert.severity || 'warning'}`}>
              <strong>{alert.normalized_plate}</strong> - {alert.message}
            </div>
          ))}
          {alerts.length > 5 && <p style={{ color: '#6b7280', marginTop: '0.5rem' }}>+{alerts.length - 5} more alerts</p>}
        </div>
      ) : (
        <div className="empty-state">
          <p>No active alerts</p>
        </div>
      )}

      <div style={{ marginTop: '1.5rem', paddingTop: '1.5rem', borderTop: '1px solid var(--border-color)' }}>
        <h4 style={{ fontSize: '0.875rem', fontWeight: '600', textTransform: 'uppercase', marginBottom: '0.75rem' }}>
          Add to Watchlist
        </h4>
        <input
          type="text"
          placeholder="Plate: DL01AB1234"
          value={plateToAdd}
          onChange={(e) => setPlateToAdd(e.target.value.toUpperCase())}
          style={{ marginBottom: '0.5rem', width: '100%' }}
        />
        <input
          type="text"
          placeholder="Reason (optional)"
          value={reasonToAdd}
          onChange={(e) => setReasonToAdd(e.target.value)}
          style={{ marginBottom: '0.5rem', width: '100%' }}
        />
        <button onClick={handleAddClick} style={{ width: '100%' }}>
          Add to Watchlist
        </button>
      </div>
    </div>
  );
}

export default AlertsPanel;
