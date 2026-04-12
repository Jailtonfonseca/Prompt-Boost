# Prompt-Boost

[![Version](https://img.shields.io/badge/version-2.0.1-blue)](https://github.com/Jailtonfonseca/Prompt-Boost/releases)
[![License](https://img.shields.io/badge/license-GPL--3.0-green)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.11+-yellow)](https://www.python.org/)
[![React](https://https://img.shields.io/badge/react-19.x-orange)](https://react.dev/)
[![Docker](https://img.shields.io/badge/docker-24.x-2496ed)](https://www.docker.com/)

**Prompt-Boost** é uma ferramenta web full-stack para otimização de prompts para LLMs. Insira um prompt bruto e receba uma versão melhorada, mais clara e eficaz usando técnicas avançadas de pensamento recursivo.

> **Nota**: A versão 2.0.1 usa SQLite (não requer PostgreSQL/Redis) e inclui compatibility layer para frontends v1.x.

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
- **SQLite + aiosqlite** - Banco de dados local (async)
- **Pydantic** - Validação de dados
- **SQLAlchemy 2.0** - ORM async

### Frontend
- **React 19** - Biblioteca de UI moderna
- **React Router** - Navegação SPA
- **diff-match-patch** - Renderização de diffs

## Instalação

### Clone o Repositório

```bash
git clone https://github.com/Jailtonfonseca/Prompt-Boost.git
cd Prompt-Boost
```

### Configuração Docker (Recomendado)

```bash
# Iniciar todos os serviços (backend + frontend)
docker compose up -d

# Verificar logs
docker compose logs -f

# Parar serviços
docker compose down
```

Os serviços estarán disponíveis em:
- **Frontend**: http://localhost:3000
- **Backend**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

### Variáveis de Configuração

| Variável | Descrição | Padrão |
|----------|----------|--------|
| CORS_ORIGINS | Origins permitidos (formato JSON array) | ["http://localhost:3000"] |
| DATABASE_URL | URL do banco (sqlite+aiosqlite ou postgresql+asyncpg) | sqlite+aiosqlite |
| OPENAI_API_KEY | Chave API OpenAI | - |
| DEFAULT_PROVIDER | Provedor padrão | openai |
| DEFAULT_MODEL | Modelo padrão | gpt-4o |

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
│   ├── src/
│   │   ├── main.py              # API FastAPI (src/main.py)
│   │   ├── config.py           # Configurações
│   │   ├── api/                # Routers API
│   │   │   ├── recursion.py    # Recursion endpoints (v2)
│   │   │   ├── websocket.py    # WebSocket endpoints
│   │   │   └── compatibility.py # API v1 compatibility
│   │   ├── providers.py        # Abstração de provedores
│   │   ├── engines/            # Técnicas de recursão
│   │   ├── models/             # Modelos SQLAlchemy
│   │   └── requirements.txt    # Dependências Python
│   ├── .env                    # Configuração (criar a partir do .env.example)
│   ├── Dockerfile              # Container backend
│   └── docs/                   # Documentação técnica
├── frontend/
│   ├── src/
│   │   ├── App.js              # Componente raiz
│   │   ├── MainPage.js        # Página principal
│   │   ├── SettingsPage.js    # Página de configurações
│   │   ├── GalleryPage.js     # Galeria
│   │   ├── DiffDisplay.js     # Componente de diff
│   │   ├── api.js             # Cliente API
│   │   └── reportWebVitals.js # Métricas de performance
│   ├── public/
│   ├── package.json
│   └── Dockerfile             # Container frontend
├── docs/                      # Documentação geral
├── docker-compose.yml         # Configuração Docker
├── CHANGELOG.md              # Histórico de versões
└── README.md                 # Este arquivo
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

### Erro "error parsing value for field CORS_ORIGINS"
```bash
# O formato deve ser JSON array, não lista separada por vírgula
# ERRADO: CORS_ORIGINS=http://localhost:3000,http://localhost:8000
# CORRETO: CORS_ORIGINS=["http://localhost:3000","http://localhost:8000"]
```

### Erro "The loaded 'pysqlite' is not async"
```bash
# Use o driver aiosqlite para SQLite async
# DATABASE_URL=sqlite+aiosqlite:///./prompt_boost.db
# Não use: sqlite:/// (sync) ou pysqlite
```

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
docker compose logs backend

# Rebuild
docker compose build --no-cache
docker compose up -d
```

### Frontend 502 Bad Gateway
```bash
# Verificar se o backend está rodando
docker compose ps
docker compose logs backend
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

### v2.0.1 (2026-04-12)
- ✅ Backend com SQLite + aiosqlite (não requer PostgreSQL)
- ✅ API Compatibility Layer v1 para frontends legacy
- ✅ Correção de erros CORS e driver async
- ✅ Troubleshooting atualizado

### v2.0.0
- ✅ Sistema de recursão com 7 técnicas LLM
- ✅ Multi-provider (OpenAI, Anthropic, Gemini, Groq)
- ✅ WebSocket streaming
- ✅ Prometheus metrics

## Licença

Este projeto está sob a licença GPL-3.0. Veja [LICENSE](LICENSE) para detalhes.

## Créditos

Desenvolvido por [Jailton Fonseca](https://github.com/Jailtonfonseca).

---

⭐ Star este projeto se foi útil!