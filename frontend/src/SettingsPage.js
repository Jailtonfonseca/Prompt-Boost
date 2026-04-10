import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { getConfig, updateConfig, testApiKey } from './api';
import './SettingsPage.css';

function SettingsPage() {
  const [config, setConfig] = useState({
    openai_api_key: '',
    cors_origins: 'http://localhost:3000',
    rate_limit: 30,
    model: 'gpt-4o',
    temperature: 0.7,
    max_tokens: 2000
  });
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [isTesting, setIsTesting] = useState(false);
  const [showApiKey, setShowApiKey] = useState(false);
  const [notification, setNotification] = useState('');
  const [testResult, setTestResult] = useState(null);

  useEffect(() => {
    loadConfig();
  }, []);

  const loadConfig = async () => {
    setIsLoading(true);
    try {
      const data = await getConfig();
      setConfig(prev => ({
        ...prev,
        cors_origins: data.cors_origins,
        rate_limit: data.rate_limit,
        model: data.model,
        temperature: data.temperature,
        max_tokens: data.max_tokens,
        api_key_configured: data.api_key_configured
      }));
    } catch (err) {
      showNotification('Erro ao carregar configurações: ' + err.message, 'error');
    } finally {
      setIsLoading(false);
    }
  };

  const showNotification = (message, type = 'success') => {
    setNotification({ message, type });
    setTimeout(() => setNotification(''), 3500);
  };

  const handleChange = (field, value) => {
    setConfig(prev => ({ ...prev, [field]: value }));
  };

  const handleSave = async () => {
    setIsSaving(true);
    try {
      await updateConfig(config);
      showNotification('Configurações salvas com sucesso!', 'success');
    } catch (err) {
      showNotification('Erro ao salvar: ' + err.message, 'error');
    } finally {
      setIsSaving(false);
    }
  };

  const handleTestApiKey = async () => {
    if (!config.openai_api_key) {
      showNotification('Digite uma API key para testar', 'error');
      return;
    }
    setIsTesting(true);
    setTestResult(null);
    try {
      const result = await testApiKey(config.openai_api_key);
      setTestResult(result);
      if (result.success) {
        showNotification('API key válida!', 'success');
      }
    } catch (err) {
      setTestResult({ success: false, message: err.message });
      showNotification('Erro ao testar API key', 'error');
    } finally {
      setIsTesting(false);
    }
  };

  const handleClearApiKey = () => {
    setConfig(prev => ({ ...prev, openai_api_key: '' }));
    setTestResult(null);
  };

  if (isLoading) {
    return (
      <div className="App">
        <div className="loading-spinner">
          <div className="spinner"></div>
          <span>Carregando configurações...</span>
        </div>
      </div>
    );
  }

  return (
    <div className="App">
      {notification && (
        <div className={`notification ${notification.type === 'error' ? 'error' : ''}`}>
          {notification.message}
        </div>
      )}

      <header className="App-header">
        <h1>⚙️ Configurações</h1>
        <p>Gerencie as configurações do Prompt-Boost</p>
        <nav>
          <Link to="/">← Voltar ao Início</Link>
        </nav>
      </header>

      <main className="settings-container">
        <div className="settings-section">
          <h2>🔑 OpenAI API Key</h2>
          <p className="section-description">
            Cole sua chave de API da OpenAI. obtains em <a href="https://platform.openai.com/api-keys" target="_blank" rel="noopener noreferrer">platform.openai.com</a>
          </p>
          <div className="input-group">
            <div className="input-with-actions">
              <input
                type={showApiKey ? "text" : "password"}
                value={config.openai_api_key}
                onChange={(e) => handleChange('openai_api_key', e.target.value)}
                placeholder="sk-..."
              />
              <button
                type="button"
                className="icon-btn"
                onClick={() => setShowApiKey(!showApiKey)}
                title={showApiKey ? "Ocultar" : "Mostrar"}
              >
                {showApiKey ? '👁️' : '👁️‍🗨️'}
              </button>
              {config.openai_api_key && (
                <button
                  type="button"
                  className="icon-btn clear"
                  onClick={handleClearApiKey}
                  title="Limpar"
                >
                  🗑️
                </button>
              )}
            </div>
            <button
              type="button"
              className="test-btn"
              onClick={handleTestApiKey}
              disabled={isTesting || !config.openai_api_key}
            >
              {isTesting ? '⏳ Testando...' : '🧪 Testar Conexão'}
            </button>
          </div>
          {testResult && (
            <div className={`test-result ${testResult.success ? 'success' : 'error'}`}>
              {testResult.success ? '✅' : '❌'} {testResult.message}
              {testResult.model && <span className="model-info"> | Modelo: {testResult.model}</span>}
            </div>
          )}
          {config.api_key_configured && !config.openai_api_key && (
            <div className="api-configured-badge">
              ✅ API Key configurada no servidor
            </div>
          )}
        </div>

        <div className="settings-section">
          <h2>🌐 CORS Origins</h2>
          <p className="section-description">
            Origins permitidos para requisições (separados por vírgula)
          </p>
          <div className="input-group">
            <input
              type="text"
              value={config.cors_origins}
              onChange={(e) => handleChange('cors_origins', e.target.value)}
              placeholder="http://localhost:3000, http://localhost:8080"
            />
          </div>
        </div>

        <div className="settings-section">
          <h2>⚡ Rate Limit</h2>
          <p className="section-description">
            Número máximo de requisições por minuto
          </p>
          <div className="input-group">
            <input
              type="number"
              min="1"
              max="1000"
              value={config.rate_limit}
              onChange={(e) => handleChange('rate_limit', parseInt(e.target.value) || 30)}
            />
          </div>
        </div>

        <div className="settings-section">
          <h2>🤖 Modelo OpenAI</h2>
          <p className="section-description">
            Modelo usado para otimizar os prompts
          </p>
          <div className="input-group">
            <select
              value={config.model}
              onChange={(e) => handleChange('model', e.target.value)}
            >
              <option value="gpt-4o">GPT-4o (Recomendado)</option>
              <option value="gpt-4o-mini">GPT-4o Mini</option>
              <option value="gpt-4-turbo">GPT-4 Turbo</option>
              <option value="gpt-3.5-turbo">GPT-3.5 Turbo</option>
            </select>
          </div>
        </div>

        <div className="settings-section">
          <h2>🌡️ Temperature</h2>
          <p className="section-description">
            Controla a criatividade das respostas (0 = mais preciso, 1 = mais criativo)
          </p>
          <div className="input-group range-group">
            <input
              type="range"
              min="0"
              max="2"
              step="0.1"
              value={config.temperature}
              onChange={(e) => handleChange('temperature', parseFloat(e.target.value))}
            />
            <span className="range-value">{config.temperature}</span>
          </div>
          <div className="range-labels">
            <span>Mais preciso</span>
            <span>Mais criativo</span>
          </div>
        </div>

        <div className="settings-section">
          <h2>📝 Max Tokens</h2>
          <p className="section-description">
            Limite máximo de tokens na resposta
          </p>
          <div className="input-group">
            <input
              type="number"
              min="100"
              max="32000"
              value={config.max_tokens}
              onChange={(e) => handleChange('max_tokens', parseInt(e.target.value) || 2000)}
            />
          </div>
        </div>

        <div className="settings-actions">
          <button
            className="save-btn"
            onClick={handleSave}
            disabled={isSaving}
          >
            {isSaving ? '⏳ Salvando...' : '💾 Salvar Configurações'}
          </button>
        </div>

        <div className="settings-info">
          <h3>ℹ️ Informações</h3>
          <ul>
            <li>A API key é armazenada de forma segura no servidor</li>
            <li>As alterações nas configurações podem requerer reinício do container</li>
            <li>有些设置可能需要刷新页面才能生效</li>
          </ul>
        </div>
      </main>
    </div>
  );
}

export default SettingsPage;