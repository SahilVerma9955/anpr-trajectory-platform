import React from 'react';

function TrajectoryPanel({ plate, trajectory }) {
  const getTrajectoryStats = () => {
    if (!trajectory || !trajectory.trajectory || !trajectory.trajectory.features[0]) {
      return {};
    }
    const feature = trajectory.trajectory.features[0];
    return {
      cameras: feature.properties?.camera_sequence || [],
      points: feature.geometry?.coordinates?.length || 0,
    };
  };

  const stats = getTrajectoryStats();

  return (
    <div className="panel">
      <div className="panel-title">Trajectory Details: {plate}</div>
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.5rem' }}>
        <div>
          <h4 style={{ fontSize: '0.875rem', fontWeight: '600', textTransform: 'uppercase', marginBottom: '0.5rem' }}>
            Camera Sequence
          </h4>
          <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
            {stats.cameras && stats.cameras.length > 0 ? (
              stats.cameras.map((camera, idx) => (
                <span
                  key={idx}
                  style={{
                    backgroundColor: '#e0e7ff',
                    color: '#3730a3',
                    padding: '0.25rem 0.75rem',
                    borderRadius: '20px',
                    fontSize: '0.875rem',
                  }}
                >
                  {camera}
                </span>
              ))
            ) : (
              <span style={{ color: '#6b7280' }}>No camera data</span>
            )}
          </div>
        </div>
        <div>
          <h4 style={{ fontSize: '0.875rem', fontWeight: '600', textTransform: 'uppercase', marginBottom: '0.5rem' }}>
            Route Points
          </h4>
          <p style={{ fontSize: '1.5rem', fontWeight: '700', color: 'var(--primary-color)' }}>
            {stats.points}
          </p>
        </div>
      </div>
      <p style={{ marginTop: '1rem', fontSize: '0.875rem', color: '#6b7280' }}>
        This trajectory shows the detected route of vehicle {plate} across connected CCTV cameras.
      </p>
    </div>
  );
}

export default TrajectoryPanel;
