import React, { useEffect, useState } from 'react';
import { getDocuments, deleteDocument } from '../services/api';
import { Trash2 } from 'lucide-react';

const DocumentList = ({ refreshTrigger, onDocumentSelect, selectedDocId }) => {
  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const fetchDocuments = async () => {
    try {
      setLoading(true);
      const res = await getDocuments();
      setDocuments(res.data);
      setError('');
    } catch (err) {
      setError('Failed to fetch indexed documents.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDocuments();
  }, [refreshTrigger]);

  const handleDelete = async (docId, e) => {
    e.stopPropagation();
    if (!window.confirm("Are you sure you want to delete this document?")) return;
    
    try {
      await deleteDocument(docId);
      if (selectedDocId === docId && onDocumentSelect) {
        onDocumentSelect(''); // clear selection if deleted
      }
      fetchDocuments();
    } catch (err) {
      setError('Failed to delete document.');
    }
  };

  return (
    <div className="bg-white p-6 rounded-lg shadow-md border border-gray-200 mt-6">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-xl font-bold">Indexed Documents</h2>
        <button 
          onClick={fetchDocuments}
          className="text-sm text-blue-600 hover:underline"
        >
          Refresh
        </button>
      </div>

      {error && <p className="text-red-600 text-sm mb-3">{error}</p>}

      {loading ? (
        <p className="text-sm text-gray-500">Loading documents...</p>
      ) : documents.length === 0 ? (
        <p className="text-sm text-gray-500">No documents indexed yet.</p>
      ) : (
        <ul className="space-y-2">
          <li 
            className={`p-3 rounded border cursor-pointer flex justify-between items-center transition-colors
              ${selectedDocId === '' ? 'bg-blue-50 border-blue-300' : 'bg-white hover:bg-gray-50 border-gray-200'}
            `}
            onClick={() => onDocumentSelect('')}
          >
            <div>
              <span className="font-semibold text-gray-800">All Documents</span>
              <p className="text-xs text-gray-500">Search across all indexed materials</p>
            </div>
          </li>
          {documents.map((doc) => (
            <li 
              key={doc.document_id}
              className={`p-3 rounded border flex justify-between items-center cursor-pointer transition-colors
                ${selectedDocId === doc.document_id ? 'bg-blue-50 border-blue-300' : 'bg-white hover:bg-gray-50 border-gray-200'}
              `}
              onClick={() => onDocumentSelect(doc.document_id)}
            >
              <div>
                <span className="font-medium text-gray-800 break-all">{doc.filename}</span>
                <div className="text-xs text-gray-500 mt-1 flex gap-3">
                  <span>Chunks: {doc.total_chunks}</span>
                  <span>Size: {doc.chunk_size || 'N/A'}</span>
                  <span>Overlap: {doc.chunk_overlap || 'N/A'}</span>
                </div>
              </div>
              <button 
                onClick={(e) => handleDelete(doc.document_id, e)}
                className="text-red-500 hover:text-red-700 p-2 rounded hover:bg-red-50"
                title="Delete document"
              >
                <Trash2 size={18} />
              </button>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
};

export default DocumentList;
