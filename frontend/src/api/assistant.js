import client from './client';

export const getAIStatus = async () => {
  const response = await client.get('/api/ai/status');
  return response.data;
};

export const sendChatMessage = async (message, context = null) => {
  const response = await client.post('/api/ai/chat', { message, context });
  return response.data;
};

export const getEquipmentAnalysis = async (id) => {
  const response = await client.post(`/api/ai/analyze/${id}`);
  return response.data;
};

export const getAutoInsights = async () => {
  const response = await client.get('/api/ai/insights');
  return response.data;
};
