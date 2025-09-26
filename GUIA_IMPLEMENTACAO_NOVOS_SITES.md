# Guia de Implementação - Novos Sites de Notícias

## Visão Geral

Este guia explica como adicionar suporte para novos sites de notícias ao Adam Sandler News Agent. O sistema foi projetado para ser facilmente extensível através da implementação de novos scrapers.

## Estrutura Base de um Scraper

### 1. Classe Base do Scraper

Todo scraper deve seguir a mesma estrutura básica:

```python
import asyncio
import aiohttp
from bs4 import BeautifulSoup
from datetime import datetime
from typing import List, Optional
from urllib.parse import urljoin, quote

from ...domain.entities.news import News
from ...domain.entities.news_source import NewsSource, SourceType

class NovoSiteScraper:
    """Scraper específico para [Nome do Site]."""
    
    def __init__(self):
        self.base_url = "https://www.exemplo.com"
        self.search_url = "https://www.exemplo.com/search"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    
    def get_news_source(self) -> NewsSource:
        """Retorna a configuração da fonte."""
        return NewsSource(
            name="Nome do Site",
            base_url=self.base_url,
            source_type=SourceType.WEB_SCRAPING,
            search_endpoint="/search",
            config={
                "max_results": 20,
                "timeout": 30,
                "retry_attempts": 3
            }
        )
    
    async def search_adam_sandler_news(self, session: aiohttp.ClientSession, 
                                     max_results: int = 10) -> List[News]:
        """Busca notícias sobre Adam Sandler."""
        # Implementação específica do site
        pass
```

## Passo a Passo para Implementação

### Passo 1: Análise do Site Alvo

Antes de começar a implementação, analise o site:

1. **URL de Busca**: Como o site estrutura URLs de busca?
   ```
   Exemplos:
   - BBC: https://www.bbc.com/search?q=Adam%20Sandler
   - CNN: https://www.cnn.com/search?q=Adam+Sandler
   - G1: https://g1.globo.com/busca/?q=Adam+Sandler
   ```

2. **Estrutura HTML**: Inspecione os elementos da página de resultados
   ```html
   <!-- Exemplo de estrutura típica -->
   <div class="search-results">
       <article class="news-item">
           <h2 class="title">Título da Notícia</h2>
           <p class="summary">Resumo da notícia...</p>
           <a href="/noticia/123">Link</a>
           <time datetime="2025-01-01">Data</time>
       </article>
   </div>
   ```

3. **Estrutura da Página do Artigo**: Como o conteúdo completo é estruturado?
   ```html
   <!-- Exemplo de página de artigo -->
   <article class="article-content">
       <h1 class="article-title">Título</h1>
       <div class="article-body">
           <p>Conteúdo do artigo...</p>
       </div>
   </article>
   ```

### Passo 2: Implementação do Scraper

#### 2.1 Método de Busca Principal

```python
async def search_adam_sandler_news(self, session: aiohttp.ClientSession, 
                                 max_results: int = 10) -> List[News]:
    """Busca notícias sobre Adam Sandler no [Nome do Site]."""
    
    query = "Adam Sandler"
    
    try:
        # Construir URL de busca (adaptar para cada site)
        url = f"{self.search_url}?q={quote(query)}"
        print(f"URL de busca: {url}")
        
        async with session.get(url, headers=self.headers, timeout=30) as response:
            if response.status != 200:
                print(f"Erro ao acessar {self.base_url}: Status {response.status}")
                return []
            
            html = await response.text()
            return await self._parse_search_results(html, max_results, session)
            
    except asyncio.TimeoutError:
        print(f"Timeout ao acessar {self.base_url}")
        return []
    except Exception as e:
        print(f"Erro ao buscar notícias: {str(e)}")
        return []
```

#### 2.2 Parser de Resultados

