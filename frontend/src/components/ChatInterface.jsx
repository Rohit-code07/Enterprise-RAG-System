import React, { useState, useRef, useEffect } from 'react';
import { chat } from '../services/api';

import ReactMarkdown from 'react-markdown';

const ChatInterface = ({ selectedDocId }) => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const endOfMessagesRef = useRef(null);

  const scrollToBottom = () => {
    endOfMessagesRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async (e) => {
    e.preventDefault();
    if (!input.trim() || loading) return;

    const userMessage = { role: 'user', content: input };
    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setLoading(true);

    try {
      const response = await chat(userMessage.content, selectedDocId || null);
      
      const assistantMessage = { 
        role: 'assistant', 
        content: response.data.answer,
        sources: response.data.sources
      };
      
      setMessages((prev) => [...prev, assistantMessage]);
    } catch (error) {
      const errorMessage = error.response?.data?.detail || "Sorry, I encountered an error while processing your request.";
      setMessages((prev) => [...prev, { 
        role: 'assistant', 
        content: errorMessage,
        isError: true 
      }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-md border border-gray-200 flex flex-col h-[800px]">
      <div className="p-4 border-b bg-gray-50 flex justify-between items-center rounded-t-lg">
        <h2 className="text-xl font-bold">Document Chat</h2>
        {selectedDocId && (
          <span className="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded-full font-semibold">
            Filtered by Document
          </span>
        )}
      </div>
      
      <div className="flex-1 p-4 overflow-y-auto bg-gray-50 flex flex-col gap-4">
        {messages.length === 0 && (
          <div className="text-center text-gray-500 mt-10">
            <p>Ask a question about your uploaded documents.</p>
            <p className="text-sm mt-2">Example: "What are the key takeaways?"</p>
          </div>
        )}
        
        {messages.map((msg, idx) => (
          <div key={idx} className={`flex flex-col ${msg.role === 'user' ? 'items-end' : 'items-start'}`}>
            <div 
              className={`max-w-[85%] p-4 rounded-lg ${
                msg.role === 'user' 
                  ? 'bg-blue-600 text-white rounded-tr-none' 
                  : msg.isError 
                    ? 'bg-red-100 text-red-800 border border-red-200 rounded-tl-none'
                    : 'bg-white border border-gray-200 text-gray-800 rounded-tl-none shadow-sm'
              }`}
            >
              <div className={`text-sm md:text-base leading-relaxed ${msg.role === 'assistant' && !msg.isError ? 'prose prose-sm max-w-none' : 'whitespace-pre-wrap'}`}>
                {msg.role === 'assistant' && !msg.isError ? (
                  <ReactMarkdown>{msg.content}</ReactMarkdown>
                ) : (
                  msg.content
                )}
              </div>
            </div>
            
            {msg.sources && msg.sources.length > 0 && (
              <div className="mt-2 max-w-[85%]">
                <p className="text-xs font-semibold text-gray-500 mb-1">Sources:</p>
                <div className="flex flex-col gap-2">
                  {msg.sources.map((src, sIdx) => (
                    <div key={sIdx} className="bg-white border border-gray-200 p-2 rounded text-xs text-gray-600 shadow-sm">
                      <div className="font-semibold text-gray-800 mb-1 flex justify-between">
                        <span>{src.source}</span>
                        <span className="bg-gray-100 px-1.5 py-0.5 rounded">Page {src.page}</span>
                      </div>
                      <p className="italic bg-gray-50 p-1.5 rounded line-clamp-3">"...{src.excerpt}..."</p>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        ))}
        {loading && (
          <div className="flex items-start">
            <div className="bg-white border border-gray-200 text-gray-500 rounded-lg p-3 rounded-tl-none shadow-sm flex gap-1">
              <span className="animate-bounce">●</span>
              <span className="animate-bounce" style={{animationDelay: '0.2s'}}>●</span>
              <span className="animate-bounce" style={{animationDelay: '0.4s'}}>●</span>
            </div>
          </div>
        )}
        <div ref={endOfMessagesRef} />
      </div>

      <div className="p-4 border-t bg-white rounded-b-lg">
        <form onSubmit={handleSend} className="flex gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask a question..."
            disabled={loading}
            className="flex-1 border border-gray-300 rounded-md p-3 focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <button 
            type="submit"
            disabled={loading || !input.trim()}
            className="bg-blue-600 text-white px-6 py-3 rounded-md font-medium hover:bg-blue-700 disabled:opacity-50 transition-colors"
          >
            Send
          </button>
        </form>
      </div>
    </div>
  );
};

export default ChatInterface;
