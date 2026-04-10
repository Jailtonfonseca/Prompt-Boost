import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { getConfig, updateConfig, testProvider, getProviders } from './api';
import './SettingsPage.css';

const DEFAULT_SYSTEM_PROMPT = `You are an expert prompt engineer. Your task is to refine user prompts to be more clear, 
focused, and effective for Large Language Models. 

Guidelines for improvement:
- Make the prompt more specific and detailed
- Add necessary context and constraints
- Improve clarity and remove ambiguity
- Add structure when helpful (bullet points, numbered lists)
- Preserve the original intent and key elements

Respond ONLY with the improved prompt, no explanations.`;

function SettingsPage() {
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [isTestingMain, setIsTestingMain] = useState(false);
  const [isTestingCritique, setIsTestingCritique] = useState(false);
  const [notification, setNotification] = useState('');
  
  const [providers, setProviders] = useState({});
  
  const [mainProvider, setMainProvider] = useState({
    provider_type: 'openai',
    model: 'gpt-4o',
    api_key: '',
    base_url: ''
  });
  
  const [critiqueProvider, setCritiqueProvider] = useState({
    provider_type: 'same',
    model: '',
    api_key: '',
    base_url: ''
  });
  
  const [recursion, setRecursion] = useState({
    technique: 'none',
    iterations: 3,
    show_iterations: true
  });
  
  const [systemPrompt, setSystemPrompt] = useState(DEFAULT_SYSTEM_PROMPT);
  const [showApiKey, setShowApiKey] = useState(false);
  const [showCritiqueApiKey, setShowCritiqueApiKey] = useState(false);
  const [testResultMain, setTestResultMain] = useState(null);
  const [testResultCritique, setTestResultCritique] = useState(null);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    setIsLoading(true);
    try {
      const [configData, providersData] = await Promise.all([
        getConfig(),
        getProviders()
      ]);
      setProviders(providersData);
      
      if (configData.provider_main) {
        setMainProvider(configData.provider_main);
      }
      
      if (configData.provider_critique) {
        setCritiqueProvider({
          ...configData.provider_critique,
          provider_type: 'custom'
        });
      } else {
        setCritiqueProvider({ ...critiqueProvider, provider_type: 'same' });
      }
      
      setRecursion({
        technique: configData.recursion_technique || 'none',
        iterations: configData.recursion_iterations || 3,
        show_iterations: configData.recursion_show_iterations !== false
      });
      
      setSystemPrompt(configData.system_prompt || DEFAULT_SYSTEM_PROMPT);
      
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

  const handleMainProviderChange = (field, value) => {
    setMainProvider(prev => ({ ...prev, [field]: value }));
    if (field === 'provider_type') {
      const providerModels = providers[value]?.models || [];
      if (providerModels.length > 0) {
        setMainProvider(prev => ({ ...prev, model: providerModels[0], api_key: '', base_url: '' }));
      }
    }
    setTestResultMain(null);
  };

  const handleCritiqueProviderChange = (field, value) => {
    setCritiqueProvider(prev => ({ ...prev, [field]: value }));
    if (field === 'provider_type') {
      if (value === 'same') {
        setCritiqueProvider(prev => ({ ...prev, api_key: '', model: '', base_url: '' }));
      } else if (value === 'custom') {
        setCritiqueProvider(prev => ({ ...prev, provider_type: 'openai', model: 'gpt-4o' }));
      }
    }
    setTestResultCritique(null);
  };

  const handleTestMain = async () => {
    if (!mainProvider.api_key) {
      showNotification('Digite uma API key para testar', 'error');
      return;
    }
    setIsTestingMain(true);
    setTestResultMain(null);
    try {
      const result = await testProvider(mainProvider);
      setTestResultMain(result);
      if (result.success) {
        showNotification('Conexão bem-sucedida!', 'success');
      }
    } catch (err) {
      setTestResultMain({ success: false, message: err.message });
      showNotification('Erro ao testar conexão', 'error');
    } finally {
      setIsTestingMain(false);
    }
  };

  const handleTestCritique = async () => {
    if (!critiqueProvider.api_key) {
      showNotification('Digite uma API key para testar', 'error');
      return;
    }
    setIsTestingCritique(true);
    setTestResultCritique(null);
    try {
      const result = await testProvider(critiqueProvider);
      setTestResultCritique(result);
      if (result.success) {
        showNotification('Conexão bem-sucedida!', 'success');
      }
    } catch (err) {
      setTestResultCritique({ success: false, message: err.message });
      showNotification('Erro ao testar conexão', 'error');
    } finally {
      setIsTestingCritique(false);
    }
  };

  const handleSave = async () => {
    setIsSaving(true);
    try {
      const configUpdate = {
        provider_main: mainProvider,
        provider_critique: critiqueProvider.provider_type === 'custom' ? {
          provider_type: critiqueProvider.provider_type,
          model: critiqueProvider.model,
          api_key: critiqueProvider.api_key,
          base_url: critiqueProvider.base_url
        } : null,
        recursion_technique: recursion.technique,
        recursion_iterations: recursion.iterations,
        recursion_show_iterations: recursion.show_iterations,
        system_prompt: systemPrompt
      };
      
      await updateConfig(configUpdate);
      showNotification('Configurações salvas com sucesso!', 'success');
    } catch (err) {
      showNotification('Erro ao salvar: ' + err.message, 'error');
    } finally {
      setIsSaving(false);
    }
  };

  const handleResetSystemPrompt = () => {
    setSystemPrompt(DEFAULT_SYSTEM_PROMPT);
    showNotification('System prompt restaurado para o padrão', 'success');
  };

  const getAvailableModels = (providerType) => {
    return providers[providerType]?.models || [];
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
        <p>Configure provedores de IA e técnicas de pensamento recursivo</p>
        <nav>
          <Link to="/">← Voltar ao Início</Link>
        </nav>
      </header>

      <main className="settings-container">
        <div className="settings-section">
          <h2>🤖 Provedor Principal</h2>
          <p className="section-description">
            Provedor usado para otimizar os prompts
          </p>
          
          <div className="input-group">
            <label>Provedor</label>
            <select
              value={mainProvider.provider_type}
              onChange={(e) => handleMainProviderChange('provider_type', e.target.value)}
            >
              {Object.entries(providers).map(([key, value]) => (
                <option key={key} value={key}>{value.name}</option>
              ))}
            </select>
          </div>
          
          <div className="input-group">
            <label>Modelo</label>
            <select
              value={mainProvider.model}
              onChange={(e) => handleMainProviderChange('model', e.target.value)}
            >
              {getAvailableModels(mainProvider.provider_type).map(model => (
                <option key={model} value={model}>{model}</option>
              ))}
            </select>
          </div>
          
          <div className="input-group">
            <label>API Key</label>
            <div className="input-with-actions">
              <input
                type={showApiKey ? "text" : "password"}
                value={mainProvider.api_key}
                onChange={(e) => handleMainProviderChange('api_key', e.target.value)}
                placeholder="Cole sua API key aqui..."
              />
              <button
                type="button"
                className="icon-btn"
                onClick={() => setShowApiKey(!showApiKey)}
                title={showApiKey ? "Ocultar" : "Mostrar"}
              >
                {showApiKey ? '👁️' : '👁️‍🗨️'}
              </button>
            </div>
          </div>
          
          {mainProvider.provider_type === 'openrouter' && (
            <div className="input-group">
              <label>Custom Base URL (opcional)</label>
              <input
                type="text"
                value={mainProvider.base_url}
                onChange={(e) => handleMainProviderChange('base_url', e.target.value)}
                placeholder="https://openrouter.ai/api/v1"
              />
            </div>
          )}
          
          <button
            type="button"
            className="test-btn"
            onClick={handleTestMain}
            disabled={isTestingMain || !mainProvider.api_key}
          >
            {isTestingMain ? '⏳ Testando...' : '🧪 Testar Conexão'}
          </button>
          
          {testResultMain && (
            <div className={`test-result ${testResultMain.success ? 'success' : 'error'}`}>
              {testResultMain.success ? '✅' : '❌'} {testResultMain.message}
            </div>
          )}
        </div>

        <div className="settings-section">
          <h2>🔄 Técnicas de Pensamento Recursivo</h2>
          <p className="section-description">
            Selecione uma técnica para melhorar a qualidade das otimizações
          </p>
          
          <div className="input-group">
            <label>Técnica</label>
            <select
              value={recursion.technique}
              onChange={(e) => setRecursion(prev => ({ ...prev, technique: e.target.value }))}
            >
              <option value="none">Nenhuma (otimização básica)</option>
              <option value="self-refine">Self-Refine (gerar → criticar → refinar)</option>
              <option value="toT">Tree of Thoughts (múltiplas versões)</option>
            </select>
          </div>
          
          {recursion.technique !== 'none' && (
            <>
              <div className="input-group">
                <label>Número de Iterações: {recursion.iterations}</label>
                <input
                  type="range"
                  min="2"
                  max="5"
                  value={recursion.iterations}
                  onChange={(e) => setRecursion(prev => ({ ...prev, iterations: parseInt(e.target.value) }))}
                />
                <div className="range-labels">
                  <span>2 (mais rápido)</span>
                  <span>5 (mais completo)</span>
                </div>
              </div>
              
              <div className="input-group checkbox-group">
                <label>
                  <input
                    type="checkbox"
                    checked={recursion.show_iterations}
                    onChange={(e) => setRecursion(prev => ({ ...prev, show_iterations: e.target.checked }))}
                  />
                  Mostrar iterações ao usuário
                </label>
                <p className="field-hint">Exibe cada etapa do processo de otimização</p>
              </div>
            </>
          )}
          
          {recursion.technique === 'self-refine' && (
            <div className="technique-info">
              <h4>📖 Como funciona o Self-Refine:</h4>
              <ol>
                <li>Gera uma versão melhorada do prompt</li>
                <li>Critica essa versão para identificar melhorias</li>
                <li>Refina com base na crítica</li>
                <li>Repete pelo número de iterações</li>
              </ol>
            </div>
          )}
          
          {recursion.technique === 'toT' && (
            <div className="technique-info">
              <h4>📖 Como funciona o Tree of Thoughts:</h4>
              <ol>
                <li>Gera múltiplas versões diferentes do prompt</li>
                <li>Avalia cada versão com pontuação</li>
                <li>Seleciona a melhor versão</li>
                <li>Retorna a versão com maior pontuação</li>
              </ol>
            </div>
          )}
        </div>

        <div className="settings-section">
          <h2>🔍 Provedor de Crítica (Self-Refine)</h2>
          <p className="section-description">
            Opcional - use provedor diferente para criticAR as otimizações
          </p>
          
          <div className="input-group">
            <label>Usar</label>
            <select
              value={critiqueProvider.provider_type}
              onChange={(e) => handleCritiqueProviderChange('provider_type', e.target.value)}
            >
              <option value="same">Mesmo do provedor principal</option>
              <option value="custom">Provedor personalizado</option>
            </select>
          </div>
          
          {critiqueProvider.provider_type === 'custom' && (
            <>
              <div className="input-group">
                <label>Provedor</label>
                <select
                  value={critiqueProvider.provider_type === 'custom' ? 'openai' : critiqueProvider.provider_type}
                  onChange={(e) => setCritiqueProvider(prev => ({ ...prev, provider_type: e.target.value }))}
                >
                  {Object.entries(providers).map(([key, value]) => (
                    <option key={key} value={key}>{value.name}</option>
                  ))}
                </select>
              </div>
              
              <div className="input-group">
                <label>Modelo</label>
                <select
                  value={critiqueProvider.model}
                  onChange={(e) => setCritiqueProvider(prev => ({ ...prev, model: e.target.value }))}
                >
                  {getAvailableModels('openai').map(model => (
                    <option key={model} value={model}>{model}</option>
                  ))}
                </select>
              </div>
              
              <div className="input-group">
                <label>API Key</label>
                <div className="input-with-actions">
                  <input
                    type={showCritiqueApiKey ? "text" : "password"}
                    value={critiqueProvider.api_key}
                    onChange={(e) => setCritiqueProvider(prev => ({ ...prev, api_key: e.target.value }))}
                    placeholder="Cole a API key..."
                  />
                  <button
                    type="button"
                    className="icon-btn"
                    onClick={() => setShowCritiqueApiKey(!showCritiqueApiKey)}
                  >
                    {showCritiqueApiKey ? '👁️' : '👁️‍🗨️'}
                  </button>
                </div>
              </div>
              
              <button
                type="button"
                className="test-btn"
                onClick={handleTestCritique}
                disabled={isTestingCritique || !critiqueProvider.api_key}
              >
                {isTestingCritique ? '⏳ Testando...' : '🧪 Testar Conexão'}
              </button>
              
              {testResultCritique && (
                <div className={`test-result ${testResultCritique.success ? 'success' : 'error'}`}>
                  {testResultCritique.success ? '✅' : '❌'} {testResultCritique.message}
                </div>
              )}
            </>
          )}
        </div>

        <div className="settings-section">
          <h2>📝 System Prompt</h2>
          <p className="section-description">
            Instruções enviadas ao modelo antes de otimizar o prompt
          </p>
          
          <div className="input-group">
            <textarea
              value={systemPrompt}
              onChange={(e) => setSystemPrompt(e.target.value)}
              rows={8}
              placeholder="Instruções do sistema..."
            />
          </div>
          
          <button
            type="button"
            className="reset-btn"
            onClick={handleResetSystemPrompt}
          >
            🔄 Restaurar Padrão
          </button>
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
            <li><strong>Self-Refine:</strong> Melhora iterativamente com feedback interno</li>
            <li><strong>ToT:</strong> Gera múltiplas versões e escolhe a melhor</li>
            <li>Mais iterações = melhor qualidade, mas mais tempo e custo</li>
            <li>Use provedor de crítica diferente para diversidade de perspectivas</li>
          </ul>
        </div>
      </main>
    </div>
  );
}

export default SettingsPage;