const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

const handleResponse = async (response) => {
  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(errorData.detail || 'An unknown error occurred.');
  }
  return response.json();
};

export const improvePrompt = async (prompt) => {
  const response = await fetch(`${API_BASE_URL}/improve-prompt`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ prompt }),
  });
  return handleResponse(response);
};

export const sharePrompt = async (original_prompt, improved_prompt) => {
  const response = await fetch(`${API_BASE_URL}/prompts`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ original_prompt, improved_prompt }),
  });
  return handleResponse(response);
};

export const publishPrompt = async (promptId) => {
  const response = await fetch(`${API_BASE_URL}/prompts/${promptId}/publish`, {
    method: 'POST',
  });
  // This endpoint returns a 204 No Content on success, so no JSON to parse.
  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(errorData.detail || 'Failed to publish.');
  }
  return;
};

export const getConfig = async () => {
  const response = await fetch(`${API_BASE_URL}/config`);
  return handleResponse(response);
};

export const updateConfig = async (config) => {
  const response = await fetch(`${API_BASE_URL}/config`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(config),
  });
  return handleResponse(response);
};

export const testApiKey = async (apiKey) => {
  const response = await fetch(`${API_BASE_URL}/config/test`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ api_key: apiKey }),
  });
  return handleResponse(response);
};

export const getProviders = async () => {
  const response = await fetch(`${API_BASE_URL}/providers`);
  return handleResponse(response);
};

export const testProvider = async (providerConfig) => {
  const response = await fetch(`${API_BASE_URL}/config/test-provider`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(providerConfig),
  });
  return handleResponse(response);
};
