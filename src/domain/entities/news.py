from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class News:
    """Entidade que representa uma notícia sobre Adam Sandler."""
    
    title: str
    content: str
    url: str
    source: str
    published_date: datetime
    author: Optional[str] = None
    summary: Optional[str] = None
    
    def __post_init__(self):
        """Validações da entidade."""
        if not self.title.strip():
            raise ValueError("Título da notícia não pode estar vazio")
        
        if not self.content.strip():
            raise ValueError("Conteúdo da notícia não pode estar vazio")
        
        if not self.url.strip():
            raise ValueError("URL da notícia não pode estar vazia")
        
        if not self.source.strip():
            raise ValueError("Fonte da notícia não pode estar vazia")
    
    def is_relevant_to_adam_sandler(self) -> bool:
        """Verifica se a notícia é relevante para Adam Sandler."""
        keywords = ["adam sandler", "sandler", "happy madison", "netflix", "comedy"]
        text_to_search = f"{self.title} {self.content}".lower()
        
        return any(keyword in text_to_search for keyword in keywords)
        # return True
    
    def generate_summary(self, max_length: int = 200) -> str:
        """Gera um resumo da notícia."""
        if len(self.content) <= max_length:
            return self.content
        
        # Pega as primeiras frases até o limite
        sentences = self.content.split('. ')
        summary = ""
        
        for sentence in sentences:
            if len(summary + sentence) <= max_length:
                summary += sentence + ". "
            else:
                break
        
        return summary.strip()