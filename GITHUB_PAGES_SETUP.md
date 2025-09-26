# Configuração do GitHub Pages

Este guia explica como configurar o GitHub Pages para publicar automaticamente os relatórios de notícias sobre Adam Sandler.

## 📋 Pré-requisitos

1. **Repositório no GitHub**: Você precisa ter um repositório no GitHub onde o código está hospedado
2. **Token de Acesso**: Um token de acesso pessoal do GitHub com permissões adequadas

## 🔧 Passo a Passo

### 1. Criar Token de Acesso no GitHub

1. Acesse [GitHub Settings > Developer settings > Personal access tokens](https://github.com/settings/tokens)
2. Clique em "Generate new token" > "Generate new token (classic)"
3. Configure o token:
   - **Note**: `Adam Sandler News Agent`
   - **Expiration**: Escolha um período adequado (recomendado: 90 dias ou mais)
   - **Scopes**: Selecione as seguintes permissões:
     - ✅ `repo` (Full control of private repositories)
     - ✅ `workflow` (Update GitHub Action workflows)
4. Clique em "Generate token"
5. **IMPORTANTE**: Copie o token gerado (você não conseguirá vê-lo novamente)

### 2. Configurar Variáveis de Ambiente

1. Abra o arquivo `.env` na raiz do projeto
2. Configure as seguintes variáveis:

```env
# GitHub Pages Configuration
GITHUB_TOKEN=seu_token_aqui
GITHUB_REPOSITORY=seu_usuario/nome_do_repositorio
```

**Exemplo:**
```env
GITHUB_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
GITHUB_REPOSITORY=joaosilva/adam-sandler-news
```

### 3. Habilitar GitHub Pages no Repositório

1. Acesse seu repositório no GitHub
2. Vá para **Settings** > **Pages**
3. Configure:
   - **Source**: Deploy from a branch
   - **Branch**: `main` (ou `master`)
   - **Folder**: `/docs`
4. Clique em "Save"

### 4. Configurar Branch Principal (se necessário)

Se você ainda não tem um repositório Git configurado:

```bash
# Inicializar repositório
git init

# Adicionar arquivos
git add .

# Fazer primeiro commit
git commit -m "Initial commit: Adam Sandler News Agent"

# Adicionar repositório remoto
git remote add origin https://github.com/seu_usuario/seu_repositorio.git

# Enviar para GitHub
git push -u origin main
```

## 🚀 Como Usar

### Gerar Relatório e Publicar Automaticamente

```bash
# Gerar relatório com publicação automática no GitHub Pages
python main.py --report

# Ou usar o comando específico para relatório
python main.py --generate-report
```

### Verificar Status da Configuração

```bash
# Verificar se o GitHub está configurado corretamente
python -c "
from src.infrastructure.github.github_service import GitHubService
service = GitHubService()
status = service.get_github_pages_status()
print('Configurado:', status['configured'])
print('Repositório:', status['repository'])
print('URL do site:', status['pages_url'])
"
```

## 🌐 Acessando o Site

Após a primeira publicação, seu site estará disponível em:
```
https://seu_usuario.github.io/nome_do_repositorio
```

**Exemplo:**
```
https://joaosilva.github.io/adam-sandler-news
```

## 📁 Estrutura dos Arquivos

O sistema criará automaticamente:

```
docs/
├── index.html              # Página principal do site
├── reports.json            # Índice dos relatórios
├── relatorio_YYYYMMDD_HHMMSS.html  # Relatórios individuais
└── ...
```

## 🔍 Solução de Problemas

### Erro: "GitHub não configurado"
- Verifique se `GITHUB_TOKEN` e `GITHUB_REPOSITORY` estão definidos no `.env`
- Confirme que o token tem as permissões corretas

### Erro: "401 Unauthorized"
- O token pode estar expirado ou inválido
- Gere um novo token seguindo o passo 1

### Erro: "404 Not Found"
- Verifique se o nome do repositório está correto no formato `usuario/repositorio`
- Confirme que o repositório existe e você tem acesso

### Site não atualiza
- Aguarde alguns minutos (GitHub Pages pode demorar para atualizar)
- Verifique se os arquivos foram enviados para a branch correta
- Confirme que o GitHub Pages está configurado para usar a pasta `/docs`

## 🔒 Segurança

- **NUNCA** commite o arquivo `.env` com tokens reais
- O `.gitignore` já está configurado para ignorar o `.env`
- Mantenha seus tokens seguros e renove-os periodicamente

## 📊 Funcionalidades

- ✅ Publicação automática de relatórios
- ✅ Página principal com lista de relatórios
- ✅ Relatórios com timestamp único
- ✅ Análise de IA incluída nos relatórios
- ✅ Design responsivo
- ✅ Histórico de até 50 relatórios

## 🆘 Suporte

Se encontrar problemas:

1. Verifique os logs do sistema
2. Confirme todas as configurações
3. Teste a conexão com o GitHub
4. Consulte a documentação do GitHub Pages

---

**Desenvolvido para o Adam Sandler News Agent** 🎬📰