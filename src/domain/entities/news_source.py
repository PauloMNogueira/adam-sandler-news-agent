from dataclasses import dataclass
from typing import Dict, Any
from enum import Enum


class SourceType(Enum):
    """Tipos de fonte de notícias."""
    RSS = "rss"
    WEB_SCRAPING = "web_scraping"
    API = "api"


@dataclass
class NewsSource:
    """Entidade que representa uma fonte de notícias."""
    
    name: str
    base_url: str
    source_type: SourceType
    search_endpoint: str
    is_active: bool = True
    config: Dict[str, Any] = None
    
    def __post_init__(self):
        """Validações da entidade."""
        if not self.name.strip():
            raise ValueError("Nome da fonte não pode estar vazio")
        
        if not self.base_url.strip():
            raise ValueError("URL base da fonte não pode estar vazia")
        
        if not self.search_endpoint.strip():
            raise ValueError("Endpoint de busca não pode estar vazio")
        
        if self.config is None:
            self.config = {}
    
    def get_search_url(self, query: str) -> str:
        """Constrói a URL de busca para a query especificada."""
        if self.source_type == SourceType.WEB_SCRAPING:
            return f"{self.base_url}{self.search_endpoint}?q={query}"
        elif self.source_type == SourceType.RSS:
            return f"{self.base_url}{self.search_endpoint}"
        elif self.source_type == SourceType.API:
            return f"{self.base_url}{self.search_endpoint}"
        
        return f"{self.base_url}{self.search_endpoint}"
    
    def get_config_value(self, key: str, default: Any = None) -> Any:
        """Obtém um valor de configuração."""
        return self.config.get(key, default)
    
    def set_config_value(self, key: str, value: Any) -> None:
        """Define um valor de configuração."""
        self.config[key] = value