```python
async def _parse_search_results(self, html: str, max_results: int, 
                              session: aiohttp.ClientSession) -> List[News]:
    """Analisa os resultados de busca."""
    soup = BeautifulSoup(html, 'html.parser')
    news_list = []
    
    # IMPORTANTE: Adaptar seletores para cada site
    selectors = [
        '.news-item',           # Seletor principal
        'article.search-result', # Seletor alternativo
        '.result-item',         # Fallback
    ]
    
    articles = []
    for selector in selectors:
        articles = soup.select(selector)
        if articles:
            print(f"Usando seletor '{selector}' - encontrados {len(articles)} artigos")
            break
    
    if not articles:
        print("Nenhum artigo encontrado")
        return []
    
    for article in articles[:max_results]:
        try:
            news = self._extract_news_from_article(article)
            if news:
                print(f"Notícia extraída: '{news.title}' - URL: {news.url}")
                
                # Buscar conteúdo completo
                full_content = await self.get_article_content(session, news.url)
                if full_content and len(full_content) > len(news.content):
                    news.content = full_content
                
                if news.is_relevant_to_adam_sandler():
                    print(f"✅ Notícia relevante: {news.title}")
                    news_list.append(news)
                else:
                    print(f"❌ Notícia não relevante: {news.title}")
                    
        except Exception as e:
            print(f"Erro ao extrair notícia: {str(e)}")
            continue
    
    return news_list[:max_results]
```

#### 2.3 Extração de Dados Básicos

```python
def _extract_news_from_article(self, article) -> Optional[News]:
    """Extrai informações básicas de um elemento article."""
    try:
        # ADAPTAR: Seletores específicos do site
        title_selectors = [
            'h2.title',
            'h3.headline', 
            '.news-title',
            'h1', 'h2', 'h3'
        ]
        
        title = ""
        for selector in title_selectors:
            title_elem = article.select_one(selector)
            if title_elem:
                title = title_elem.get_text(strip=True)
                break
        
        if not title:
            return None
        
        # Encontrar link
        link_elem = article.find('a', href=True)
        if not link_elem:
            return None
        
        url = link_elem.get('href', '')
        if url.startswith('/'):
            url = urljoin(self.base_url, url)
        
        # Encontrar resumo/conteúdo básico
        content_selectors = [
            '.summary',
            '.excerpt', 
            'p.description',
            'p'
        ]
        
        content = ""
        for selector in content_selectors:
            content_elem = article.select_one(selector)
            if content_elem:
                content = content_elem.get_text(strip=True)
                if content and len(content) > 10:
                    break
        
        if not content or len(content) <= 10:
            content = title
        
        # Tentar extrair data (opcional)
        published_date = datetime.now()
        date_elem = article.select_one('time')
        if date_elem:
            # Implementar parsing de data específico do site
            pass
        
        return News(
            title=title,
            content=content,
            url=url,
            source="Nome do Site",
            published_date=published_date,
            author=None
        )
        
    except Exception as e:
        print(f"Erro ao extrair notícia: {str(e)}")
        return None
```

#### 2.4 Extração de Conteúdo Completo

```python
async def get_article_content(self, session: aiohttp.ClientSession, 
                            url: str) -> Optional[str]:
    """Busca o conteúdo completo de um artigo."""
    try:
        async with session.get(url, headers=self.headers, timeout=30) as response:
            if response.status != 200:
                return None
            
            html = await response.text()
            soup = BeautifulSoup(html, 'html.parser')
            
            # ADAPTAR: Seletores específicos para conteúdo do artigo
            content_selectors = [
                '.article-content p',
                '.post-content p',
                '.entry-content p',
                'article p',
                '.content p'
            ]
            
            content_parts = []
            for selector in content_selectors:
                elements = soup.select(selector)
                if elements:
                    for elem in elements:
                        text = elem.get_text(strip=True)
                        if text and len(text) > 20:
                            content_parts.append(text)
                    break
            
            return ' '.join(content_parts) if content_parts else None
            
    except Exception as e:
        print(f"Erro ao buscar conteúdo do artigo: {str(e)}")
        return None
```

### Passo 3: Integração ao Sistema

#### 3.1 Adicionar ao Repositório

Edite `src/infrastructure/web_scraping/news_repository_impl.py`:

```python
from .novo_site_scraper import NovoSiteScraper

class WebScrapingNewsRepository(NewsRepository):
    def __init__(self):
        self.scrapers = {
            "BBC News": BBCScraper(),
            "Nome do Site": NovoSiteScraper(),  # ADICIONAR AQUI
        }
```

#### 3.2 Atualizar Método de Busca

```python
async def fetch_news_from_source(self, source: NewsSource, query: str) -> List[News]:
    # ... código existente ...
    
    try:
        if source.name == "BBC News":
            return await scraper.search_adam_sandler_news(session, max_results)
        elif source.name == "Nome do Site":  # ADICIONAR
            return await scraper.search_adam_sandler_news(session, max_results)
        else:
            return []
```

## Exemplos Práticos

