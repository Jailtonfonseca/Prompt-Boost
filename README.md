# Prompt-Boost

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![License](https://img.shields.io/badge/license-GPL--3.0-green)
![Python](https://img.shields.io/badge/python-3.9+-yellow)
![React](https://img.shields.io/badge/react-19.x-orange)

**Prompt-Boost** é uma ferramenta web full-stack para otimização de prompts para LLMs. Insira um prompt bruto e receba uma versão melhorada, mais clara e eficaz.

![Demo](docs/demo.gif)

## Funcionalidades

- ✨ **Otimização de Prompts**: Melhora prompts usando GPT-4o
- 📊 **Diff Visual**: Compare lado a lado o prompt original vs melhorado
- 🌐 **Galeria Pública**: Compartilhe e descubra prompts da comunidade
- 🔒 **Seguro**: API Key nunca sai do seu navegador
- 📱 **Responsivo**: Interface moderna e adaptável

## Stack Tecnológica

### Backend
- **FastAPI** - Framework web assíncrono
- **OpenAI SDK** - Integração com GPT-4o
- **SQLite** - Banco de dados local
- **Pydantic** - Validação de dados

### Frontend
- **React 19** - Biblioteca de UI
- **React Router** - Navegação SPA
- **diff-match-patch** - Renderização de diffs

## Instalação

### Pré-requisitos

- Python 3.9+
- Node.js 18+
- Chave de API OpenAI (opcional para uso local)

### Clone o Repositório

```bash
git clone https://github.com/Jailtonfonseca/Prompt-Boost.git
cd Prompt-Boost
```

### Backend

```bash
cd backend

# Crie um ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
.\venv\Scripts\activate   # Windows

# Instale as dependências
pip install -r requirements.txt

# Configure as variáveis de ambiente
cp .env.example .env
# Edite .env e adicione sua OPENAI_API_KEY

# Inicie o servidor
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend

```bash
cd frontend

# Instale as dependências
npm install

# Inicie o servidor de desenvolvimento
npm start
```

O frontend estará disponível em `http://localhost:3000` e se conectará ao backend em `http://localhost:8000`.

## Variáveis de Ambiente

### Backend (`backend/.env`)

| Variável | Descrição | Obrigatório |
|----------|-----------|-------------|
| `OPENAI_API_KEY` | Chave da API OpenAI | Sim (para uso local) |
| `CORS_ORIGINS` | Origins permitidos para CORS (separados por vírgula) | Não |
| `DATABASE_URL` | Caminho do banco SQLite | Não |

### Frontend

O frontend não requer configuração de variáveis de ambiente para uso básico.

## Uso

1. **Otimizar um Prompt**: Insira seu prompt no campo de texto e clique em "Melhorar"
2. **Ver o Diff**: Analise as alterações feitas pelo GPT-4o
3. **Compartilhar**: Salve o par de prompts para compartilhar
4. **Galeria**: Navegue pelos prompts públicos da comunidade

## API Endpoints

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| `GET` | `/` | Status da API |
| `POST` | `/api/improve-prompt` | Melhora um prompt |
| `POST` | `/api/prompts` | Salva um par de prompts |
| `GET` | `/api/prompts/{id}` | Recupera um prompt pelo ID |
| `POST` | `/api/prompts/{id}/publish` | Publica um prompt na galeria |
| `GET` | `/api/gallery` | Lista todos os prompts públicos |

### Documentação Interativa

Acesse `http://localhost:8000/docs` para a documentação Swagger UI.

## Desenvolvimento

### Executar com Docker

```bash
# Backend apenas
docker build -t prompt-boost-backend ./backend
docker run -p 8000:8000 --env-file backend/.env prompt-boost-backend

# Ou use docker-compose (se disponível)
docker-compose up
```

### Executar Testes

```bash
# Backend
cd backend
pytest

# Frontend
cd frontend
npm test
```

## Estrutura do Projeto

```
Prompt-Boost/
├── backend/
│   ├── main.py           # API FastAPI
│   ├── database.py       # Operações SQLite
│   ├── requirements.txt  # Dependências Python
│   └── .env.example      # Template de configuração
├── frontend/
│   ├── src/
│   │   ├── api.js        # Cliente da API
│   │   ├── App.js        # Componente principal
│   │   ├── MainPage.js   # Página principal
│   │   ├── GalleryPage.js # Galeria de prompts
│   │   └── DiffDisplay.js # Componente de diff
│   ├── public/
│   └── package.json
├── docs/                 # Documentação adicional
├── .gitignore
├── LICENSE
└── README.md
```

## Contribuição

Contribuições são bem-vindas! Por favor, leia [CONTRIBUTING.md](CONTRIBUTING.md) para detalhes.

1. Fork o repositório
2. Crie uma branch (`git checkout -b feature/nova-funcionalidade`)
3. Commit suas mudanças (`git commit -m 'Add nova funcionalidade'`)
4. Push para a branch (`git push origin feature/nova-funcionalidade`)
5. Abra um Pull Request

## Changelog

Veja [CHANGELOG.md](CHANGELOG.md) para o histórico de versões.

## Licença

Este projeto está sob a licença GPL-3.0. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

## Créditos

Desenvolvido por [Jailton Fonseca](https://github.com/Jailtonfonseca).

## Troubleshooting

### Erro de CORS

Se você receber erros de CORS, certifique-se de que o backend está rodando e o frontend está configurado para usar a URL correta da API.

### API Key Inválida

Verifique se sua chave da API OpenAI está correta e tem créditos disponíveis.

---

⭐ Star este projeto se foi útil!
