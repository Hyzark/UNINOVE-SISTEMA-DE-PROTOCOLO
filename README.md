# Como executar o projeto

## Sistema de Protocolo

Aplicação web acadêmica para cadastro e acompanhamento de processos, construída com FastAPI e SQLite.

## Funcionalidades implementadas

### Acesso e usuários

- Login com e-mail e senha, sessão autenticada e logout.
- Níveis de acesso: funcionário (`1`), administrador (`2`) e gerente (`3`).
- O administrador pode cadastrar funcionários ou gerentes, vinculando-os a um setor.
- E-mails cadastrados para funcionários e gerentes devem usar `@empresa.sp.gov.br`.
- O painel administrativo permite cadastrar setores.

### Setores, mesas e processos

- Funcionários e gerentes veem as mesas ativas do próprio setor.
- Ao entrar em uma mesa, podem criar processos com assunto e descrição.
- O número do processo é gerado pelo sistema no formato `PROC-000001`.
- A lista da mesa exibe seus processos; ao abrir um processo, a tela mostra dados, situação, setor, mesa, autor e datas.
- O acesso a mesas e processos é validado no servidor por setor.

### Arquivos e documentos

- É possível anexar arquivos a um processo. O limite atual é 20 MB por arquivo.
- O anexo pode ser baixado por usuários autorizados do setor do processo.
- A tela de processo mantém uma lista de arquivos, incluindo PDFs gerados pelo editor.
- O editor de documentos permite texto formatado, títulos, listas e imagens PNG, JPG/JPEG, GIF e WebP.
- Imagens de até 20 MB são redimensionadas no navegador antes de serem inseridas.
- O conteúdo editável é salvo para reabertura. Cada salvamento gera ou substitui o PDF associado ao documento.

### Histórico

- O processo exibe eventos de criação, anexação de arquivos, criação e atualização de documentos editáveis e tramitações que estejam registradas no banco.
- Os eventos mostram usuário, data e hora; a interface formata as datas para o fuso de São Paulo.

## Endpoints principais

| Endpoint | Uso |
| --- | --- |
| `POST /login`, `GET /sessao`, `POST /logout` | Autenticação e sessão |
| `POST /cadastrarfuncionario` | Cadastro administrativo de funcionário ou gerente |
| `GET /setores`, `POST /cadastrarsetor` | Listar e cadastrar setores |
| `POST /cadastrarMesa` | Cadastrar uma mesa para o setor do funcionário autenticado |
| `GET /minhas-mesas`, `POST /mesa-atual` | Listar e selecionar mesa |
| `GET /mesas/{mesa_id}/processos`, `POST /processos` | Listar processos da mesa e criar processo |
| `GET /processos/{processo_id}` | Consultar detalhes, anexos e histórico |
| `POST /processos/{processo_id}/documentos` | Anexar arquivo |
| `GET /documentos/{documento_id}/download` | Baixar arquivo autorizado |
| `POST /processos/{processo_id}/documentos-editoriais` | Criar documento editável e PDF |
| `GET /documentos-editoriais/{documento_id}`, `PUT /documentos-editoriais/{documento_id}` | Reabrir e atualizar documento editável |

## Ainda não implementado

As tabelas de algumas destas funcionalidades já aparecem no esquema do banco, mas ainda não há fluxo completo de tela, rota e serviço para elas:

- Tramitar processo entre mesas e setores.
- Buscar processos por número, assunto, setor, responsável, situação ou datas.
- Alterar a situação do processo pela interface.
- Criar comentários e anotações públicas ou privadas.
- Criar e aplicar marcadores.
- Sobrestamento, controle de disponibilidade por setor, processos relacionados e solicitações de alteração ou exclusão.
- Assinaturas e workflows de aprovação.
- PDF consolidado com todo o processo e seus eventos.
- Recursos de inteligência artificial descritos na documentação funcional.

## Dados e arquivos

- O banco utilizado pela aplicação é `banco.db`, relativo ao diretório de execução.
- `repository.py` contém a criação das tabelas principais. Em uma base nova, execute `python repository.py` uma vez antes de iniciar a aplicação.
- Anexos e PDFs são armazenados localmente em `uploads/documentos/` e `uploads/documentos_editoriais/`.
- Para o primeiro acesso administrativo, a base precisa ter um usuário nível `2` e um setor ativo. O sistema ainda não tem uma tela pública para criar o primeiro administrador.

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
