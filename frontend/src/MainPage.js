import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import DiffDisplay from './DiffDisplay';
import { improvePrompt, sharePrompt, publishPrompt } from './api';
import './App.css';

function MainPage() {
  const [originalPrompt, setOriginalPrompt] = useState('');
  const [improvedPrompt, setImprovedPrompt] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [shareableLink, setShareableLink] = useState('');
  const [sharedId, setSharedId] = useState('');
  const [isPublished, setIsPublished] = useState(false);
  const [notification, setNotification] = useState('');

  const showNotification = (message) => {
    setNotification(message);
    setTimeout(() => {
      setNotification('');
    }, 3000);
  };

  const handleImprovePrompt = async () => {
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
      const data = await improvePrompt(originalPrompt);
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
      const data = await sharePrompt(originalPrompt, improvedPrompt);
      const shareId = data.share_id;
      const link = `${window.location.origin}/prompt/${shareId}`;
      setShareableLink(link);
      setSharedId(shareId);
      showNotification('Share link created successfully!');
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
      await publishPrompt(sharedId);
      setIsPublished(true);
      showNotification('Prompt published to the gallery!');
    } catch (err) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  const handleCopy = (text, message) => {
    navigator.clipboard.writeText(text);
    showNotification(message);
  };

  return (
    <div className="App">
      {notification && <div className={`notification ${notification ? 'show' : ''}`}>{notification}</div>}
      <header className="App-header">
        <h1>Prompt Enhancer</h1>
        <p>Refine your prompts for better AI results.</p>
        <nav>
          <Link to="/gallery">View Gallery</Link>
        </nav>
      </header>

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
          <div className="prompt-header">
            <h2>Improved Prompt (Visual Diff)</h2>
            {improvedPrompt && (
              <button className="copy-button" onClick={() => handleCopy(improvedPrompt, 'Improved prompt copied!')}>
                Copy
              </button>
            )}
          </div>
          <DiffDisplay text1={originalPrompt} text2={improvedPrompt} isLoading={isLoading} />
        </div>
      </main>

      <div className="button-container">
        <button onClick={handleImprovePrompt} disabled={isLoading || !originalPrompt}>
          {isLoading ? 'Improving...' : 'Improve Prompt'}
        </button>
        {improvedPrompt && (
          <>
            <button onClick={() => handleCopy(improvedPrompt, 'Improved prompt copied!')}>
              Copy Improved Prompt
            </button>
            <button onClick={handleShare} disabled={isLoading} className="share-button">
              Share
            </button>
          </>
        )}
      </div>

      {shareableLink && (
        <div className="shareable-link-section">
          <h3>Share this link:</h3>
          <input type="text" readOnly value={shareableLink} />
          <button onClick={() => handleCopy(shareableLink, 'Link copied to clipboard!')}>
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
