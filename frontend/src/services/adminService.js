import apiClient from './apiClient';
export default {
  stats: () => apiClient.get('/admin/dashboard'),
  brands: () => apiClient.get('/admin/brands'),
  users: () => apiClient.get('/admin/users'),
  settings: () => apiClient.get('/admin/settings'),
  reports: () => apiClient.get('/admin/reports'),
};
