import React, { useState, useEffect } from 'react';

const API_BASE = "http://127.0.0.1:8000";

function App() {
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState(null);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState('hybrid'); // 'hybrid', 'dense', 'sparse'

  const handleSearch = async (e) => {
    if (e) e.preventDefault();
    if (!query.trim()) return;

    setLoading(true);
    setError(null);
    try {
      const response = await fetch(`${API_BASE}/search`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query, top_k: 6 })
      });
      if (!response.ok) throw new Error(`Backend Error: ${response.statusText}`);
      const data = await response.json();
      setResults(data);
    } catch (error) {
      console.error("Search failed:", error);
      setError("Failed to connect to search engine. Please make sure the backend is running.");
    } finally {
      setLoading(false);
    }
  };

  const getActiveResults = () => {
    if (!results) return [];
    return results[activeTab] || [];
  };

  const getScoreLabel = (doc) => {
    if (activeTab === 'dense') return `Score: ${doc.dense_score.toFixed(4)}`;
    if (activeTab === 'sparse') return `BM25: ${doc.sparse_score.toFixed(2)}`;
    return `RRF: ${doc.rrf_score.toFixed(4)}`;
  };

  return (
    <div id="root">
      <header className="header">
        <div className="logo-container">
          <div className="logo-icon">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
              <circle cx="11" cy="11" r="8"></circle>
              <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
            </svg>
          </div>
          <h1>HybridSearch AI</h1>
        </div>
        <p className="subtitle">
          Experience the next generation of information retrieval. Combining semantic understanding with precision keyword matching.
        </p>
      </header>

      <div className="search-container">
        <form onSubmit={handleSearch} className="search-input-wrapper">
          <input 
            type="text" 
            placeholder="Search for concepts, code, or data..." 
            value={query}
            onChange={(e) => setQuery(e.target.value)}
          />
          <button type="submit" className="search-btn" disabled={loading}>
            {loading ? 'Searching...' : 'Search'}
          </button>
        </form>

        <div className="tabs">
          <div 
            className={`tab ${activeTab === 'hybrid' ? 'active' : ''}`}
            onClick={() => setActiveTab('hybrid')}
          >
            🌟 Hybrid (Best)
          </div>
          <div 
            className={`tab ${activeTab === 'dense' ? 'active' : ''}`}
            onClick={() => setActiveTab('dense')}
          >
            🤖 Semantic
          </div>
          <div 
            className={`tab ${activeTab === 'sparse' ? 'active' : ''}`}
            onClick={() => setActiveTab('sparse')}
          >
            🎯 Keyword
          </div>
        </div>
      </div>

      {loading && (
        <div className="loading">
          <div className="dot"></div>
          <div className="dot"></div>
          <div className="dot"></div>
        </div>
      )}

      {error && (
        <div style={{ marginTop: '2rem', color: '#ff4444', textAlign: 'center', background: 'rgba(255,0,0,0.1)', padding: '1rem', borderRadius: '12px' }}>
          {error}
        </div>
      )}

      {!loading && !error && results && getActiveResults().length > 0 && (
        <div className="results-grid">
          {getActiveResults().map((doc, index) => (
            <div className="card" key={doc.id || index} style={{ animationDelay: `${index * 0.1}s` }}>
              <div className="card-tag">{doc.category}</div>
              <h3 className="card-title">{doc.title}</h3>
              <p className="card-text">{doc.text}</p>
              <div className="card-footer">
                <span className="score-badge">{getScoreLabel(doc)}</span>
                <button className="search-btn" style={{ padding: '0.4rem 1rem', fontSize: '0.8rem' }}>View Detail</button>
              </div>
            </div>
          ))}
        </div>
      )}

      {!loading && !error && results && getActiveResults().length === 0 && (
        <div style={{ marginTop: '4rem', color: 'var(--text-muted)', textAlign: 'center' }}>
          <p>No results found for "<strong>{query}</strong>". Try a different query!</p>
        </div>
      )}

      {!loading && !error && !results && query === '' && (
        <div style={{ marginTop: '4rem', color: 'var(--text-muted)', textAlign: 'center' }}>
          <p>Try searching for <strong>"machine learning"</strong>, <strong>"agri-tech"</strong>, or <strong>"python"</strong></p>
        </div>
      )}
    </div>
  );
}

export default App;
