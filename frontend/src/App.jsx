import React, { useState } from 'react';
import DocumentUpload from './components/DocumentUpload';
import DocumentList from './components/DocumentList';
import ChatInterface from './components/ChatInterface';

function App() {
  const [refreshTrigger, setRefreshTrigger] = useState(0);
  const [selectedDocId, setSelectedDocId] = useState('');

  const handleUploadSuccess = () => {
    setRefreshTrigger(prev => prev + 1);
  };

  return (
    <div className="min-h-screen bg-gray-100 font-sans">
      <header className="bg-blue-800 text-white p-4 shadow-md">
        <div className="container mx-auto max-w-7xl flex items-center">
          <h1 className="text-2xl font-bold tracking-tight">CourseMate AI</h1>
          <span className="ml-4 text-blue-200 text-sm hidden md:inline">Strict Document-Grounded RAG</span>
        </div>
      </header>
      
      <main className="container mx-auto max-w-7xl p-4 md:p-6 mt-4">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          
          <div className="lg:col-span-4 flex flex-col gap-6">
            <DocumentUpload onUploadSuccess={handleUploadSuccess} />
            <DocumentList 
              refreshTrigger={refreshTrigger} 
              selectedDocId={selectedDocId}
              onDocumentSelect={setSelectedDocId}
            />
          </div>

          <div className="lg:col-span-8">
            <ChatInterface selectedDocId={selectedDocId} />
          </div>

        </div>
      </main>
    </div>
  );
}

export default App;
