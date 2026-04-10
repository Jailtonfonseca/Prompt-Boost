import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import './App.css';
import './GalleryPage.css';

const GalleryPage = () => {
  const [prompts, setPrompts] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    const fetchGallery = async () => {
      setIsLoading(true);
      try {
        const response = await fetch(`${process.env.REACT_APP_API_URL || 'http://localhost:8000/api'}/gallery`);
        if (!response.ok) {
          const errorData = await response.json();
          throw new Error(errorData.detail || 'Falha ao carregar galeria.');
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

  const handleCardClick = (promptId) => {
    navigate(`/prompt/${promptId}`);
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>Galeria de Prompts</h1>
        <p>Explore prompts compartilhados pela comunidade</p>
        <nav>
          <Link to="/">← Voltar ao Início</Link>
          <Link to="/settings">⚙️ Configurações</Link>
        </nav>
      </header>

      {error && <div className="error-message">{error}</div>}

      {isLoading ? (
        <div className="gallery-container">
          <div className="loading-spinner">
            <div className="spinner"></div>
            <span>Carregando galeria...</span>
          </div>
        </div>
      ) : prompts.length === 0 ? (
        <div className="gallery-container">
          <div className="empty-state">
            <span>📭</span>
            <h2>Nenhum prompt publicado ainda</h2>
            <p>Seja o primeiro a compartilhar um prompt!</p>
            <Link to="/">
              <button>Criar Prompt</button>
            </Link>
          </div>
        </div>
      ) : (
        <div className="gallery-grid">
          {prompts.map(prompt => (
            <div 
              key={prompt.id} 
              className="gallery-card"
              onClick={() => handleCardClick(prompt.id)}
            >
              <h3>Prompt Original</h3>
              <p>{prompt.original_prompt}</p>
              <div className="date">
                🎯 Ver detalhes →
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default GalleryPage;