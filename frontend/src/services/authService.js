import apiClient from './apiClient';
export default {
  login: data => {
    const form = new URLSearchParams();
    form.append('username', data.email);
    form.append('password', data.password);
    return apiClient.post('/auth/login', form, { headers:{'Content-Type':'application/x-www-form-urlencoded'} });
  }
};
