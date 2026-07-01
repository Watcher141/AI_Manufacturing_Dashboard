import client from './client';

export const getEquipmentList = async (filters = {}) => {
  const response = await client.get('/api/equipment', { params: filters });
  return response.data;
};

export const getEquipmentDetail = async (id) => {
  const response = await client.get(`/api/equipment/${id}`);
  return response.data;
};

export const getSensorHistory = async (id, hours = 24) => {
  const response = await client.get(`/api/equipment/${id}/sensors`, { params: { hours } });
  return response.data;
};

export const getSensorTrends = async (equipmentId = null, hours = 24) => {
  const params = { hours };
  if (equipmentId) params.equipment_id = equipmentId;
  const response = await client.get('/api/analytics/sensor-trends', { params });
  return response.data;
};

export const addSensorReading = async (id, data) => {
  const response = await client.post(`/api/equipment/${id}/readings`, data);
  return response.data;
};

export const getEquipmentTypes = async () => {
  const response = await client.get('/api/equipment/types');
  return response.data;
};
