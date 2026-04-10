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
    }, 3500);
  };

  const handleImprovePrompt = async () => {
    if (!originalPrompt.trim()) {
      setError('Digite um prompt para melhorar.');
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
      showNotification('Prompt otimizado com sucesso!');
    } catch (err) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  const handleShare = async () => {
    if (!originalPrompt || !improvedPrompt) {
      setError('Você precisa ter um prompt original e um melhorado para compartilhar.');
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
      showNotification('Link criado com sucesso!');
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
      showNotification('Prompt publicado na galeria!');
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
      {notification && <div className="notification">{notification}</div>}
      
      <header className="App-header">
        <h1>Prompt-Boost</h1>
        <p>Otimize seus prompts e obtenha melhores resultados da IA</p>
        <nav>
          <Link to="/gallery">Ver Galeria</Link>
        </nav>
      </header>

      {error && <div className="error-message">{error}</div>}

      <main className="main-content">
        <div className="prompt-container">
          <h2>Prompt Original</h2>
          <textarea
            value={originalPrompt}
            onChange={(e) => setOriginalPrompt(e.target.value)}
            placeholder="Digite seu prompt aqui...&#10;&#10;Exemplo: Escreva um email profissional recusando uma proposta de emprego de forma educada."
          />
        </div>
        
        <div className="prompt-container">
          <div className="prompt-header">
            <h2>Prompt Otimizado</h2>
            {improvedPrompt && (
              <button className="copy-button" onClick={() => handleCopy(improvedPrompt, 'Copiado!')}>
                📋 Copiar
              </button>
            )}
          </div>
          <DiffDisplay text1={originalPrompt} text2={improvedPrompt} isLoading={isLoading} />
        </div>
      </main>

      <div className="button-container">
        <button onClick={handleImprovePrompt} disabled={isLoading || !originalPrompt.trim()}>
          {isLoading ? '⏳ Otimizando...' : '✨ Otimizar Prompt'}
        </button>
        
        {improvedPrompt && (
          <>
            <button onClick={() => handleCopy(improvedPrompt, 'Prompt otimizado copiado!')}>
              📋 Copiar Resultado
            </button>
            <button onClick={handleShare} disabled={isLoading} className="share-button">
              🔗 Compartilhar
            </button>
          </>
        )}
      </div>

      {shareableLink && (
        <div className="shareable-link-section">
          <h3>Compartilhe este link:</h3>
          <input type="text" readOnly value={shareableLink} />
          <button onClick={() => handleCopy(shareableLink, 'Link copiado!')}>
            📋 Copiar
          </button>
          {!isPublished ? (
            <button onClick={handlePublish} disabled={isLoading}>
              🌍 Publicar na Galeria
            </button>
          ) : (
            <span>Publicado!</span>
          )}
        </div>
      )}
    </div>
  );
}

export default MainPage;