### Exemplo 1: Site com Estrutura Simples (G1)

```python
class G1Scraper:
    def __init__(self):
        self.base_url = "https://g1.globo.com"
        self.search_url = "https://g1.globo.com/busca"
        
    # Seletores específicos do G1
    def _get_selectors(self):
        return {
            'articles': '.widget--info__text-container',
            'title': '.widget--info__title',
            'link': '.widget--info__text-container a',
            'content': '.content-text__container p'
        }
```

### Exemplo 2: Site com JavaScript (CNN)

```python
class CNNScraper:
    def __init__(self):
        self.base_url = "https://www.cnn.com"
        self.search_url = "https://www.cnn.com/search"
        
    # Para sites com muito JavaScript, pode ser necessário
    # usar selenium ou aguardar carregamento
    async def _wait_for_content(self, soup):
        # Implementar lógica de espera se necessário
        pass
```

## Checklist de Implementação

### ✅ Análise Prévia
- [ ] Identificar URL de busca
- [ ] Mapear seletores CSS principais
- [ ] Testar seletores no DevTools
- [ ] Verificar se precisa de headers especiais
- [ ] Checar rate limiting do site

### ✅ Implementação
- [ ] Criar classe do scraper
- [ ] Implementar `get_news_source()`
- [ ] Implementar `search_adam_sandler_news()`
- [ ] Implementar `_parse_search_results()`
- [ ] Implementar `_extract_news_from_article()`
- [ ] Implementar `get_article_content()`

### ✅ Integração
- [ ] Adicionar ao repositório
- [ ] Atualizar método de busca
- [ ] Testar com `python main.py --search`
- [ ] Verificar logs de debug
- [ ] Validar filtro de relevância

### ✅ Testes
- [ ] Testar com diferentes termos de busca
- [ ] Verificar tratamento de erros
- [ ] Testar timeout e rate limiting
- [ ] Validar extração de conteúdo completo

## Dicas e Boas Práticas

### 1. Seletores CSS Robustos

```python
# ❌ Evitar seletores muito específicos
'.css-1234567-ArticleTitle'

# ✅ Preferir seletores semânticos
'article h2', '.article-title', '[data-testid="headline"]'

# ✅ Usar múltiplos fallbacks
selectors = [
    '.primary-selector',
    '.fallback-selector', 
    'generic-selector'
]
```

### 2. Tratamento de URLs

```python
# Sempre normalizar URLs
url = link_elem.get('href', '')
if url.startswith('/'):
    url = urljoin(self.base_url, url)
elif url.startswith('//'):
    url = f"https:{url}"
```

### 3. Headers Apropriados

```python
# Simular navegador real
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'pt-BR,pt;q=0.9,en;q=0.8',
    'Accept-Encoding': 'gzip, deflate',
    'Connection': 'keep-alive',
}
```

### 4. Rate Limiting

```python
# Adicionar pausas entre requisições
await asyncio.sleep(1)  # 1 segundo entre artigos

# Respeitar robots.txt
# Implementar backoff exponencial em caso de erro 429
```

### 5. Logs Detalhados

```python
print(f"🔍 Buscando em {self.base_url}")
print(f"📄 Encontrados {len(articles)} artigos")
print(f"✅ {len(relevant_news)} notícias relevantes")
print(f"⏱️ Processamento concluído em {elapsed_time:.2f}s")
```

## Troubleshooting

### Problema: Seletores não funcionam
**Solução**: Verificar se o site usa JavaScript para carregar conteúdo

### Problema: Muitos falsos positivos
**Solução**: Refinar filtros de relevância ou seletores

### Problema: Rate limiting
**Solução**: Aumentar pausas entre requisições

### Problema: Conteúdo não encontrado
**Solução**: Verificar se URLs estão sendo construídas corretamente

## Exemplo Completo

Veja o arquivo `src/infrastructure/web_scraping/bbc_scraper.py` como referência completa de implementação.

## Próximos Passos

1. **Implementar scrapers para sites populares**:
   - CNN, Reuters, Associated Press
   - Sites de entretenimento (Variety, Hollywood Reporter)
   - Sites brasileiros (G1, UOL, Folha)

2. **Melhorar robustez**:
   - Cache de resultados
   - Retry automático
   - Detecção de mudanças na estrutura

3. **Adicionar funcionalidades**:
   - Suporte a RSS feeds
   - APIs oficiais quando disponíveis
   - Processamento de imagens