# Interpreter-Lycosidae

Serviço backend do projeto **Lycosidae CTF**, responsável por abstrair a comunicação entre os componentes e o banco de dados **MariaDB**, utilizando **FastAPI** e **SQLAlchemy** como ORM.

O sistema expõe endpoints HTTPS que recebem requisições HTTP, interpretam as instruções e convertem em consultas padronizadas executadas diretamente no repositório de dados.

## ✨ Funcionalidades Implementadas

### 🔧 CRUD Completo

- **Usuários**: Registro, autenticação, gerenciamento de perfis
- **Competições**: Criação, gerenciamento e controle de acesso
- **Exercícios**: Cadastro e classificação por dificuldade
- **Tags**: Sistema de categorização flexível
- **Times**: Formação e gerenciamento de equipes
- **Containers**: Controle de prazos e recursos

### 🔗 Relacionamentos

- **Usuário ↔ Competição**: Participação em competições
- **Usuário ↔ Time**: Membro de equipes
- **Time ↔ Competição**: Times em competições
- **Exercício ↔ Tag**: Categorização de exercícios
- **Exercício ↔ Competição**: Exercícios por competição
- **Container ↔ Competição**: Recursos por competição

### 📊 Logs Estruturados

- **Sistema de logging centralizado** em `app/logger.py`
- **Rastreabilidade completa** de operações de banco
- **Métricas de performance** (tempo de execução)
- **Logs coloridos** para desenvolvimento
- **Formato JSON** para produção

### 📚 Documentação Automática

- **Swagger UI** disponível em `/docs`
- **ReDoc** disponível em `/redoc`
- **Schemas completos** com validação
- **Exemplos de request/response**
- **Interface interativa** para testes

---

## 🚀 Como Executar

### Pré-requisitos

- Python 3.8+
- MariaDB/MySQL
- Docker (opcional)

### Instalação

```bash
# Clone o repositório
git clone <repository-url>
cd Interpreter-Lycosidae

# Instale as dependências
pip install -r requirements.txt

# Configure as variáveis de ambiente
cp .env.example .env
# Edite o arquivo .env com suas configurações

# Execute o servidor
./uvicorn.sh
```

### Acessar a Documentação

- **Swagger UI**: <http://localhost:8000/docs>
- **ReDoc**: <http://localhost:8000/redoc>
- **API Base**: <http://localhost:8000>

---

## 📡 Endpoints da API

### 👤 Usuários

- `POST /route/register` - Registro de usuário
- `GET /route/users/{user_id}` - Buscar usuário
- `PUT /route/users/{user_id}` - Atualizar usuário
- `DELETE /route/users/{user_id}` - Deletar usuário

### 🏆 Competições

- `POST /route/competitions` - Criar competição
- `GET /route/competitions/{competition_id}` - Buscar competição
- `GET /route/competitions/invite/{invite_code}` - Buscar por código
- `PUT /route/competitions/{competition_id}` - Atualizar competição
- `DELETE /route/competitions/{competition_id}` - Deletar competição

### 💪 Exercícios

- `POST /route/exercises` - Criar exercício
- `GET /route/exercises/{exercise_id}` - Buscar exercício
- `PUT /route/exercises/{exercise_id}` - Atualizar exercício
- `DELETE /route/exercises/{exercise_id}` - Deletar exercício

### 🏷️ Tags

- `POST /route/tags` - Criar tag
- `GET /route/tags/{tag_id}` - Buscar tag
- `GET /route/tags/type/{tag_type}` - Buscar por tipo
- `PUT /route/tags/{tag_id}` - Atualizar tag
- `DELETE /route/tags/{tag_id}` - Deletar tag

### 👥 Times

- `POST /route/teams` - Criar time
- `GET /route/teams/{team_id}` - Buscar time
- `PUT /route/teams/{team_id}` - Atualizar time
- `DELETE /route/teams/{team_id}` - Deletar time

### 📦 Containers

- `POST /route/containers` - Criar container
- `GET /route/containers/{container_id}` - Buscar container
- `PUT /route/containers/{container_id}` - Atualizar container
- `DELETE /route/containers/{container_id}` - Deletar container

