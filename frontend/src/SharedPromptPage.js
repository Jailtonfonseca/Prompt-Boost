import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import DiffDisplay from './DiffDisplay';
import './App.css'; // Reuse some styles

const SharedPromptPage = () => {
  const { promptId } = useParams();
  const [promptData, setPromptData] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchPrompt = async () => {
      setIsLoading(true);
      try {
        const response = await fetch(`http://localhost:8000/api/prompts/${promptId}`);
        if (!response.ok) {
          const errorData = await response.json();
          throw new Error(errorData.detail || 'Prompt not found.');
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
    return <div className="App"><h1>Loading Shared Prompt...</h1></div>;
  }

  if (error) {
    return <div className="App"><div className="error-message">{error}</div></div>;
  }

  if (!promptData) {
    return null;
  }

  return (
    <div className="App">
      <header className="App-header">
        <h1>Shared Prompt</h1>
      </header>

      <main className="main-content">
        <div className="prompt-container">
          <h2>Original Prompt</h2>
          <textarea
            value={promptData.original_prompt}
            readOnly
          />
        </div>
        <div className="prompt-container">
          <h2>Improved Prompt (Visual Diff)</h2>
          <DiffDisplay
            text1={promptData.original_prompt}
            text2={promptData.improved_prompt}
          />
        </div>
      </main>

      <div className="button-container">
        <Link to="/">
          <button>Create Your Own Prompt</button>
        </Link>
      </div>
    </div>
  );
};

export default SharedPromptPage;
