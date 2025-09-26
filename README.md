# Adam Sandler News Agent 🎬📰

Um agente de IA inteligente que busca notícias sobre Adam Sandler em sites internacionais de notícias e gera relatórios personalizados enviados por email.

## 🚀 Características

- **Arquitetura DDD (Domain-Driven Design)** para escalabilidade
- **Web Scraping Assíncrono** com suporte a múltiplos sites de notícias
- **Geração de Relatórios** em HTML e texto
- **Envio Automático por Email** com suporte a múltiplos destinatários
- **Interface CLI** intuitiva e fácil de usar
- **Configuração Flexível** via variáveis de ambiente
- **Extensível** - fácil adição de novos sites de notícias

## 📋 Pré-requisitos

- Python 3.8 ou superior
- Conta de email com suporte a SMTP (Gmail recomendado)
- Conexão com a internet

## 🛠️ Instalação

### 1. Clone o repositório
```bash
git clone <repository-url>
cd adam-sandler-news-agent
```

### 2. Crie um ambiente virtual
```bash
python -m venv venv
source venv/bin/activate  # No Windows: venv\Scripts\activate
```

### 3. Instale as dependências
```bash
pip install -r requirements.txt
```

### 4. Configure as variáveis de ambiente
```bash
cp .env.example .env
```

Edite o arquivo `.env` com suas configurações:

```env
# Configuração SMTP (exemplo para Gmail)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=seu-email@gmail.com
SMTP_PASSWORD=sua-senha-de-app
SMTP_USE_TLS=true

# Destinatário do relatório
DEFAULT_EMAIL_RECIPIENT=destinatario@exemplo.com
```

### 5. Configure a senha de app do Gmail (se usando Gmail)

1. Acesse [Configurações da conta Google](https://myaccount.google.com/)
2. Vá para "Segurança" → "Verificação em duas etapas"
3. Role para baixo e clique em "Senhas de app"
4. Gere uma nova senha de app para "Email"
5. Use essa senha no campo `SMTP_PASSWORD` do arquivo `.env`

## 🎯 Como Usar

### Comando Básico - Relatório Diário
```bash
python main.py daily-report
```

### Buscar Notícias (sem enviar email)
```bash
python main.py search-news
```

### Testar o Sistema
```bash
python main.py test
```

### Gerar Relatório em Arquivo
```bash
python main.py generate-report --output relatorio.html --format html
```

### Ver Status do Sistema
```bash
python main.py status
```

### Ajuda Completa
```bash
python main.py --help
```

## 📊 Exemplos de Uso

### 1. Relatório Diário Automático
```bash
# Busca notícias e envia por email
python main.py daily-report --email destinatario@exemplo.com
```

### 2. Busca Personalizada
```bash
# Busca apenas notícias sem enviar email
python main.py search-news --max-news 20
```

### 3. Teste Completo do Sistema
```bash
# Testa todas as funcionalidades
python main.py test --send-test-email
```

### 4. Salvar Relatório Localmente
```bash
# Gera relatório HTML local
python main.py generate-report --output "relatorio_$(date +%Y%m%d).html" --format html
```

## 🏗️ Arquitetura

O projeto segue os princípios do Domain-Driven Design (DDD):

```
src/
├── domain/           # Regras de negócio e entidades
│   ├── entities/     # News, NewsSource, Report
│   └── repositories/ # Interfaces dos repositórios
├── infrastructure/   # Implementações concretas
│   ├── web_scraping/ # Scrapers (BBC, etc.)
│   └── email/        # Serviço de email SMTP
├── application/      # Casos de uso e serviços
│   ├── services/     # ReportService
│   └── use_cases/    # NewsAggregatorUseCase
└── interfaces/       # Interfaces externas
    └── cli/          # Interface de linha de comando
```

## 🔧 Configurações Avançadas

### Variáveis de Ambiente Disponíveis

| Variável | Descrição | Padrão |
|----------|-----------|---------|
| `SMTP_SERVER` | Servidor SMTP | smtp.gmail.com |
| `SMTP_PORT` | Porta SMTP | 587 |
| `SMTP_USERNAME` | Usuário SMTP | - |
| `SMTP_PASSWORD` | Senha SMTP | - |
| `DEFAULT_EMAIL_RECIPIENT` | Email destinatário | - |
| `MAX_NEWS_PER_SOURCE` | Máx. notícias por fonte | 10 |
| `REQUEST_TIMEOUT` | Timeout das requisições | 30 |
| `LOG_LEVEL` | Nível de log | INFO |

### Adicionando Novos Sites de Notícias

1. Crie um novo scraper em `src/infrastructure/web_scraping/`
2. Implemente a interface base do scraper
3. Adicione o scraper ao `WebScrapingNewsRepository`

Exemplo:
```python
# src/infrastructure/web_scraping/cnn_scraper.py
class CNNScraper(BaseScraper):
    def get_news_source(self) -> NewsSource:
        return NewsSource(
            name="CNN",
            base_url="https://www.cnn.com",
            source_type=SourceType.WEB_SCRAPING,
            search_endpoint="/search/?q={query}"
        )
```

## 🧪 Testes

### Executar Teste Básico
```bash
python main.py test
```

### Teste com Email
```bash
python main.py test --send-test-email
```

## 📝 Logs

Os logs são exibidos no console por padrão. Para salvar em arquivo:

```bash
python main.py daily-report 2>&1 | tee logs/$(date +%Y%m%d).log
```

## 🚨 Solução de Problemas

### Erro de Autenticação SMTP
- Verifique se a verificação em duas etapas está ativada
- Use uma senha de app específica, não sua senha normal
- Confirme o servidor e porta SMTP

### Erro de Web Scraping
- Verifique sua conexão com a internet
- Alguns sites podem bloquear bots - isso é normal
- O agente tentará outros sites automaticamente

### Erro de Dependências
```bash
pip install --upgrade -r requirements.txt
```

## 🔄 Automação

### Cron Job (Linux/Mac)
Para executar diariamente às 9h:
```bash
crontab -e
# Adicione a linha:
0 9 * * * cd /caminho/para/adam-sandler-news-agent && python main.py daily-report
```

### Task Scheduler (Windows)
1. Abra o Agendador de Tarefas
2. Crie uma nova tarefa básica
3. Configure para executar `python main.py daily-report`

## 🤝 Contribuindo

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/nova-feature`)
3. Commit suas mudanças (`git commit -am 'Adiciona nova feature'`)
4. Push para a branch (`git push origin feature/nova-feature`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

## 🎭 Sobre Adam Sandler

Este agente foi criado para manter você atualizado sobre as últimas notícias do comediante e ator Adam Sandler, conhecido por filmes como "Águas Passadas", "Uncut Gems", e muitos outros sucessos!

---

**Desenvolvido com ❤️ para fãs do Adam Sandler**