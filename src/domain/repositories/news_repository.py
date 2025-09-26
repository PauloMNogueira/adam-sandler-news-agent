from abc import ABC, abstractmethod
from typing import List, Optional
from datetime import datetime
from ..entities.news import News
from ..entities.news_source import NewsSource


class NewsRepository(ABC):
    """Interface para repositório de notícias."""
    
    @abstractmethod
    async def fetch_news_from_source(self, source: NewsSource, query: str) -> List[News]:
        """Busca notícias de uma fonte específica."""
        pass
    
    @abstractmethod
    async def save_news(self, news: News) -> None:
        """Salva uma notícia."""
        pass
    
    @abstractmethod
    async def save_multiple_news(self, news_list: List[News]) -> None:
        """Salva múltiplas notícias."""
        pass
    
    @abstractmethod
    async def get_news_by_date_range(self, start_date: datetime, end_date: datetime) -> List[News]:
        """Busca notícias por intervalo de datas."""
        pass
    
    @abstractmethod
    async def get_news_by_source(self, source_name: str) -> List[News]:
        """Busca notícias por fonte."""
        pass
    
    @abstractmethod
    async def search_news(self, query: str) -> List[News]:
        """Busca notícias por termo de pesquisa."""
        pass
    
    @abstractmethod
    async def get_latest_news(self, limit: int = 10) -> List[News]:
        """Busca as notícias mais recentes."""
        pass