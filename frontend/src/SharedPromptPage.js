import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import DiffDisplay from './DiffDisplay';
import './App.css';

const SharedPromptPage = () => {
  const { promptId } = useParams();
  const [promptData, setPromptData] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchPrompt = async () => {
      setIsLoading(true);
      try {
        const response = await fetch(`${process.env.REACT_APP_API_URL || 'http://localhost:8000/api'}/prompts/${promptId}`);
        if (!response.ok) {
          const errorData = await response.json();
          throw new Error(errorData.detail || 'Prompt não encontrado.');
        }
        const data = await response.json();
        setPromptData(data);
      } catch (err) {
        setError(err.message);
      } finally {
        setIsLoading(false);
      }
    };

    fetchPrompt();
  }, [promptId]);

  if (isLoading) {
    return (
      <div className="App">
        <div className="loading-spinner">
          <div className="spinner"></div>
          <span>Carregando prompt...</span>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="App">
        <div className="error-message">{error}</div>
        <Link to="/">
          <button>Voltar ao Início</button>
        </Link>
      </div>
    );
  }

  if (!promptData) {
    return null;
  }

  return (
    <div className="App">
      <header className="App-header">
        <h1>Prompt Compartilhado</h1>
        <nav>
          <Link to="/">← Voltar ao Início</Link>
          <Link to="/settings">⚙️ Configurações</Link>
        </nav>
      </header>

      <main className="main-content">
        <div className="prompt-container">
          <h2>Prompt Original</h2>
          <textarea
            value={promptData.original_prompt}
            readOnly
          />
        </div>
        <div className="prompt-container">
          <h2>Prompt Otimizado</h2>
          <DiffDisplay
            text1={promptData.original_prompt}
            text2={promptData.improved_prompt}
          />
        </div>
      </main>

      <div className="button-container">
        <Link to="/">
          <button>Criar Seu Próprio Prompt</button>
        </Link>
      </div>
    </div>
  );
};

export default SharedPromptPage;