# Aprimorador de Prompts (Prompt Enhancer)

Esta é uma aplicação web full-stack projetada para ajudar usuários a melhorar seus prompts de IA. Possui um frontend em React e um backend em FastAPI.

## Funcionalidades

*   **Aprimoramento com IA**: Envie um prompt e receba uma versão aprimorada por IA para melhorar sua clareza, foco e eficácia.
*   **Use Sua Própria Chave**: A aplicação utiliza a sua chave de API pessoal da OpenAI para todas as interações com a IA.
*   **Comparação Visual (Diff)**: Veja as alterações exatas entre o seu prompt original e a versão melhorada com uma comparação lado a lado, clara e codificada por cores.
*   **Links Compartilháveis**: Crie um link único e compartilhável para qualquer par de prompt/melhoria para enviar a outras pessoas.
*   **Galeria Pública**: Publique seu trabalho em uma galeria pública e explore prompts compartilhados pela comunidade.

## Tecnologias Utilizadas

*   **Backend**: Python, FastAPI
*   **Frontend**: React.js
*   **Banco de Dados**: SQLite

## Como Executar

### Backend
1.  Navegue até o diretório `backend`.
2.  Crie um ambiente virtual Python: `python -m venv venv`
3.  Ative o ambiente: `source venv/bin/activate`
4.  Instale as dependências: `pip install -r requirements.txt`
5.  Execute o servidor: `uvicorn main:app --reload`
    *   O backend estará disponível em `http://localhost:8000`.

### Frontend
1.  Navegue até o diretório `frontend`.
2.  Instale as dependências: `npm install`
3.  Inicie o servidor de desenvolvimento: `npm start`
    *   O frontend estará disponível em `http://localhost:3000`.
