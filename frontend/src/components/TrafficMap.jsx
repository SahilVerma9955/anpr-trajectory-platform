import React, { useEffect, useState } from 'react';
import { MapContainer, TileLayer, Marker, Popup, Polyline } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';

function TrafficMap({ trajectory, selectedPlate }) {
  const [mapCenter, setMapCenter] = useState([28.6139, 77.2090]); // Delhi
  const [routePoints, setRoutePoints] = useState([]);

  useEffect(() => {
    if (trajectory && trajectory.trajectory && trajectory.trajectory.features) {
      const feature = trajectory.trajectory.features[0];
      if (feature && feature.geometry && feature.geometry.coordinates) {
        const coords = feature.geometry.coordinates;
        setRoutePoints(coords.map((c) => [c[1], c[0]]));
        if (coords.length > 0) {
          setMapCenter([coords[0][1], coords[0][0]]);
        }
      }
    }
  }, [trajectory]);

  const defaultIcon = L.icon({
    iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon.png',
    iconSize: [25, 41],
    iconAnchor: [12, 41],
    popupAnchor: [1, -34],
  });

  return (
    <div className="panel">
      <div className="panel-title">
        {selectedPlate ? `Route - ${selectedPlate}` : 'Traffic Map'}
      </div>
      <MapContainer center={mapCenter} zoom={11} style={{ height: '400px', borderRadius: '6px' }}>
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        {routePoints.length > 0 && <Polyline positions={routePoints} color="red" weight={3} opacity={0.7} />}
        {routePoints.map((point, idx) => (
          <Marker key={idx} position={point} icon={defaultIcon}>
            <Popup>Point {idx + 1}</Popup>
          </Marker>
        ))}
      </MapContainer>
    </div>
  );
}

export default TrafficMap;
