import api from './axios';

export const clearData = async () => {
  const response = await api.post('/settings/clear-data');
  return response.data;
};

export const uploadData = async (file) => {
  const formData = new FormData();
  formData.append('file', file);
  
  const response = await api.post('/settings/upload-data', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  return response.data;
};

export const retrainModels = async () => {
  const response = await api.post('/settings/retrain-models');
  return response.data;
};
