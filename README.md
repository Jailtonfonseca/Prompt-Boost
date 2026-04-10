# Prompt-Boost

[![Version](https://img.shields.io/badge/version-1.4.0-blue)](https://github.com/Jailtonfonseca/Prompt-Boost/releases)
[![License](https://img.shields.io/badge/license-GPL--3.0-green)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.9+-yellow)](https://www.python.org/)
[![React](https://img.shields.io/badge/react-19.x-orange)](https://react.dev/)
[![Docker](https://img.shields.io/badge/docker-24.x-2496ed)](https://www.docker.com/)

**Prompt-Boost** é uma ferramenta web full-stack para otimização de prompts para LLMs. Insira um prompt bruto e receba uma versão melhorada, mais clara e eficaz using técnicas avançadas de pensamento recursivo.

![Demo](docs/demo.gif)

## Funcionalidades

- **Multi-Provedor**: Suporte a OpenAI, Google Gemini, xAI Grok, OpenRouter e Groq
- **Técnicas Recursivas**: Self-Refine e Tree of Thoughts (ToT)
- **Iterações Configuráveis**: Determine quantas vezes o prompt deve ser refinado
- **Provedor de Crítica**: Use um modelo separado para avaliar melhorias
- **Diff Visual**: Compare lado a lado o prompt original vs melhorado
- **System Prompt Customizável**: Defina seu próprio contexto de atuação
- **Seguro**: API Keys permanecem no seu servidor
- **Responsivo**: Interface moderna e adaptável

## Stack Tecnológica

### Backend
- **FastAPI** - Framework web assíncrono de alta performance
- **OpenAI SDK** - Integração com modelos GPT
- **Google Generative AI** - Integração com Gemini
- **xAI SDK** - Integração com Grok
- **SQLite** - Banco de dados local
- **Pydantic** - Validação de dados

### Frontend
- **React 19** - Biblioteca de UI moderna
- **React Router** - Navegação SPA
- **diff-match-patch** - Renderização de diffs

## Provedores Suportados

| Provedor | Modelo Padrão | native Models |
|---------|--------------|-------------|
| **OpenAI** | gpt-4o | gpt-4o, gpt-4o-mini, gpt-4-turbo, o1-preview |
| **Google Gemini** | gemini-2.0-flash | gemini-2.0-flash, gemini-1.5-pro, gemini-1.5-flash |
| **xAI Grok** | grok-2 | grok-2, grok-2-vision-1212, grok-beta |
| **OpenRouter** | openai/gpt-4o | openai/gpt-4o, claude-3.5-sonnet, llama-3.1-405b |
| **Groq** | llama-3.1-70b-versatile | llama-3.1-70b-versatile, mixtral-8x7b-32768 |

## Técnicas Recursivas

### Self-Refine
O **Self-Refine** itera o prompt através de ciclos de geração e crítica:
1. Gera uma versão melhorada do prompt
2. Usa um modelo de crítica para avaliar
3. Refina baseado no feedback
4. Repete pelo número de iterações configurado

### Tree of Thoughts (ToT)
O **ToT** explora múltiplos caminhos de pensamento:
1. Gera várias abordagens alternativas
2. Avalia cada ramificação
3. Seleciona a melhor via
4. Repete para refinar

## Instalação

### Clone o Repositório

```bash
git clone https://github.com/Jailtonfonseca/Prompt-Boost.git
cd Prompt-Boost
```

### Configuração Docker (Recomendado)

```bash
# Iniciar todos os serviços
docker-compose up -d

# Verificar logs
docker-compose logs -f

# Parar serviços
docker-compose down
```

Os serviços estarán disponíveis em:
- **Frontend**: http://localhost:3000
- **Backend**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

### Instalação Manual

#### Pré-requisitos

- Python 3.9+
- Node.js 18+

#### Backend

```bash
cd backend

# Criar ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# .\venv\Scripts\activate   # Windows

# Instalar dependências
pip install -r requirements.txt

# Iniciar servidor
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend

```bash
cd frontend

# Instalar dependências
npm install

# Iniciar servidor
npm start
```

O frontend estará disponível em `http://localhost:3000`.

## Configuração

### Via Interface Web

1. Acesse http://localhost:3000
2. Clique no ícone de configurações (⚙️)
3. Selecione o provedorprincipal
4. Cole sua API Key
5. Clique em "Testar" para verificar
6. Save as configurações

### Adicionar Provedor de Crítica (Self-Refine)

Para usar técnicas Self-Refine com dois modelos:

1. Nas configurações, configure o **Provedor Principal**
2. Selecione "custom" em provedor de crítica
3. Configure um segundo provedor/API key
4. A técnica usará o provedor principal para gerar e o de crítica para avaliar

### Variáveis de Configuração

| Variável | Descrição | Padrão |
|----------|----------|--------|
| CORS_ORIGINS | Origins permitidos (vírgula) | http://localhost:3000 |
| RATE_LIMIT | Requisições por minuto | 30 |
| TEMPERATURE | Temperatura do modelo | 0.7 |
| MAX_TOKENS | Tokens máximos de saída | 2000 |
| RECURSION_TECHNIQUE | Técnica: none/self-refine/tot | none |
| RECURSION_ITERATIONS | Iterações (2-5) | 3 |

## Uso

### Via Interface

1. Insira seu prompt no campo de texto
2. Selecione a técnica recursiva (opcional)
3. Clique em "Melhorar"
4. Analise as alterações no diff
5. Copie o prompt mejorado

### Via API REST

```bash
# Melhora um prompt
curl -X POST http://localhost:8000/api/improve-prompt \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Write a function to add two numbers"}'

# Lista provedores disponíveis
curl http://localhost:8000/api/providers

# Testa conexão com provedor
curl -X POST http://localhost:8000/api/config/test-provider \
  -H "Content-Type: application/json" \
  -d '{"provider_type": "openai", "api_key": "sk-...", "model": "gpt-4o"}'
```

### Documentação Interativa

Acesse http://localhost:8000/docs para Swagger UI.

## API Endpoints

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/` | Status da API |
| GET | `/api/providers` | Lista provedores e modelos |
| GET | `/api/config` | Retorna configuração atual |
| POST | `/api/config` | Salva configuração |
| POST | `/api/config/test-provider` | Testa conexão com provedor |
| POST | `/api/improve-prompt` | Melhora um prompt |
| POST | `/api/prompts` | Salva um par de prompts |
| GET | `/api/prompts/{id}` | Recupera prompt pelo ID |
| POST | `/api/prompts/{id}/publish` | Publica na galeria |
| GET | `/api/gallery` | Lista prompts públicos |

## Estrutura do Projeto

```
Prompt-Boost/
├── backend/
│   ├── main.py              # API FastAPI
│   ├── providers.py          # Abstração de provedores
│   ├── recursion.py          # Técnicas Self-Refine e ToT
│   ├── database.py           # Operações SQLite
│   ├── requirements.txt     # Dependências Python
│   └── .env                 # Configuração (runtime)
├── frontend/
│   ├── src/
│   │   ├── api.js           # Cliente API
│   │   ├── App.js           # Componente raiz
│   │   ├── MainPage.js      # Página principal
│   │   ├── SettingsPage.js  # Página de configurações
│   │   ├── GalleryPage.js  # Galeria
│   │   └── DiffDisplay.js   # Componente de diff
│   ├── public/
│   └── package.json
├── docs/                    # Documentação
├── docker-compose.yml       # Configuração Docker
├── CHANGELOG.md           # Histórico de versões
└── README.md              # Este arquivo
```

## Desenvolvimento

### Executar Testes

```bash
# Backend
cd backend
pytest

# Frontend
cd frontend
npm test
```

### Builds Customizados

```bash
# Build apenas backend
docker build -t prompt-boost-backend ./backend

# Build apenas frontend
docker build -t prompt-boost-frontend ./frontend
```

## Troubleshooting

### Erro 429 (Too Many Requests)
O rate limit está configurado para 30 req/min. Aguarde ou ajuste em configurações.

### API Key Inválida
Verifique se:
- A chave está correta
- Tem créditos disponíveis
- O modelo selecionado existe

### CORS Error
Certifique-se que o backend está rodando e o frontend usa a URL correta da API.

### Container não inicia
```bash
# Verificar logs
docker-compose logs backend

# Rebuild
docker-compose build --no-cache
docker-compose up -d
```

## Contribuição

Contribuições são bem-vindas! Leia [CONTRIBUTING.md](CONTRIBUTING.md) para detalhes.

1. Fork o repositório
2. Crie uma branch (`git checkout -b feature/nova`)
3. Commit suas mudanças (`git commit -m 'Add feature'`)
4. Push para a branch (`git push origin feature/nova`)
5. Abra um Pull Request

## Changelog

Veja [CHANGELOG.md](CHANGELOG.md) para o histórico completo de versões.

## Licença

Este projeto está sob a licença GPL-3.0. Veja [LICENSE](LICENSE) para detalhes.

## Créditos

Desenvolvido por [Jailton Fonseca](https://github.com/Jailtonfonseca).

---

⭐ Star este projeto se foi útil!