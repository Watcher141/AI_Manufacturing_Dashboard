import client from './client';

export const getDefects = async (filters = {}) => {
  const response = await client.get('/api/defects', { params: filters });
  return response.data;
};

export const getDefectStats = async () => {
  const response = await client.get('/api/defects/stats');
  return response.data;
};

export const triggerDefectScan = async (equipmentId = null) => {
  const response = await client.post('/api/defects/detect', null, {
    params: equipmentId ? { equipment_id: equipmentId } : {},
  });
  return response.data;
};

export const resolveDefect = async (id) => {
  const response = await client.patch(`/api/defects/${id}/resolve`);
  return response.data;
};
