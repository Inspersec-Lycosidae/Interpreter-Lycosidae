# Interpreter-Lycosidae

Serviço backend do projeto **Lycosidae CTF**, responsável por abstrair a comunicação entre os componentes e o banco de dados **MariaDB**, utilizando **FastAPI** e **SQLAlchemy** como ORM.

O sistema expõe endpoints HTTPS que recebem requisições HTTP, interpretam as instruções e convertem em consultas padronizadas executadas diretamente no repositório de dados.
Logs são centralizados em `app/logger.py`, garantindo rastreabilidade e clareza na análise de operações.

---

## Arquitetura de Execução

* Orquestração feita por repositório auxiliar com script que inicializa todos os containers.
* Arquivo `.env` centralizado em outro diretório (não deve ser duplicado).
* Conexão ao banco controlada pela variável `DATABASE_URL`.

---

## Estrutura de Dados

### Tabelas

* **Users**: username, email, password, phone\_number
* **Competitions**: name, organizer, invite\_code, start\_date, end\_date
* **Exercises**: link, name, score, difficulty
* **Tags**: type, id
* **Teams**: name, competition, creator, score
* **Containers**: id, deadline

### Relações

* **user\_competitions** → vínculo de usuários com competições
* **user\_teams** → vínculo de usuários com times
* **team\_competitions** → times pertencentes a competições
* **exercise\_tags** → associação de exercícios a múltiplas tags
* **exercise\_competitions** → exercícios pertencentes a competições
* **container\_competitions** → containers associados a competições

---

## Variáveis de Ambiente (.env)

```env
MARIADB_DATABASE=Lycosidae
MARIADB_ROOT_PASSWORD=admin
MARIADB_USER=admin
MARIADB_PASSWORD=admin
DATABASE_URL=mariadb+pymysql://admin:admin@84.247.185.240:3306/Lycosidae
JWT_SECRET="Lycosidae"
JWT_EXPIRATION=1800
PASS_SALT="Lycosidae"
```

# Rotas a serem usadas 

# CRUD para usuario competicao exercicos teams tags e containers
# CRUD para tabelas de relacoes 






