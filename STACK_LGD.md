# Stack LGD Mantos

Este arquivo resume as tecnologias do projeto e serve como referência rápida
para manutenção, onboarding e futuras decisões técnicas.

## Backend

- **FastAPI**: expõe a API HTTP versionada em `/api/v1`.
- **SQLAlchemy Async**: acessa o PostgreSQL com sessões assíncronas.
- **Pydantic**: define contratos de entrada e saída das rotas.
- **JWT com python-jose**: protege as rotas autenticadas.
- **httpx**: realiza chamadas externas para a camada de IA.

## Banco de Dados

- **PostgreSQL**: base única para catálogo, estoque, vendas, compras, despesas e análises.
- **asyncpg**: driver assíncrono usado pelo SQLAlchemy.
- **Volumes Docker**: preservam dados do banco e uploads entre reinicializações.

## Frontend

- **React + Vite**: frontend web responsivo oficial do projeto, acessado pelo navegador em qualquer dispositivo.
- **PWA**: suporte a instalação e uso em mobile via navegador, sem app nativo.

## Infraestrutura Local

- **Dockerfile**: cria a imagem do backend.
- **docker-compose.yml**: sobe PostgreSQL e API com reload para desenvolvimento.
- **requirements.txt**: fixa dependências Python compartilhadas pelo ambiente local.

## IA

- A camada central fica em `backend/app/core/ai`.
- Os módulos devem chamar `AIService.generate(...)` em vez de integrar direto com provedores externos.
- A IA gera explicações, descrições e sugestões, mas não altera dados operacionais sozinha.
