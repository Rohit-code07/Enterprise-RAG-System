import axios from 'axios';

const API_URL = 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_URL,
});

export const getHealth = () => api.get('/health');

export const getDocuments = () => api.get('/documents');

export const deleteDocument = (documentId) => api.delete(`/documents/${documentId}`);

export const uploadDocument = (file, chunkSize, chunkOverlap) => {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('chunk_size', chunkSize);
  formData.append('chunk_overlap', chunkOverlap);
  
  return api.post('/documents', formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  });
};

export const previewDocument = (file, chunkSize, chunkOverlap) => {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('chunk_size', chunkSize);
  formData.append('chunk_overlap', chunkOverlap);
  
  return api.post('/documents/preview', formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  });
};

export const chat = (question, documentId = null) => {
  return api.post('/chat', {
    question,
    document_id: documentId
  });
};
