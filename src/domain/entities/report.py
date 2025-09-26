from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Any
from .news import News


@dataclass
class Report:
    """Entidade que representa um relatório de notícias sobre Adam Sandler."""
    
    title: str
    generated_at: datetime
    news_list: List[News] = field(default_factory=list)
    summary: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Validações da entidade."""
        if not self.title.strip():
            raise ValueError("Título do relatório não pode estar vazio")
    
    def add_news(self, news: News) -> None:
        """Adiciona uma notícia ao relatório."""
        if news not in self.news_list:
            self.news_list.append(news)
    
    def add_multiple_news(self, news_list: List[News]) -> None:
        """Adiciona múltiplas notícias ao relatório."""
        for news in news_list:
            self.add_news(news)
    
    def get_news_count(self) -> int:
        """Retorna o número de notícias no relatório."""
        return len(self.news_list)
    
    def get_sources_summary(self) -> Dict[str, int]:
        """Retorna um resumo das fontes das notícias."""
        sources = {}
        for news in self.news_list:
            sources[news.source] = sources.get(news.source, 0) + 1
        return sources
    
    def generate_summary(self) -> str:
        """Gera um resumo do relatório."""
        if not self.news_list:
            return "Nenhuma notícia encontrada sobre Adam Sandler."
        
        total_news = len(self.news_list)
        sources = self.get_sources_summary()
        sources_text = ", ".join([f"{source}: {count}" for source, count in sources.items()])
        
        summary = f"""
Relatório de Notícias sobre Adam Sandler
Gerado em: {self.generated_at.strftime('%d/%m/%Y às %H:%M')}

Total de notícias encontradas: {total_news}
Fontes consultadas: {sources_text}

Principais notícias:
"""
        
        # Adiciona as 5 primeiras notícias
        for i, news in enumerate(self.news_list[:5], 1):
            summary += f"\n{i}. {news.title}"
            summary += f"\n   Fonte: {news.source}"
            summary += f"\n   Data: {news.published_date.strftime('%d/%m/%Y')}"
            summary += f"\n   URL: {news.url}\n"
        
        if total_news > 5:
            summary += f"\n... e mais {total_news - 5} notícias."
        
        return summary
    
    def to_html(self) -> str:
        """Converte o relatório para HTML."""
        html = f"""
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{self.title}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; }}
        .header {{ background-color: #f4f4f4; padding: 20px; border-radius: 5px; }}
        .news-item {{ border-bottom: 1px solid #eee; padding: 20px 0; }}
        .news-title {{ font-size: 18px; font-weight: bold; color: #333; }}
        .news-meta {{ color: #666; font-size: 14px; margin: 5px 0; }}
        .news-summary {{ margin: 10px 0; }}
        .sources-summary {{ background-color: #e8f4f8; padding: 15px; border-radius: 5px; margin: 20px 0; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>{self.title}</h1>
        <p>Gerado em: {self.generated_at.strftime('%d/%m/%Y às %H:%M')}</p>
        <p>Total de notícias: {len(self.news_list)}</p>
    </div>
    
    <div class="sources-summary">
        <h3>Resumo das Fontes:</h3>
        <ul>
"""
        
        for source, count in self.get_sources_summary().items():
            html += f"            <li>{source}: {count} notícias</li>\n"
        
        html += """        </ul>
    </div>
    
    <h2>Notícias Encontradas:</h2>
"""
        
        for news in self.news_list:
            html += f"""
    <div class="news-item">
        <div class="news-title">{news.title}</div>
        <div class="news-meta">
            Fonte: {news.source} | 
            Data: {news.published_date.strftime('%d/%m/%Y')} |
            <a href="{news.url}" target="_blank">Ver notícia completa</a>
        </div>
        <div class="news-summary">{news.generate_summary()}</div>
    </div>
"""
        
        html += """
</body>
</html>
"""
        return html