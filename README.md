# 👗 Minha Loja — Sistema de Gestão Interno

Sistema interno focado em **produtos, estoque, compras e finanças** da sua loja de camisetas oversized e peruanas.

---

## 🚀 Subir em 1 comando

### Pré-requisitos
- Docker + Docker Compose instalados

### 1. Configure o `.env`
Edite o arquivo `.env` com suas configurações:
```
APP_PASSWORD=sua-senha-aqui          # senha de acesso ao sistema
ANTHROPIC_API_KEY=sk-ant-...         # sua chave da Anthropic (para IA)
```

### 2. Suba tudo
```bash
docker compose up --build
```

### 3. Acesse
**http://localhost:8000**
Senha padrão: `minhaloja123`

---

## ✅ O que tem dentro

| Módulo | Funcionalidade |
|--------|---------------|
| 📊 Dashboard | KPIs do dia e mês, receita, lucro, gráfico 30 dias |
| 👕 Produtos | Cadastro completo, variantes, margem, fotos organizadas |
| 🏭 Fornecedores | Cadastro com contato e histórico |
| 📦 Estoque | Movimentações, alertas de mínimo, inventário |
| 🛍️ Compras | Pedidos de compra → receber atualiza estoque automaticamente |
| 💳 Vendas | Registro por canal (loja/Instagram/WhatsApp/site) |
| 💰 Financeiro | DRE mensal: receita, CMV, lucro bruto e líquido |
| 🧾 Despesas | Controle de gastos por categoria |
| 📈 Análises | Top produtos, vendas por tamanho, por canal |
| 💡 O Que Comprar | Sugestão de reposição baseada em giro + estoque |
| 🤖 Assistente IA | Descrições, marketing, análise, decisões de compra |

## ❌ O que foi removido

- Multi-usuário / controle de acesso por perfil
- CRM de clientes e pontos de fidelidade
- Carrinho / PDV
- Histórico de cancelamento de vendas

---

## 🤖 Assistente de IA

O assistente é treinado com contexto da sua loja e pode:
- Criar descrições de produtos para Instagram/WhatsApp
- Sugerir o que comprar com base nas vendas
- Analisar desempenho por tamanho/modelo
- Criar legendas e copys para postagens
- Dar insights sobre estratégia de vendas

**Requer `ANTHROPIC_API_KEY` configurada no `.env`**

---

## 📷 Fotos de Produtos

Upload direto pelo sistema (botão 📷 na lista de produtos). As fotos ficam salvas em volume Docker persistente.

---

## 🛑 Parar / Limpar

```bash
docker compose down          # para sem apagar dados
docker compose down -v       # apaga banco e uploads
```

---

## 🔐 Segurança

Autenticação simplificada por senha única (configurada no `.env`).
Token JWT válido por 30 dias — sem necessidade de fazer login todo dia.
