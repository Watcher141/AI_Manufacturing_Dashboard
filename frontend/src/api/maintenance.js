import client from './client';

export const getPredictions = async () => {
  const response = await client.get('/api/maintenance/predictions');
  return response.data;
};

export const getEquipmentPrediction = async (id) => {
  const response = await client.get(`/api/maintenance/predictions/${id}`);
  return response.data;
};

export const getMaintenanceSchedule = async () => {
  const response = await client.get('/api/maintenance/schedule');
  return response.data;
};

export const getMaintenanceLogs = async (equipmentId = null) => {
  const response = await client.get('/api/maintenance/logs', {
    params: equipmentId ? { equipment_id: equipmentId } : {},
  });
  return response.data;
};
