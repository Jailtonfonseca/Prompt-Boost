import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import './App.css';
import './GalleryPage.css';

const GalleryPage = () => {
  const [prompts, setPrompts] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchGallery = async () => {
      setIsLoading(true);
      try {
        const response = await fetch('http://localhost:8000/api/gallery');
        if (!response.ok) {
          const errorData = await response.json();
          throw new Error(errorData.detail || 'Failed to fetch gallery.');
        }
        const data = await response.json();
        setPrompts(data.prompts);
      } catch (err) {
        setError(err.message);
      } finally {
        setIsLoading(false);
      }
    };

    fetchGallery();
  }, []);

  return (
    <div className="App">
      <header className="App-header">
        <h1>Public Prompt Gallery</h1>
        <p>Explore prompts shared by the community.</p>
        <nav>
          <Link to="/">Home</Link>
        </nav>
      </header>

      {isLoading && <h1>Loading gallery...</h1>}
      {error && <div className="error-message">{error}</div>}

      <div className="gallery-grid">
        {prompts.map(prompt => (
          <div key={prompt.id} className="gallery-item">
            <h3>Original Prompt</h3>
            <p className="prompt-text">{prompt.original_prompt}</p>
            <Link to={`/prompt/${prompt.id}`}>
              <button>View Details</button>
            </Link>
          </div>
        ))}
      </div>
    </div>
  );
};

export default GalleryPage;
