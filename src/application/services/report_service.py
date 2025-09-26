from datetime import datetime
from typing import List, Optional
import asyncio

from ...domain.entities.news import News
from ...domain.entities.report import Report
from ...domain.repositories.news_repository import NewsRepository
from ...domain.repositories.email_repository import EmailRepository


class ReportService:
    """Serviço responsável pela geração e envio de relatórios."""
    
    def __init__(self, news_repository: NewsRepository, email_repository: EmailRepository):
        self.news_repository = news_repository
        self.email_repository = email_repository
    
    async def generate_adam_sandler_report(self, title: Optional[str] = None) -> Report:
        """Gera um relatório completo sobre Adam Sandler."""
        if title is None:
            title = f"Relatório de Notícias sobre Adam Sandler - {datetime.now().strftime('%d/%m/%Y')}"
        
        print("Iniciando geração do relatório...")
        
        # Buscar todas as notícias sobre Adam Sandler
        news_list = await self.news_repository.fetch_all_adam_sandler_news()
        
        # Filtrar apenas notícias relevantes
        relevant_news = [news for news in news_list if news.is_relevant_to_adam_sandler()]
        
        # Criar relatório
        report = Report(
            title=title,
            generated_at=datetime.now()
        )
        
        # Adicionar notícias ao relatório
        report.add_multiple_news(relevant_news)
        
        # Gerar resumo
        report.summary = report.generate_summary()
        
        # Adicionar metadados
        report.metadata = {
            "total_sources_consulted": len(self.news_repository.get_available_sources()),
            "total_news_found": len(news_list),
            "relevant_news_count": len(relevant_news),
            "generation_time": datetime.now().isoformat(),
            "sources_summary": report.get_sources_summary()
        }
        
        print(f"Relatório gerado com {len(relevant_news)} notícias relevantes")
        return report
    
    async def generate_adam_sandler_report_from_news(self, news_list: List[News], title: Optional[str] = None) -> Report:
        """Gera um relatório a partir de uma lista de notícias já processadas."""
        if title is None:
            title = f"Relatório de Notícias sobre Adam Sandler - {datetime.now().strftime('%d/%m/%Y')}"
        
        print("Gerando relatório a partir de notícias processadas...")
        
        # Criar relatório
        report = Report(
            title=title,
            generated_at=datetime.now()
        )
        
        # Adicionar notícias ao relatório
        report.add_multiple_news(news_list)
        
        # Gerar resumo
        report.summary = report.generate_summary()
        
        # Adicionar metadados
        report.metadata = {
            "total_sources_consulted": len(self.news_repository.get_available_sources()),
            "total_news_found": len(news_list),
            "relevant_news_count": len(news_list),
            "generation_time": datetime.now().isoformat(),
            "sources_summary": report.get_sources_summary()
        }
        
        print(f"Relatório gerado com {len(news_list)} notícias")
        return report
    
    async def generate_and_send_report(self, recipient_email: str, 
                                     title: Optional[str] = None,
                                     send_html: bool = True) -> bool:
        """Gera um relatório e envia por e-mail."""
        try:
            # Validar e-mail
            if not self.email_repository.validate_email(recipient_email):
                raise ValueError(f"E-mail inválido: {recipient_email}")
            
            print(f"Gerando relatório para envio para {recipient_email}...")
            
            # Gerar relatório
            report = await self.generate_adam_sandler_report(title)
            
            # Enviar por e-mail
            if send_html:
                success = await self.email_repository.send_html_report(report, recipient_email)
            else:
                success = await self.email_repository.send_report(report, recipient_email)
            
            if success:
                print(f"Relatório enviado com sucesso para {recipient_email}")
            else:
                print(f"Falha ao enviar relatório para {recipient_email}")
            
            return success
            
        except Exception as e:
            print(f"Erro ao gerar e enviar relatório: {str(e)}")
            return False
    
    async def generate_html_report(self, report: Report) -> str:
        """Gera o HTML do relatório."""
        return report.to_html()
    
    async def generate_daily_report(self) -> Report:
        """Gera um relatório diário sobre Adam Sandler."""
        title = f"Relatório Diário - Adam Sandler - {datetime.now().strftime('%d/%m/%Y')}"
        return await self.generate_adam_sandler_report(title)
    
    async def generate_weekly_report(self) -> Report:
        """Gera um relatório semanal sobre Adam Sandler."""
        title = f"Relatório Semanal - Adam Sandler - Semana de {datetime.now().strftime('%d/%m/%Y')}"
        return await self.generate_adam_sandler_report(title)
    
    async def send_test_report(self, recipient_email: str) -> bool:
        """Envia um relatório de teste."""
        try:
            print(f"Enviando relatório de teste para {recipient_email}...")
            
            # Criar notícia de teste
            test_news = News(
                title="Teste - Adam Sandler anuncia novo projeto",
                content="Esta é uma notícia de teste para verificar o funcionamento do sistema de relatórios do Adam Sandler News Agent.",
                url="https://example.com/test-news",
                source="Sistema de Teste",
                published_date=datetime.now(),
                author="Sistema Automatizado"
            )
            
            # Criar relatório de teste
            test_report = Report(
                title=f"Relatório de Teste - Adam Sandler News Agent - {datetime.now().strftime('%d/%m/%Y às %H:%M')}",
                generated_at=datetime.now()
            )
            
            test_report.add_news(test_news)
            test_report.summary = test_report.generate_summary()
            test_report.metadata = {
                "is_test": True,
                "test_timestamp": datetime.now().isoformat(),
                "system_status": "operational"
            }
            
            # Enviar relatório de teste
            success = await self.email_repository.send_html_report(
                test_report, 
                recipient_email,
                "Teste - Adam Sandler News Agent"
            )
            
            if success:
                print("Relatório de teste enviado com sucesso!")
            else:
                print("Falha ao enviar relatório de teste")
            
            return success
            
        except Exception as e:
            print(f"Erro ao enviar relatório de teste: {str(e)}")
            return False
    
    async def get_report_statistics(self) -> dict:
        """Obtém estatísticas sobre os relatórios."""
        try:
            # Buscar notícias para estatísticas
            news_list = await self.news_repository.get_latest_news(50)
            
            sources = {}
            for news in news_list:
                sources[news.source] = sources.get(news.source, 0) + 1
            
            return {
                "total_news_available": len(news_list),
                "sources_count": len(sources),
                "sources_breakdown": sources,
                "last_update": datetime.now().isoformat(),
                "available_sources": self.news_repository.get_available_sources()
            }
            
        except Exception as e:
            print(f"Erro ao obter estatísticas: {str(e)}")
            return {
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def save_report_to_file(self, report: Report, file_path: str, 
                                 format_type: str = "html") -> bool:
        """Salva um relatório em arquivo."""
        try:
            if format_type.lower() == "html":
                content = report.to_html()
                file_path = file_path if file_path.endswith('.html') else f"{file_path}.html"
            else:
                content = report.generate_summary()
                file_path = file_path if file_path.endswith('.txt') else f"{file_path}.txt"
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"Relatório salvo em: {file_path}")
            return True
            
        except Exception as e:
            print(f"Erro ao salvar relatório: {str(e)}")
            return False