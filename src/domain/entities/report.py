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
        body {{ font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }}
        .header {{ background-color: #2c3e50; color: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; }}
        .summary {{ background-color: white; padding: 15px; border-radius: 8px; margin-bottom: 20px; border-left: 4px solid #3498db; }}
        .sources-summary {{ background-color: white; padding: 15px; border-radius: 8px; margin-bottom: 20px; }}
        .news-item {{ background-color: white; margin-bottom: 20px; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        .news-title {{ font-size: 18px; font-weight: bold; color: #2c3e50; margin-bottom: 10px; }}
        .news-meta {{ color: #7f8c8d; font-size: 14px; margin-bottom: 15px; }}
        .news-meta a {{ color: #3498db; text-decoration: none; }}
        .news-meta a:hover {{ text-decoration: underline; }}
        .news-summary {{ line-height: 1.6; color: #34495e; }}
        .ai-analysis {{ margin-top: 20px; padding: 15px; background-color: #f8f9fa; border-radius: 6px; border-left: 4px solid #e74c3c; }}
        .ai-analysis h4 {{ margin: 0 0 10px 0; color: #e74c3c; font-size: 16px; }}
        .analysis-content {{ line-height: 1.6; color: #2c3e50; }}
        .analysis-content h3 {{ color: #e74c3c; margin-top: 15px; margin-bottom: 8px; }}
        .analysis-content p {{ margin-bottom: 10px; }}
        .analysis-content strong {{ color: #2c3e50; }}
        ul {{ margin: 10px 0; }}
        li {{ margin-bottom: 5px; }}
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
        <div class="news-summary">{news.generate_summary()}</div>"""
            
            # Adicionar análise de IA se disponível
            if news.has_ai_analysis():
                html += f"""
        <div class="ai-analysis">
            <h4>🤖 Análise Inteligente:</h4>
            <div class="analysis-content">
                {news.get_ai_analysis_text()}
            </div>
        </div>"""
            
            html += """
    </div>
"""
        
        html += """
</body>
</html>
"""
        return html