import api from './client';

export const login = async (password) => {
  const response = await api.post('/api/auth/login', { password });
  return response.data;
};

export const verify = async () => {
  const response = await api.get('/api/auth/verify');
  return response.data;
};

export const logout = async () => {
  const response = await api.post('/api/auth/logout');
  return response.data;
};
