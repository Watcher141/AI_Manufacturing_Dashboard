import client from './client';

export const getInventoryItems = async (category = null) => {
  const response = await client.get('/api/inventory', {
    params: category ? { category } : {},
  });
  return response.data;
};

export const getInventoryOverview = async () => {
  const response = await client.get('/api/inventory/overview');
  return response.data;
};

export const getItemForecast = async (id, horizon = 30) => {
  const response = await client.get(`/api/inventory/${id}/forecast`, {
    params: { horizon },
  });
  return response.data;
};

export const getForecastSummary = async () => {
  const response = await client.get('/api/inventory/forecast/summary');
  return response.data;
};

export const getReorderAlerts = async () => {
  const response = await client.get('/api/inventory/reorder-alerts');
  return response.data;
};

export const restockItem = async (id, quantity) => {
  const response = await client.post(`/api/inventory/${id}/restock`, null, {
    params: { quantity },
  });
  return response.data;
};
