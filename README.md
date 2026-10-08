# Como executar o projeto

### 1. Criar a VENV
```bash
python -m venv venv
```

A `venv` cria um ambiente virtual separado para as dependências do projeto.

### 2. Ativar a VENV

**Windows:**
```bash
venv\Scripts\activate
```

Quando estiver ativada, aparecerá `(venv)` no início do terminal.

### 3. Instalar as dependências
```bash
pip install -r requirements.txt
```

Instala todas as bibliotecas necessárias para executar o projeto.

### 4. Executar o projeto
```bash
uvicorn main:app --reload
```

Inicia o servidor FastAPI.

### 5. Acessar

Projeto:
```text
http://127.0.0.1:8000
```

Documentação da API:
```text
http://127.0.0.1:8000/docs
```

---

# Git

## Configuração inicial

### 1. Inicializar o Git
```bash
git init
```

Cria um repositório Git dentro da pasta atual do projeto.

### 2. Conectar ao GitHub
```bash
git remote add origin https://github.com/Hyzark/UNINOVE-SISTEMA-DE-PROTOCOLO.git
```

`origin` é o nome dado ao repositório remoto. Neste caso, `origin` aponta para o repositório do projeto no GitHub.

### 3. Verificar o repositório remoto
```bash
git remote -v
```

Mostra para qual endereço o `origin` está apontando.

Exemplo:
```text
origin  https://github.com/Hyzark/UNINOVE-SISTEMA-DE-PROTOCOLO.git (fetch)
origin  https://github.com/Hyzark/UNINOVE-SISTEMA-DE-PROTOCOLO.git (push)
```

---

# Branches

O projeto utiliza o seguinte fluxo:

```text
main
  ↑
develop
  ↑
feature/*
```

A `main` contém a versão estável do projeto.

A `develop` é usada para integração e testes das funcionalidades.

As `feature/*` são criadas para desenvolver cada funcionalidade separadamente.

### Criar a branch develop
```bash
git checkout -b develop
```

Cria a branch `develop` e já muda para ela.

### Ver as branches
```bash
git branch
```

Mostra as branches locais. O `*` indica a branch atual.

### Criar uma feature
```bash
git checkout -b feature/login
```

Cria a branch `feature/login` e já muda para ela.

---

# Fluxo de trabalho

### 1. Ir para a develop e atualizar
```bash
git checkout develop
git pull
```

### 2. Criar uma branch para a funcionalidade
```bash
git checkout -b feature/nome-da-funcionalidade
```

### 3. Fazer as alterações no projeto

### 4. Verificar as alterações
```bash
git status
```

Mostra quais arquivos foram modificados, adicionados ou removidos.

### 5. Adicionar as alterações
```bash
git add .
```

Coloca as alterações na área de preparação para o commit.

### 6. Criar o commit
```bash
git commit -m "Descrição da alteração"
```

Salva as alterações no histórico do Git.

### 7. Enviar a branch para o GitHub
```bash
git push -u origin feature/nome-da-funcionalidade
```

`origin` é o repositório remoto e `feature/nome-da-funcionalidade` é a branch que será enviada.

Depois do primeiro `push` dessa branch, normalmente basta usar:
```bash
git push
```

---

# Merge

Depois de terminar uma funcionalidade, deve ser feito um Pull Request:

```text
feature/login
      ↓
    Pull Request
      ↓
   develop
```

Depois que as funcionalidades forem testadas e a versão estiver pronta:

```text
develop
   ↓
Pull Request
   ↓
main
```

---

# Comandos mais utilizados

```bash
git status
```
Verifica o estado do projeto.

```bash
git add .
```
Adiciona as alterações para o próximo commit.

```bash
git commit -m "mensagem"
```
Cria um commit com as alterações.

```bash
git push
```
Envia os commits para o GitHub.

```bash
git pull
```
Baixa e integra as alterações do GitHub.

```bash
git branch
```
Lista as branches locais.

```bash
git checkout nome-da-branch
```
Troca para outra branch.

```bash
git merge nome-da-branch
```
Integra uma branch na branch atual.