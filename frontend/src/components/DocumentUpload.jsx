import React, { useState } from 'react';
import { uploadDocument, previewDocument } from '../services/api';
import ChunkPreview from './ChunkPreview';

const DocumentUpload = ({ onUploadSuccess }) => {
  const [file, setFile] = useState(null);
  const [chunkSize, setChunkSize] = useState(1000);
  const [chunkOverlap, setChunkOverlap] = useState(150);
  const [loading, setLoading] = useState(false);
  const [previewLoading, setPreviewLoading] = useState(false);
  const [previewData, setPreviewData] = useState(null);
  const [error, setError] = useState('');

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
      setError('');
    }
  };

  const handlePreview = async () => {
    if (!file) {
      setError('Please select a file first.');
      return;
    }
    if (chunkOverlap >= chunkSize) {
      setError('Chunk overlap must be less than chunk size.');
      return;
    }

    setPreviewLoading(true);
    setError('');
    
    try {
      const response = await previewDocument(file, chunkSize, chunkOverlap);
      setPreviewData(response.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to generate preview.');
    } finally {
      setPreviewLoading(false);
    }
  };

  const handleUpload = async () => {
    if (!file) {
      setError('Please select a file first.');
      return;
    }
    if (chunkOverlap >= chunkSize) {
      setError('Chunk overlap must be less than chunk size.');
      return;
    }

    setLoading(true);
    setError('');
    
    try {
      await uploadDocument(file, chunkSize, chunkOverlap);
      setFile(null);
      if (document.getElementById('file-upload')) {
        document.getElementById('file-upload').value = '';
      }
      if (onUploadSuccess) onUploadSuccess();
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to upload document.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-white p-6 rounded-lg shadow-md border border-gray-200">
      <h2 className="text-xl font-bold mb-4">Upload PDF</h2>
      
      {error && (
        <div className="mb-4 p-3 bg-red-100 text-red-700 rounded text-sm">
          {error}
        </div>
      )}

      <div className="mb-4">
        <label className="block text-sm font-medium text-gray-700 mb-1">Select PDF</label>
        <input 
          id="file-upload"
          type="file" 
          accept="application/pdf"
          onChange={handleFileChange}
          className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
        />
      </div>

      <div className="grid grid-cols-2 gap-4 mb-6">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Chunk Size</label>
          <input 
            type="number" 
            value={chunkSize}
            onChange={(e) => setChunkSize(Number(e.target.value))}
            min="300"
            max="3000"
            className="w-full border-gray-300 rounded-md shadow-sm border p-2 focus:ring-blue-500 focus:border-blue-500"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Chunk Overlap</label>
          <input 
            type="number" 
            value={chunkOverlap}
            onChange={(e) => setChunkOverlap(Number(e.target.value))}
            min="0"
            max="500"
            className="w-full border-gray-300 rounded-md shadow-sm border p-2 focus:ring-blue-500 focus:border-blue-500"
          />
        </div>
      </div>

      <div className="flex gap-3">
        <button
          onClick={handlePreview}
          disabled={!file || previewLoading || loading}
          className="flex-1 bg-gray-100 text-gray-800 py-2 px-4 rounded font-medium hover:bg-gray-200 disabled:opacity-50"
        >
          {previewLoading ? 'Loading...' : 'Preview Chunks'}
        </button>
        <button
          onClick={handleUpload}
          disabled={!file || loading || previewLoading}
          className="flex-1 bg-blue-600 text-white py-2 px-4 rounded font-medium hover:bg-blue-700 disabled:opacity-50"
        >
          {loading ? 'Indexing...' : 'Upload & Index'}
        </button>
      </div>

      {previewData && (
        <ChunkPreview 
          previewData={previewData} 
          onClose={() => setPreviewData(null)} 
        />
      )}
    </div>
  );
};

export default DocumentUpload;
