import axios from 'axios';

class ApiClient {
  constructor(baseURL) {
    this.baseURL = baseURL;
    this.client = axios.create({
      baseURL,
      timeout: 15000,
    });
  }

  async getHealth() {
    return this.client.get('/health');
  }

  async getVideos() {
    return this.client.get('/api/videos');
  }

  async getCameras() {
    return this.client.get('/api/cameras');
  }

  async getVehicles() {
    return this.client.get('/api/vehicles');
  }

  async getVehicleByPlate(plate) {
    return this.client.get(`/api/vehicles/${plate}`);
  }

  async getVehicleDetections(plate) {
    return this.client.get(`/api/vehicles/${plate}/detections`);
  }

  async getTrajectory(plate) {
    return this.client.get(`/api/trajectories/${plate}`);
  }

  async getAnalyticsDensity() {
    return this.client.get('/api/analytics/density');
  }

  async getAnalyticsFlow() {
    return this.client.get('/api/analytics/flow');
  }

  async getAnalyticsSpeed() {
    return this.client.get('/api/analytics/speed');
  }

  async getAnalyticsCongestion() {
    return this.client.get('/api/analytics/congestion');
  }

  async getAnalyticsHeatmap() {
    return this.client.get('/api/analytics/heatmap');
  }

  async getAnalyticsODMatrix() {
    return this.client.get('/api/analytics/od-matrix');
  }

  async getAlerts() {
    return this.client.get('/api/alerts');
  }

  async addBlacklist(plate, reason) {
    return this.client.post(`/api/alerts/blacklist?plate=${plate}&reason=${reason}`);
  }

  async removeBlacklist(plate) {
    return this.client.delete(`/api/alerts/blacklist/${plate}`);
  }
}

export default ApiClient;
