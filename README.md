# Como executar o projeto

### 1. Criar a VENV
```bash
python -m venv venv
```

### 2. Ativar a VENV

**Windows:**
```bash
venv\Scripts\activate
```

### 3. Instalar as dependências
```bash
pip install -r requirements.txt
```

### 4. Executar o projeto
```bash
uvicorn main:app --reload
```

### 5. Acessar
```text
http://127.0.0.1:8000
```

Documentação da API:
```text
http://127.0.0.1:8000/docs
```

---

# Git

### Antes de começar a trabalhar
```bash
git pull
```

### Depois de fazer suas alterações
```bash
git status
git add .
git commit -m "descrição da alteração"
git push
```

### Para atualizar sua branch com a `main`
```bash
git checkout main
git pull
git checkout sua-branch
git merge main
```

### Para fazer o Merge na `main`
```bash
git checkout main
git pull
git merge sua-branch
git push
```

### Fluxo básico
```text
git pull
↓
fazer alterações
↓
git add .
↓
git commit
↓
git push
↓
Merge na main
```