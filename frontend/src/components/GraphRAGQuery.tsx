import React, { useState, useEffect } from 'react';
import { apiService } from '../utils/api';

interface GraphRAGInfo {
  available: boolean;
  initialized: boolean;
  graph_info: {
    nodes: number;
    edges: number;
    density?: number;
  };
}

interface GraphRAGResponse {
  response: string;
  traversal_path: number[];
  relevant_content: string[];
  query: string;
}

interface GraphRAGQueryProps {
  notes: string[];
}

const GraphRAGQuery: React.FC<GraphRAGQueryProps> = ({ notes }) => {
  const [query, setQuery] = useState('');
  const [response, setResponse] = useState<GraphRAGResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [graphInfo, setGraphInfo] = useState<GraphRAGInfo | null>(null);
  const [processing, setProcessing] = useState(false);

  useEffect(() => {
    fetchGraphInfo();
  }, []);

  const fetchGraphInfo = async () => {
    try {
      const info = await apiService.getGraphRAGInfo();
      setGraphInfo(info);
    } catch (err) {
      console.error('Failed to fetch GraphRAG info:', err);
    }
  };

  const handleQuery = async () => {
    if (!query.trim()) {
      setError('Please enter a query');
      return;
    }

    setLoading(true);
    setError(null);
    setResponse(null);

    try {
      const result = await apiService.queryGraphRAG(query);
      setResponse(result);
    } catch (err: any) {
      setError(err.message || 'Failed to query GraphRAG');
    } finally {
      setLoading(false);
    }
  };

  const handleProcessDocuments = async () => {
    setProcessing(true);
    setError(null);
    try {
      await apiService.processGraphRAGDocuments(notes);
      await fetchGraphInfo();
      alert('Documents processed successfully!');
    } catch (err: any) {
      setError(err.message || 'Failed to process documents');
    } finally {
      setProcessing(false);
    }
  };

  if (!graphInfo?.available) {
    return (
      <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
        <h3 className="text-lg font-semibold text-yellow-800 mb-2">
          GraphRAG Not Available
        </h3>
        <p className="text-yellow-700">
          The GraphRAG integration is not available. Please check your dependencies and configuration.
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Always show Process Documents button */}
      <div className="flex items-center gap-4">
        <button
          onClick={handleProcessDocuments}
          disabled={processing || notes.length === 0}
          className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 disabled:opacity-50"
        >
          {processing ? 'Processing...' : 'Process Documents'}
        </button>
        <span className="text-sm text-gray-500">{notes.length} notes in memory</span>
      </div>

      {/* GraphRAG Status */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <h3 className="text-lg font-semibold text-blue-800 mb-2">
          GraphRAG System Status
        </h3>
        <div className="grid grid-cols-3 gap-4 text-sm">
          <div>
            <span className="font-medium">Status:</span>
            <span className={`ml-2 px-2 py-1 rounded text-xs ${
              graphInfo.initialized 
                ? 'bg-green-100 text-green-800' 
                : 'bg-red-100 text-red-800'
            }`}>
              {graphInfo.initialized ? 'Initialized' : 'Not Initialized'}
            </span>
          </div>
          <div>
            <span className="font-medium">Nodes:</span>
            <span className="ml-2">{graphInfo.graph_info.nodes}</span>
          </div>
          <div>
            <span className="font-medium">Edges:</span>
            <span className="ml-2">{graphInfo.graph_info.edges}</span>
          </div>
        </div>
      </div>

      {/* Query Interface */}
      <div className="bg-white border border-gray-200 rounded-lg p-6">
        <h3 className="text-lg font-semibold text-gray-800 mb-4">
          GraphRAG Query
        </h3>
        
        <div className="space-y-4">
          <div>
            <label htmlFor="query" className="block text-sm font-medium text-gray-700 mb-2">
              Enter your query:
            </label>
            <textarea
              id="query"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Ask a question about your notes..."
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              rows={3}
            />
          </div>
          
          <button
            onClick={handleQuery}
            disabled={loading || !graphInfo.initialized}
            className="bg-blue-600 text-white px-6 py-2 rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? 'Querying...' : 'Query GraphRAG'}
          </button>
        </div>

        {error && (
          <div className="mt-4 bg-red-50 border border-red-200 rounded-md p-3">
            <p className="text-red-800 text-sm">{error}</p>
          </div>
        )}
      </div>

      {/* Response Display */}
      {response && (
        <div className="bg-white border border-gray-200 rounded-lg p-6">
          <h3 className="text-lg font-semibold text-gray-800 mb-4">
            GraphRAG Response
          </h3>
          
          <div className="space-y-4">
            {/* Query */}
            <div>
              <h4 className="font-medium text-gray-700 mb-2">Query:</h4>
              <p className="text-gray-900 bg-gray-50 p-3 rounded">{response.query}</p>
            </div>

            {/* Response */}
            <div>
              <h4 className="font-medium text-gray-700 mb-2">Response:</h4>
              <div className="bg-blue-50 p-4 rounded-md">
                <p className="text-gray-900 whitespace-pre-wrap">{response.response}</p>
              </div>
            </div>

            {/* Traversal Path */}
            <div>
              <h4 className="font-medium text-gray-700 mb-2">Traversal Path:</h4>
              <div className="bg-green-50 p-3 rounded-md">
                <p className="text-sm text-gray-700">
                  Nodes visited: {response.traversal_path.join(' → ')}
                </p>
                <p className="text-xs text-gray-500 mt-1">
                  Total nodes: {response.traversal_path.length}
                </p>
              </div>
            </div>

            {/* Relevant Content */}
            <div>
              <h4 className="font-medium text-gray-700 mb-2">Relevant Content:</h4>
              <div className="space-y-2">
                {response.relevant_content.map((content, index) => (
                  <div key={index} className="bg-yellow-50 p-3 rounded-md">
                    <p className="text-sm text-gray-700">
                      <span className="font-medium">Chunk {index + 1}:</span>
                    </p>
                    <p className="text-gray-900 text-sm mt-1">
                      {content.length > 200 ? `${content.substring(0, 200)}...` : content}
                    </p>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default GraphRAGQuery; 