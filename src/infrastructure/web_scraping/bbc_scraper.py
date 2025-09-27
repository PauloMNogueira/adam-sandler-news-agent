import asyncio
import aiohttp
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from typing import List, Optional
import re
from urllib.parse import urljoin, quote

from ...domain.entities.news import News
from ...domain.entities.news_source import NewsSource, SourceType


class BBCScraper:
    """Scraper específico para BBC News."""
    
    def __init__(self):
        self.base_url = "https://www.bbc.com"
        self.search_url = "https://www.bbc.com/search"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
    
    def get_news_source(self) -> NewsSource:
        """Retorna a configuração da fonte BBC News."""
        
        return NewsSource(
            name="BBC News",
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
        """Busca notícias sobre Adam Sandler na BBC."""
        
        query = "Adam Sandler"
        
        try:
            url = f"{self.search_url}?q={quote(query)}"
            print(f"URL de busca: {url}")
            
            async with session.get(url, headers=self.headers, timeout=30) as response:
                
                if response.status != 200:
                    print(f"Erro ao acessar BBC: Status {response.status}")
                    return []
                
                html = await response.text()
               
                return await self._parse_search_results(html, max_results, session)
                
        except asyncio.TimeoutError:
            print("Timeout ao acessar BBC News")
            return []
        except Exception as e:
            print(f"Erro ao buscar notícias na BBC: {str(e)}")
            return []
    
    async def _parse_search_results(self, html: str, max_results: int, session: aiohttp.ClientSession) -> List[News]:
        """Analisa os resultados de busca da BBC."""
        soup = BeautifulSoup(html, 'html.parser')
        news_list = []
        
        # BBC usa diferentes seletores dependendo da versão da página
        # Vamos tentar múltiplos seletores
        selectors = [
            '[data-testid="newport-card"]',
            'div[data-testid="search-results"] article',
            '.ssrcss-1f3bvyz-Stack',
            'article',
            '.media__content'
        ]
        
        articles = []
        for selector in selectors:
            articles = soup.select(selector)
            if articles:
                break
        
        if not articles:
            print("Nenhum artigo encontrado com os seletores principais")
            # Fallback: buscar por links que contenham palavras-chave
            links = soup.find_all('a', href=True)
            print(f"Tentando fallback com links: encontrados {len(links)} links")
            for link in links[:max_results]:
                href = link.get('href', '')
                text = link.get_text(strip=True)
                
                if self._is_relevant_link(text, href):
                    news = self._create_news_from_link(link)
                    if news:
                        # Tentar buscar conteúdo completo
                        full_content = await self.get_article_content(session, news.url)
                        if full_content:
                            news.content = full_content
                        news_list.append(news)
            
            print(f"Fallback retornou {len(news_list)} notícias")
            return news_list[:max_results]
        
        for article in articles[:max_results]:
            try:
                print(f"Processando artigo: {article}")
                news = self._extract_news_from_article(article)
                if news:
                    print(f"Notícia extraída: '{news.title}' - URL: {news.url}")

                    full_content = await self.get_article_content(session, news.url)
                    if full_content and len(full_content) > len(news.content):
                        print(f"✅ Conteúdo completo encontrado ({len(full_content)} caracteres)")
                        news.content = full_content
                    else:
                        print(f"⚠️ Usando conteúdo básico ({len(news.content)} caracteres)")
                    
                    if news.is_relevant_to_adam_sandler():
                        print(f"✅ Notícia relevante: {news.title}")
                        news_list.append(news)
                    else:
                        print(f"❌ Notícia não relevante: {news.title}")
                else:
                    print("❌ Falha ao extrair notícia do artigo")
            except Exception as e:
                print(f"Erro ao extrair notícia: {str(e)}")
                continue
        
        return news_list[:max_results]
    
    def _extract_news_from_article(self, article) -> Optional[News]:
        """Extrai informações de uma notícia de um elemento article."""
        try:
            # Tentar diferentes seletores para título
            title_selectors = ['h3', 'h2', 'h1', '.media__title', '[data-testid="card-headline"]']
            title = ""
            
            for selector in title_selectors:
                title_elem = article.select_one(selector)
                if title_elem:
                    title = title_elem.get_text(strip=True)
                    break
            
            if not title:
                return None
            
            # Tentar encontrar link
            link_elem = article.find('a', href=True)
            if not link_elem:
                return None
            
            url = link_elem.get('href', '')
            if url.startswith('/'):
                url = urljoin(self.base_url, url)
            
            # Tentar encontrar resumo/conteúdo básico primeiro
            content_selectors = [
                '[data-component="text-block"]',
                '[data-testid="card-description"]',
                '.media__summary', 
                'p', 
                '.ssrcss-1q0x1qg-Paragraph',
                '[data-testid="card-text"]'
            ]
            content = ""
            
            for selector in content_selectors:
                content_elem = article.select_one(selector)
                
                if content_elem:
                    content = content_elem.get_text(strip=True)
                    if content and len(content) > 10:  # Só aceitar se tiver conteúdo substancial
                        break
            
            if not content or len(content) <= 10:
                content = title  # Usar título como conteúdo se não encontrar resumo
            
            # Tentar extrair data de publicação
            published_date = self._extract_published_date(article)
            
            # Criar notícia inicial
            news = News(
                title=title,
                content=content,
                url=url,
                source="BBC News",
                published_date=published_date,
                author=None
            )
            
            return news
            
        except Exception as e:
            print(f"Erro ao extrair notícia do artigo: {str(e)}")
            return None
    
    def _create_news_from_link(self, link) -> Optional[News]:
        """Cria uma notícia a partir de um link relevante."""
        try:
            title = link.get_text(strip=True)
            if not title or len(title) < 10:
                return None
            
            href = link.get('href', '')
            if href.startswith('/'):
                url = urljoin(self.base_url, href)
            else:
                url = href
            
            return News(
                title=title,
                content=title,  # Usar título como conteúdo inicial
                url=url,
                source="BBC News",
                published_date=datetime.now(),
                author=None
            )
            
        except Exception as e:
            print(f"Erro ao criar notícia do link: {str(e)}")
            return None
    
    def _is_relevant_link(self, text: str, href: str) -> bool:
        """Verifica se um link é relevante para Adam Sandler."""
        text_lower = text.lower()
        href_lower = href.lower()
        
        keywords = ["adam sandler", "sandler", "comedy", "netflix", "movie", "film"]
        
        return any(keyword in text_lower or keyword in href_lower for keyword in keywords)
    
    async def get_article_content(self, session: aiohttp.ClientSession, url: str) -> Optional[str]:
        """Busca o conteúdo completo de um artigo."""
        try:
            async with session.get(url, headers=self.headers, timeout=30) as response:
                if response.status != 200:
                    return None
                
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                
                # Seletores para conteúdo do artigo da BBC
                content_selectors = [
                    '[data-component="text-block"]',
                    '.ssrcss-11r1m41-RichTextComponentWrapper',
                    'div[data-component="text-block"] p',
                    '.story-body__inner p'
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
    
    def _extract_published_date(self, article) -> datetime:
        """Extrai a data de publicação do elemento span com data-testid ou usa data atual como fallback."""
        try:
            # Procurar elemento span com data-testid="card-metadata-lastupdated"
            date_elem = article.find('span', {'data-testid': 'card-metadata-lastupdated'})
            
            if date_elem:
                date_text = date_elem.get_text(strip=True)
                print(f"Data encontrada no span: {date_text}")
                
                if date_text:
                    # Tentar parsear diferentes formatos de data da BBC
                    try:
                        # Formato: "22 Aug 2017"
                        return datetime.strptime(date_text, "%d %b %Y")
                    except ValueError:
                        try:
                            # Formato: "22 August 2017"
                            return datetime.strptime(date_text, "%d %B %Y")
                        except ValueError:
                            print(f"Erro ao parsear data: {date_text}")
            
            # Também tentar procurar elemento time como fallback
            time_elem = article.find('time', {'datetime': True})
            if time_elem:
                datetime_str = time_elem.get('datetime')
                if datetime_str:
                    try:
                        # Formato ISO com Z (UTC)
                        if datetime_str.endswith('Z'):
                            return datetime.fromisoformat(datetime_str.replace('Z', '+00:00'))
                        # Formato ISO com timezone
                        elif '+' in datetime_str or datetime_str.endswith('T'):
                            return datetime.fromisoformat(datetime_str)
                        else:
                            return datetime.fromisoformat(datetime_str)
                    except ValueError:
                        print(f"Erro ao parsear datetime: {datetime_str}")
            
            # Fallback: usar data atual se não conseguir extrair
            print("Nenhum elemento de data encontrado. Usando data atual.")
            return datetime.now()
            
        except Exception as e:
            print(f"Erro ao extrair data de publicação: {str(e)}")
            return datetime.now()