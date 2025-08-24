const API_BASE_URL = 'http://localhost:8000/api';

const handleResponse = async (response) => {
  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(errorData.detail || 'An unknown error occurred.');
  }
  return response.json();
};

export const improvePrompt = async (prompt, apiKey) => {
  const response = await fetch(`${API_BASE_URL}/improve-prompt`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ prompt, apiKey }),
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
