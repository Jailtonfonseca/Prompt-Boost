import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import DiffDisplay from './DiffDisplay';
import './App.css'; // Keep using the same CSS for simplicity

function MainPage() {
  const [originalPrompt, setOriginalPrompt] = useState('');
  const [improvedPrompt, setImprovedPrompt] = useState('');
  const [apiKey, setApiKey] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [shareableLink, setShareableLink] = useState('');
  const [sharedId, setSharedId] = useState('');
  const [isPublished, setIsPublished] = useState(false);

  // Load API key from local storage on component mount
  useEffect(() => {
    const storedApiKey = localStorage.getItem('openai_api_key');
    if (storedApiKey) {
      setApiKey(storedApiKey);
    }
  }, []);

  const handleApiKeyChange = (e) => {
    const newApiKey = e.target.value;
    setApiKey(newApiKey);
    localStorage.setItem('openai_api_key', newApiKey);
  };

  const handleImprovePrompt = async () => {
    if (!apiKey) {
      setError('Please enter your OpenAI API key.');
      return;
    }
    if (!originalPrompt) {
      setError('Please enter a prompt to improve.');
      return;
    }

    setIsLoading(true);
    setError('');
    setImprovedPrompt('');
    setShareableLink('');
    setSharedId('');
    setIsPublished(false);

    try {
      const response = await fetch('http://localhost:8000/api/improve-prompt', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ prompt: originalPrompt, apiKey: apiKey }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'An unknown error occurred.');
      }

      const data = await response.json();
      setImprovedPrompt(data.improved_prompt);
    } catch (err) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  const handleShare = async () => {
    if (!originalPrompt || !improvedPrompt) {
      setError('You must have an original and an improved prompt to share.');
      return;
    }
    setIsLoading(true);
    setError('');
    try {
      const response = await fetch('http://localhost:8000/api/prompts', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          original_prompt: originalPrompt,
          improved_prompt: improvedPrompt,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to create share link.');
      }

      const data = await response.json();
      const shareId = data.share_id;
      const link = `${window.location.origin}/prompt/${shareId}`;
      setShareableLink(link);
      setSharedId(shareId);
    } catch (err) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  const handlePublish = async () => {
    if (!sharedId) return;
    setIsLoading(true);
    setError('');
    try {
      const response = await fetch(`http://localhost:8000/api/prompts/${sharedId}/publish`, {
        method: 'POST',
      });
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to publish.');
      }
      setIsPublished(true);
    } catch (err) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>Prompt Enhancer</h1>
        <p>Refine your prompts for better AI results.</p>
        <nav>
          <Link to="/gallery">View Gallery</Link>
        </nav>
      </header>

      <div className="api-key-section">
        <label htmlFor="api-key">OpenAI API Key:</label>
        <input
          id="api-key"
          type="password"
          value={apiKey}
          onChange={handleApiKeyChange}
          placeholder="Enter your OpenAI API Key here"
        />
      </div>

      {error && <div className="error-message">{error}</div>}

      <main className="main-content">
        <div className="prompt-container">
          <h2>Original Prompt</h2>
          <textarea
            value={originalPrompt}
            onChange={(e) => setOriginalPrompt(e.target.value)}
            placeholder="Enter your prompt here..."
          />
        </div>
        <div className="prompt-container">
          <h2>Improved Prompt (Visual Diff)</h2>
          <DiffDisplay text1={originalPrompt} text2={improvedPrompt} />
        </div>
      </main>

      <div className="button-container">
        <button onClick={handleImprovePrompt} disabled={isLoading || !originalPrompt}>
          {isLoading ? 'Improving...' : 'Improve Prompt'}
        </button>
        {improvedPrompt && (
          <button onClick={handleShare} disabled={isLoading}>
            Share
          </button>
        )}
      </div>

      {shareableLink && (
        <div className="shareable-link-section">
          <h3>Share this link:</h3>
          <input type="text" readOnly value={shareableLink} />
          <button onClick={() => navigator.clipboard.writeText(shareableLink)}>
            Copy
          </button>
          {!isPublished ? (
            <button onClick={handlePublish} disabled={isLoading}>
              Publish to Gallery
            </button>
          ) : (
            <span>Published!</span>
          )}
        </div>
      )}
    </div>
  );
}

export default MainPage;
