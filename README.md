# MoneyHub

MoneyHub é um site de recompensas e monetização construído com Flask, SQLite, HTML5, CSS3 e JavaScript.

## Recursos

- Interface moderna com tema escuro e detalhes verdes
- Login e cadastro de usuário
- Painel do usuário com ranking, check-in diário e estatísticas
- Perfil de usuário editável
- Indicações com pontos bônus
- Área administrativa para gerenciar usuários
- API REST para dados do frontend
- PWA com manifest e service worker
- Proteções contra CSRF, XSS e SQL Injection

## Estrutura de pastas

- `moneyhub/` - código da aplicação Flask
- `moneyhub/static/` - arquivos estáticos CSS, JS, icons
- `moneyhub/templates/` - templates Jinja2
- `moneyhub/instance/` - banco SQLite (não comitado)

## Requisitos

- Python 3.11+
- pip

## Instalação

1. Crie um ambiente virtual:

```bash
python3 -m venv venv
source venv/bin/activate
```

2. Instale as dependências:

```bash
pip install -r moneyhub/requirements.txt
```

3. Execute a aplicação:

```bash
python moneyhub/app.py
```

4. Acesse no navegador:

```text
http://127.0.0.1:5000
```

## Conta administrativa

- Email: `admin@moneyhub.local`
- Senha: `admin1234`

## Observações

- O banco SQLite será criado automaticamente em `moneyhub/instance/moneyhub.db`.
- Para usar o PWA, abra o site em HTTPS ou em um servidor local suportado.
- Edite `moneyhub/config.py` para ajustar a chave secreta e o caminho do banco.
