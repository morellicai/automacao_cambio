# 💱 Automação de Câmbio SAP Business One (PTAX)

Este projeto consiste em uma automação desenvolvida em Python para consultar diariamente a taxa de câmbio PTAX de venda no Banco Central e atualizar automaticamente os registros de cotação no SAP Business One (B1) através da Service Layer (API REST). Ao concluir o processamento, o sistema valida os fluxos e envia uma notificação por e-mail aos responsáveis.

## 🚀 Fluxo de Execução

1. Consulta da Taxa PTAX: O script conecta-se à API oficial do Banco Central do Brasil para obter a cotação atualizada da PTAX de venda.
2. Atualização via Service Layer (SAP B1): O robô efetua a autenticação na Service Layer do SAP Business One e realiza a requisição para gravação das taxas de câmbio atualizadas.
3. Validação e Notificação: Ao longo do fluxo de execução, o script realiza validações da conexão com os serviços (SAP B1 e servidor de e-mail) e dispara uma notificação consolidando o status da operação.

## 📂 Estrutura do Projeto

Abaixo está a organização dos módulos e arquivos que compõem a solução:

```plain text
automacao_cambio/
├── AtualizacaoCambio.py          # Ponto de entrada (Main) que orquestra o fluxo.
├── requirements.txt              # Dependências do projeto Python.
├── .env.example                  # Modelo de estrutura para as variáveis de ambiente.
├── AGENT.md                      # Especificações técnicas do agente.
├── .gitignore                    # Arquivos ignorados pelo controle de versão.
└── services/                     # Módulos funcionais e scripts de validação:
    ├── busca_ptax_venda.py       # Consulta e extração da taxa PTAX via API do BACEN.
    ├── login_logout_sap.py       # Gerenciamento de sessão e requisições na Service Layer do SAP B1.
    ├── email_service.py          # Serviço de montagem e envio dos e-mails de log.
    ├── login_logout_sap_test.py  # Script de validação da autenticação na Service Layer.
    └── test_api.py               # Script de verificação de conectividade e resposta da API PTAX.
```


## 📋 Pré-requisitos

Antes de executar a aplicação, certifique-se de que o ambiente possui:

- Python: Versão 3.8 ou superior.
- SAP Business One (B1): Acesso à Service Layer ativa e acessível na rede/ambiente.
- Credenciais de Acesso: Usuário e senha cadastrados no SAP B1, além de acesso a um servidor SMTP para envio de e-mails.

## 🛠️ Instalação e Passo a Passo de Execução

- Clonar o repositório

```plain text
git clone https://github.com/seu-usuario/automacao_cambio.git
cd automacao_cambio
```

- Criar e ativar o ambiente virtual (recomendado):

```bash
# No Windows (PowerShell / CMD)
python -m venv venv
venv\Scripts\activate

# No Linux / macOS
python3 -m venv venv
source venv/bin/activate


Instalar as dependências:

pip install -r requirements.txt
```

- Configurar o Arquivo de Credenciais (.env):

Crie um arquivo chamado .env na raiz do projeto (com base no .env.example) e insira as credenciais do SAP Business One, URLs da Service Layer e dados do servidor de e-mail:

```bash
# Exemplo de configuração no arquivo .env
EMAIL_HOST=smtp.example.com.br
EMAIL_PORT=465
EMAIL_USER=email@example.com.br
EMAIL_PASS=example_password

SAP_URL  = "https://localhost/b1s/v1"
SAP_DB   = "SAP_DATABASE"
SAP_USER = "user_id"
SAP_PASS = "Senha"
```

- Executar a automação:

```bash
python AtualizacaoCambio.py
```

## 🔍 Validações de Conexão e Execução

Os arquivos de teste contidos no diretório services/ (login_logout_sap_test.py e test_api.py) não são testes unitários isolados. Trata-se de scripts de verificação utilizados para testar a comunicação direta com a Service Layer do SAP B1 e com a API do Banco Central no decorrer do desenvolvimento ou durante rotinas de diagnóstico.

Para executar manualmente uma verificação individual dos serviços:

```bash
python services/test_api.py
python services/login_logout_sap_test.py
```

## 🔒 Segurança e Boas Práticas

> **Atenção**: Mantenha o arquivo .env estritamente listado dentro do seu .gitignore. Nunca faça commit de senhas, credenciais do SAP B1 ou dados do servidor de e-mail no repositório.