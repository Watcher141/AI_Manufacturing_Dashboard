import client from './client';

export const getDashboardOverview = async () => {
  const response = await client.get('/api/dashboard/overview');
  return response.data;
};

export const getOEEDetails = async () => {
  const response = await client.get('/api/analytics/oee');
  return response.data;
};
