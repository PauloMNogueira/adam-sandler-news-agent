import asyncio
import aiohttp
from typing import List, Optional
from datetime import datetime

from ...domain.repositories.news_repository import NewsRepository
from ...domain.entities.news import News
from ...domain.entities.news_source import NewsSource, SourceType
from .bbc_scraper import BBCScraper


class WebScrapingNewsRepository(NewsRepository):
    """Implementação do repositório de notícias usando web scraping."""
    
    def __init__(self):
        self.scrapers = {
            "BBC News": BBCScraper()
        }
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Obtém ou cria uma sessão HTTP."""
        if self.session is None or self.session.closed:
            timeout = aiohttp.ClientTimeout(total=60)
            self.session = aiohttp.ClientSession(timeout=timeout)
        return self.session
    
    async def close_session(self):
        """Fecha a sessão HTTP."""
        if self.session and not self.session.closed:
            await self.session.close()
    
    async def fetch_news_from_source(self, source: NewsSource, query: str) -> List[News]:
        """Busca notícias de uma fonte específica."""
        if source.source_type != SourceType.WEB_SCRAPING:
            raise ValueError(f"Fonte {source.name} não é compatível com web scraping")
        
        scraper = self.scrapers.get(source.name)
        if not scraper:
            raise ValueError(f"Scraper não encontrado para a fonte: {source.name}")
        
        session = await self._get_session()
        max_results = source.get_config_value("max_results", 10)
        
        try:
            if source.name == "BBC News":
                return await scraper.search_adam_sandler_news(session, max_results)
            else:
                return []
        except Exception as e:
            print(f"Erro ao buscar notícias de {source.name}: {str(e)}")
            return []
    
    async def save_news(self, news: News) -> None:
        """Salva uma notícia (implementação simples em memória)."""
        # Em uma implementação real, salvaria em banco de dados
        print(f"Notícia salva: {news.title}")
    
    async def save_multiple_news(self, news_list: List[News]) -> None:
        """Salva múltiplas notícias."""
        for news in news_list:
            await self.save_news(news)
    
    async def get_news_by_date_range(self, start_date: datetime, end_date: datetime) -> List[News]:
        """Busca notícias por intervalo de datas."""
        # Implementação simplificada - em produção buscaria do banco de dados
        return []
    
    async def get_news_by_source(self, source_name: str) -> List[News]:
        """Busca notícias por fonte."""
        # Implementação simplificada - em produção buscaria do banco de dados
        return []
    
    async def search_news(self, query: str) -> List[News]:
        """Busca notícias por termo de pesquisa."""
        all_news = []
        
        # Buscar em todas as fontes disponíveis
        for source_name, scraper in self.scrapers.items():
            try:
                source = scraper.get_news_source()
                
                news_list = await self.fetch_news_from_source(source, query)
                all_news.extend(news_list)
            except Exception as e:
                print(f"Erro ao buscar em {source_name}: {str(e)}")
                continue
        
        return all_news
    
    async def get_latest_news(self, limit: int = 10) -> List[News]:
        """Busca as notícias mais recentes sobre Adam Sandler."""
        return await self.search_news("Adam Sandler")
    
    async def fetch_all_adam_sandler_news(self) -> List[News]:
        """Busca todas as notícias sobre Adam Sandler de todas as fontes."""
        all_news = []
        session = await self._get_session()
        
        try:
            # Buscar em todas as fontes configuradas
            for source_name, scraper in self.scrapers.items():
                try:
                    print(f"Buscando notícias em {source_name}...")
                    source = scraper.get_news_source()
                    news_list = await self.fetch_news_from_source(source, "Adam Sandler")
                    
                    print(f"Encontradas {len(news_list)} notícias em {source_name}")
                    all_news.extend(news_list)
                    
                    # Pequena pausa entre requisições para ser respeitoso
                    await asyncio.sleep(1)
                    
                except Exception as e:
                    print(f"Erro ao buscar notícias em {source_name}: {str(e)}")
                    continue
            
            # Remover duplicatas baseado na URL
            unique_news = []
            seen_urls = set()
            
            for news in all_news:
                if news.url not in seen_urls:
                    unique_news.append(news)
                    seen_urls.add(news.url)
            
            print(f"Total de notícias únicas encontradas: {len(unique_news)}")
            return unique_news
            
        finally:
            # Não fechar a sessão aqui, deixar para o contexto principal
            pass
    
    def add_scraper(self, source_name: str, scraper):
        """Adiciona um novo scraper para uma fonte."""
        self.scrapers[source_name] = scraper
        print(f"Scraper adicionado para {source_name}")
    
    def get_available_sources(self) -> List[str]:
        """Retorna lista de fontes disponíveis."""
        return list(self.scrapers.keys())