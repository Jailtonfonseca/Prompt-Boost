# Prompt Enhancer

This is a full-stack web application designed to help users improve their AI prompts. It features a React frontend and a FastAPI backend.

## Features

*   **AI-Powered Enhancement**: Submit a prompt and receive an AI-powered enhancement to improve its clarity, focus, and effectiveness.
*   **Bring Your Own Key**: The application uses your personal OpenAI API key for all AI interactions.
*   **Visual Diff Comparison**: See the exact changes between your original prompt and the improved version with a clear, color-coded side-by-side comparison.
*   **Shareable Links**: Create a unique, shareable link for any prompt-improvement pair to send to others.
*   **Public Gallery**: Publish your work to a public gallery and explore prompts shared by the community.

## Tech Stack

*   **Backend**: Python, FastAPI
*   **Frontend**: React.js
*   **Database**: SQLite

## How to Run

### Backend
1.  Navigate to the `backend` directory.
2.  Create a Python virtual environment: `python -m venv venv`
3.  Activate the environment: `source venv/bin/activate`
4.  Install dependencies: `pip install -r requirements.txt`
5.  Run the server: `uvicorn main:app --reload`
    *   The backend will be available at `http://localhost:8000`.

### Frontend
1.  Navigate to the `frontend` directory.
2.  Install dependencies: `npm install`
3.  Start the development server: `npm start`
    *   The frontend will be available at `http://localhost:3000`.
