# Gerenciamento de Processos

Aplicação web para cadastro e acompanhamento de processos, construída com FastAPI e SQLite. A interface autenticada é servida em <code>/sistema</code> e suas telas, scripts e estilos ficam em <code>protocolo-digital/</code>.

## Telas e funcionalidades

### Acesso

- A tela de login fica em <code>/</code> e usa e-mail e senha cadastrados.
- O cadastro de funcionários e gerentes exige e-mail <code>@empresa.sp.gov.br</code>. O cadastro inicial do administrador exige e-mail <code>@admin.sp.gov.br</code>.
- O logout encerra a sessão. Ao abrir a página de login, sessões antigas são descartadas; a reinicialização do servidor também invalida sessões anteriores.
- Os perfis são funcionário (<code>1</code>), administrador (<code>2</code>) e gerente (<code>3</code>).

### Processos

- **Processos:** mostra indicadores calculados com as datas do banco, os processos da mesa selecionada e filtros por assunto, número e situação. Clicar em “Processos” atualiza os dados da mesa no servidor.
- A busca do cabeçalho consulta processos por número ou assunto em todo o setor; a lista principal continua limitada à mesa escolhida.
- **Iniciar Processo:** cria processos com assunto e descrição. O número é gerado no formato <code>PROC-000001</code>.
- O seletor de mesa permite trocar de mesa e escolher “+ Criar mesa”. As mesas pertencem ao setor associado à conta.
- A tela de um processo mostra dados, documentos, status e andamento. O status pode ser alterado entre **Em análise** (roxo), **Em andamento** (azul) e **Aguardando solicitação** (cinza), com registro no histórico.
- Funcionários, gerentes e administradores acessam somente os processos do setor associado à conta.

### Documentos e anexos

- O processo aceita anexos de até 20 MB. Antes de enviar um arquivo, é obrigatório informar o título que será exibido no processo.
- Clicar em um documento abre a prévia. O download acontece pelo botão “Baixar”.
- Anexos enviados podem ter o título alterado ou o arquivo substituído.
- A prévia exibe PDF e imagens no navegador; planilhas <code>.xlsx</code>/<code>.xlsm</code>, <code>.ods</code> e <code>.csv</code>; texto de <code>.docx</code> e <code>.pptx</code>; arquivos <code>.txt</code>, <code>.log</code>, <code>.json</code>, <code>.xml</code> e <code>.md</code>; e a lista de conteúdo de arquivos ZIP. Algumas prévias são limitadas para manter a tela responsiva. Outros formatos podem ser baixados para abertura no aplicativo apropriado.
- **Novo documento** abre o editor de texto formatado, com títulos, parágrafos, listas e imagens. O conteúdo fica salvo para edição posterior e cada salvamento gera ou atualiza o PDF anexado ao processo.

### Andamento e auditoria

- O andamento do processo mostra data e hora, usuário, ação e descrição de eventos registrados, como criação do processo, alteração de status, anexos e documentos editoriais.
- Os registros identificam o usuário responsável. Alterações de status também incluem o nome de quem as fez na descrição.
- As telas administrativas de **Criar setor** e **Adicionar funcionário** têm “Consultar histórico”, que mostra o administrador, a data, a ação e os detalhes do cadastro. Esses registros passam a existir a partir da implantação da auditoria; cadastros anteriores não têm autor registrado para consulta retroativa.

### Administração

- O administrador usa o mesmo painel e as telas comuns de processos. O menu lateral também oferece **Criar setor** e **Adicionar funcionário**.
- **Criar setor** cadastra um setor e registra no histórico o administrador que o criou.
- **Adicionar funcionário** cadastra funcionário ou gerente, com e-mail, senha, cargo e setor, e registra o administrador responsável.
- Funcionários, gerentes e administradores podem criar mesas para o setor associado à conta.
- Perfil, tema claro/escuro e tamanho da fonte ficam disponíveis pelos controles compartilhados. O tema escuro usa fundo preto e acentos verdes.

## Dados e configuração inicial

Execute os comandos a partir da pasta raiz do projeto.

1. Crie e ative o ambiente virtual e instale as dependências:

       python -m venv venv
       venv\Scripts\activate
       pip install -r requirements.txt

2. Crie as tabelas, se necessário, e cadastre o primeiro setor e administrador com dados próprios:

       python repository.py
       python repositories/add_admin.py

   O cadastro inicial pede os dados no terminal e não usa credenciais de exemplo.

3. Inicie o servidor:

       uvicorn main:app --reload

   Sistema: <code>http://127.0.0.1:8000</code>. Documentação da API: <code>http://127.0.0.1:8000/docs</code>.

- O banco SQLite utilizado é <code>banco.db</code>. <code>repository.py</code> cria as tabelas; ele não cria dados de exemplo.
- <code>repository2.py</code> apaga todos os registros do banco, inclusive usuários e administradores, reinicia os IDs e mantém as tabelas. Use-o somente para começar com uma base vazia. Ele não apaga arquivos armazenados em <code>uploads/documentos/</code> e <code>uploads/documentos_editoriais/</code>.
- Os anexos e PDFs gerados ficam nessas pastas locais. Arquivos físicos sem registro no banco após uma limpeza precisam ser removidos manualmente, caso também se deseje apagá-los.
- O sistema não cria processos, usuários, datas ou movimentações fictícias para preencher as telas.

## Rotas principais

| Rota | Uso |
| --- | --- |
| <code>GET /</code>, <code>GET /sistema</code> | Login e interface autenticada |
| <code>POST /login</code>, <code>GET /sessao</code>, <code>POST /logout</code> | Autenticação e sessão |
| <code>GET /minhas-mesas</code>, <code>POST /mesa-atual</code>, <code>POST /cadastrarMesa</code> | Listar, selecionar e criar mesas |
| <code>GET /mesas/{mesa_id}/processos</code>, <code>POST /processos</code> | Listar processos da mesa e criar processo |
| <code>GET /processos/busca?termo=...</code>, <code>GET /processos/{processo_id}</code> | Buscar no setor e consultar processo |
| <code>PATCH /processos/{processo_id}/situacao</code> | Alterar status do processo |
| <code>POST /processos/{processo_id}/documentos</code>, <code>GET /documentos/{documento_id}/preview</code>, <code>GET /documentos/{documento_id}/download</code>, <code>PUT /documentos/{documento_id}</code> | Anexar, pré-visualizar, baixar e editar anexos |
| <code>POST /processos/{processo_id}/documentos-editoriais</code>, <code>GET /documentos-editoriais/{documento_id}</code>, <code>PUT /documentos-editoriais/{documento_id}</code> | Criar, consultar e atualizar documentos editáveis e seus PDFs |
| <code>GET /setores</code>, <code>POST /cadastrarsetor</code>, <code>GET /setores/historico</code> | Listar, criar e auditar setores |
| <code>POST /cadastrarfuncionario</code>, <code>GET /usuarios/historico</code> | Criar funcionário/gerente e consultar auditoria |

## Ainda não disponíveis na interface

- Tramitação de processos entre mesas ou setores.
- Comentários e anotações públicas ou privadas.
- Marcadores, sobrestamento, disponibilidade por setor e processos relacionados.
- Solicitações de alteração/exclusão, assinaturas e fluxos de aprovação.
- PDF consolidado do processo e recursos de inteligência artificial.

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
