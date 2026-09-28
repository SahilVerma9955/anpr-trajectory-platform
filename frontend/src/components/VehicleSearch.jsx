import React, { useState } from 'react';

function VehicleSearch({ onSearch, loading }) {
  const [plate, setPlate] = useState('');

  const handleSearch = (e) => {
    e.preventDefault();
    if (plate.trim()) {
      onSearch(plate.toUpperCase());
    }
  };

  return (
    <div className="panel">
      <div className="panel-title">Vehicle Search</div>
      <form onSubmit={handleSearch}>
        <div className="search-box">
          <input
            type="text"
            placeholder="Enter plate: DL01AB1234"
            value={plate}
            onChange={(e) => setPlate(e.target.value.toUpperCase())}
            disabled={loading}
          />
          <button type="submit" disabled={loading}>
            {loading ? 'Searching...' : 'Search'}
          </button>
        </div>
      </form>
      <p style={{ fontSize: '0.875rem', color: '#6b7280', marginTop: '0.5rem' }}>
        Enter a normalized Indian license plate to search for vehicle history and trajectory.
      </p>
    </div>
  );
}

export default VehicleSearch;
