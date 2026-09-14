import React from 'react';

const ChunkPreview = ({ previewData, onClose }) => {
  if (!previewData) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex justify-center items-center p-4 z-50">
      <div className="bg-white rounded-lg shadow-xl w-full max-w-4xl max-h-[90vh] flex flex-col">
        <div className="p-4 border-b flex justify-between items-center">
          <h2 className="text-xl font-semibold">Chunk Preview</h2>
          <button 
            onClick={onClose}
            className="text-gray-500 hover:text-gray-800 font-bold"
          >
            ✕
          </button>
        </div>
        
        <div className="p-4 border-b bg-gray-50">
          <p className="text-sm text-gray-700">
            Total Chunks that will be generated: <span className="font-bold">{previewData.total_chunks}</span>
          </p>
          <p className="text-xs text-gray-500 mt-1">Showing the first few chunks for verification.</p>
        </div>
        
        <div className="p-4 overflow-y-auto flex-1 space-y-4">
          {previewData.preview.map((chunk, idx) => (
            <div key={idx} className="border rounded-md p-4 bg-gray-50">
              <div className="flex justify-between items-center mb-2">
                <span className="text-xs font-semibold bg-blue-100 text-blue-800 px-2 py-1 rounded">
                  Chunk {chunk.chunk_index}
                </span>
                <span className="text-xs text-gray-500">
                  Page {chunk.page}
                </span>
              </div>
              <p className="text-sm font-mono whitespace-pre-wrap text-gray-800">
                {chunk.text}
              </p>
            </div>
          ))}
        </div>
        
        <div className="p-4 border-t flex justify-end">
          <button 
            onClick={onClose}
            className="px-4 py-2 bg-gray-200 text-gray-800 rounded hover:bg-gray-300"
          >
            Close Preview
          </button>
        </div>
      </div>
    </div>
  );
};

export default ChunkPreview;
