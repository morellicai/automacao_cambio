# Automação de Câmbio - Guia do Agente de Código

## 1. Visão Geral & Contexto

- **Objetivo**: Atualizar diariamente a cotação do Câmbio diário no SAP B1 por meio da API do Banco Central.
- **Stack**: Python, Requests, smtplib, urllib3, dotenv, email.

## 2. Padrões de Código & Arquitetura

- **Estilo de Código**:
  - PEP 8.
  - quote-style: single
  - line-lenght = 79
  
- **Estrutura de Pastas**: Neste projeto temos apenas a pasta `services`. Todo módulo adicional, é adicionado lá.

## 3. Comandos & Ferramentas

- **Rodar projeto**: Comandos exatos do terminal para subir o ambiente local.
- **Testes & Linter**: Comandos para executar testes unitários, formatação ou build de verificação.
- **Instalações**: Instruções de qual gerenciador usar para adicionar dependências.

## 4. O Que NÃO Fazer (Obrigatório)

- **Proibições diretas**:
  - Não instalar novas bibliotecas sem solicitar permissão explícita.
  - Não alterar esquemas de banco ou rotas de API sem validação prévia.
  - Nunca commitar chaves, tokens de API ou credenciais de acesso no repositório.

## 5. Formato das Respostas & Entregas

- **Escopo**: Exigir alterações focadas apenas no problema pontuado, evitando reescrever arquivos inteiros desnecessariamente.
- **Commits / PRs**: Conventional Commits.