### 🔗 Endpoints de Relacionamentos

- `POST /route/user-competitions` - Relacionar usuário-competição
- `POST /route/user-teams` - Relacionar usuário-time
- `POST /route/team-competitions` - Relacionar time-competição
- `POST /route/exercise-tags` - Relacionar exercício-tag
- `DELETE /route/exercise-tags/{exercise_id}/{tag_id}` - Remover relação
- `POST /route/exercise-competitions` - Relacionar exercício-competição
- `POST /route/container-competitions` - Relacionar container-competição

---

## 🏗️ Arquitetura de Execução

- Orquestração feita por repositório auxiliar com script que inicializa todos os containers.
- Arquivo `.env` centralizado em outro diretório (não deve ser duplicado).
- Conexão ao banco controlada pela variável `DATABASE_URL`.

---

## 📊 Estrutura de Dados

### Tabelas Principais

| Tabela | Campos | Descrição |
|--------|--------|-----------|
| **Users** | username, email, password, phone_number | Usuários do sistema |
| **Competitions** | name, organizer, invite_code, start_date, end_date | Competições CTF |
| **Exercises** | link, name, score, difficulty | Exercícios/Desafios |
| **Tags** | type, id | Categorização de exercícios |
| **Teams** | name, competition, creator, score | Equipes participantes |
| **Containers** | id, deadline | Recursos com prazo |

### Tabelas de Relacionamento

| Tabela | Relaciona | Descrição |
|--------|-----------|-----------|
| **user_competitions** | Users ↔ Competitions | Participação em competições |
| **user_teams** | Users ↔ Teams | Membros de equipes |
| **team_competitions** | Teams ↔ Competitions | Times em competições |
| **exercise_tags** | Exercises ↔ Tags | Categorização de exercícios |
| **exercise_competitions** | Exercises ↔ Competitions | Exercícios por competição |
| **container_competitions** | Containers ↔ Competitions | Recursos por competição |

---

## 🔧 Desenvolvimento

### Estrutura do Projeto

```text
app/
├── main.py              # Aplicação principal FastAPI
├── database.py          # Configuração do banco de dados
├── models.py            # Modelos SQLAlchemy
├── schemas.py           # DTOs Pydantic
├── routers.py           # Endpoints da API
├── dbutils_mysql.py     # Funções de banco de dados
└── logger.py            # Sistema de logging estruturado
```

### Logs Estruturados

- **Desenvolvimento**: Logs coloridos no console
- **Produção**: Logs em formato JSON
- **Rastreabilidade**: IDs de transação e contexto
- **Performance**: Tempo de execução de operações
- **Erros**: Stack traces completos com contexto

### Validação de Dados

- **Pydantic schemas** para validação de entrada
- **Validação automática** de tipos e formatos
- **Mensagens de erro** claras e específicas
- **Sanitização** de dados de entrada

### Segurança

- **Hash de senhas** com SHA-256 + salt
- **Validação de relacionamentos** antes de criação
- **Controle de duplicatas** em relacionamentos
- **Tratamento de erros** padronizado

---

## 🧪 Testando a API

### Exemplo de Requisição

```bash
# Registrar um usuário
curl -X POST "http://localhost:8000/route/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "password123",
    "phone_number": "+1234567890"
  }'

# Criar uma competição
curl -X POST "http://localhost:8000/route/competitions" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "CTF 2024",
    "organizer": "Lycosidae Team",
    "invite_code": "CTF2024",
    "start_date": "2024-01-01T00:00:00",
    "end_date": "2024-01-31T23:59:59"
  }'
```

### Documentação Interativa

Acesse <http://localhost:8000/docs> para testar todos os endpoints diretamente no navegador.

---

## 🤝 Contribuição

### Padrões de Código

- **Docstrings** no formato `"""Explicação"""` no início de cada função
- **Logs estruturados** para todas as operações de banco
- **Validação de dados** com Pydantic schemas
- **Tratamento de erros** padronizado
- **Comentários limpos** sem código desnecessário

### Estrutura de Commits

```text
feat: adiciona nova funcionalidade
fix: corrige bug
docs: atualiza documentação
refactor: refatora código
test: adiciona testes
```

---
