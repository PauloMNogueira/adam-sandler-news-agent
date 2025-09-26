from typing import List, Optional
from datetime import datetime
import asyncio

from ...domain.entities.news import News
from ...domain.entities.report import Report
from ...domain.repositories.news_repository import NewsRepository
from ...domain.repositories.email_repository import EmailRepository
from ..services.report_service import ReportService


class NewsAggregatorUseCase:
    """Caso de uso principal para agregação de notícias sobre Adam Sandler."""
    
    def __init__(self, news_repository: NewsRepository, email_repository: EmailRepository):
        self.news_repository = news_repository
        self.email_repository = email_repository
        self.report_service = ReportService(news_repository, email_repository)
    
    async def execute_daily_news_report(self, recipient_email: str) -> bool:
        """Executa o processo completo de busca e envio de relatório diário."""
        try:
            print("=== ADAM SANDLER NEWS AGENT ===")
            print("Iniciando processo de agregação de notícias...")
            print(f"Destinatário: {recipient_email}")
            print(f"Data/Hora: {datetime.now().strftime('%d/%m/%Y às %H:%M')}")
            print("-" * 50)
            
            # Validar e-mail
            if not self.email_repository.validate_email(recipient_email):
                print(f"❌ E-mail inválido: {recipient_email}")
                return False
            
            # Gerar e enviar relatório
            success = await self.report_service.generate_and_send_report(
                recipient_email=recipient_email,
                title=f"Relatório Diário - Adam Sandler - {datetime.now().strftime('%d/%m/%Y')}",
                send_html=True
            )
            
            if success:
                print("✅ Processo concluído com sucesso!")
                print(f"📧 Relatório enviado para {recipient_email}")
            else:
                print("❌ Falha no processo de envio do relatório")
            
            print("-" * 50)
            return success
            
        except Exception as e:
            print(f"❌ Erro no processo de agregação: {str(e)}")
            return False
        finally:
            # Fechar sessão HTTP se existir
            if hasattr(self.news_repository, 'close_session'):
                await self.news_repository.close_session()
    
    async def execute_news_search_only(self) -> List[News]:
        """Executa apenas a busca de notícias sem enviar relatório."""
        try:
            print("=== BUSCA DE NOTÍCIAS SOBRE ADAM SANDLER ===")
            print(f"Iniciando busca em {datetime.now().strftime('%d/%m/%Y às %H:%M')}")
            print("-" * 50)
            
            # Buscar notícias
            news_list = await self.news_repository.fetch_all_adam_sandler_news()
            
            # Filtrar notícias relevantes
            relevant_news = [news for news in news_list if news.is_relevant_to_adam_sandler()]
            
            print(f"📰 Total de notícias encontradas: {len(news_list)}")
            print(f"✅ Notícias relevantes: {len(relevant_news)}")
            
            # Mostrar resumo das fontes
            sources = {}
            for news in relevant_news:
                sources[news.source] = sources.get(news.source, 0) + 1
            
            print("\n📊 Resumo por fonte:")
            for source, count in sources.items():
                print(f"  • {source}: {count} notícias")
            
            print("-" * 50)
            return relevant_news
            
        except Exception as e:
            print(f"❌ Erro na busca de notícias: {str(e)}")
            return []
        finally:
            # Fechar sessão HTTP se existir
            if hasattr(self.news_repository, 'close_session'):
                await self.news_repository.close_session()
    
    async def execute_test_workflow(self, recipient_email: str) -> bool:
        """Executa um fluxo de teste completo."""
        try:
            print("=== TESTE DO ADAM SANDLER NEWS AGENT ===")
            print(f"Testando envio para: {recipient_email}")
            print(f"Data/Hora: {datetime.now().strftime('%d/%m/%Y às %H:%M')}")
            print("-" * 50)
            
            # Testar conexão de e-mail
            print("🔧 Testando conexão SMTP...")
            if hasattr(self.email_repository, 'test_connection'):
                if not self.email_repository.test_connection():
                    print("❌ Falha na conexão SMTP")
                    return False
                print("✅ Conexão SMTP OK")
            
            # Enviar e-mail de teste
            print("📧 Enviando e-mail de teste...")
            success = await self.report_service.send_test_report(recipient_email)
            
            if success:
                print("✅ Teste concluído com sucesso!")
                print(f"📧 E-mail de teste enviado para {recipient_email}")
            else:
                print("❌ Falha no envio do e-mail de teste")
            
            print("-" * 50)
            return success
            
        except Exception as e:
            print(f"❌ Erro no teste: {str(e)}")
            return False
    
    async def execute_report_generation_only(self, save_to_file: Optional[str] = None) -> Optional[Report]:
        """Executa apenas a geração do relatório sem enviar por e-mail."""
        try:
            print("=== GERAÇÃO DE RELATÓRIO ===")
            print(f"Iniciando em {datetime.now().strftime('%d/%m/%Y às %H:%M')}")
            print("-" * 50)
            
            # Gerar relatório
            report = await self.report_service.generate_adam_sandler_report()
            
            print(f"📊 Relatório gerado:")
            print(f"  • Título: {report.title}")
            print(f"  • Notícias encontradas: {report.get_news_count()}")
            print(f"  • Fontes consultadas: {len(report.get_sources_summary())}")
            
            # Salvar em arquivo se solicitado
            if save_to_file:
                success = await self.report_service.save_report_to_file(report, save_to_file, "html")
                if success:
                    print(f"💾 Relatório salvo em: {save_to_file}")
                else:
                    print("❌ Falha ao salvar relatório")
            
            print("-" * 50)
            return report
            
        except Exception as e:
            print(f"❌ Erro na geração do relatório: {str(e)}")
            return None
        finally:
            # Fechar sessão HTTP se existir
            if hasattr(self.news_repository, 'close_session'):
                await self.news_repository.close_session()
    
    async def get_system_status(self) -> dict:
        """Obtém o status do sistema."""
        try:
            # Obter estatísticas
            stats = await self.report_service.get_report_statistics()
            
            # Testar conexões
            email_status = "unknown"
            if hasattr(self.email_repository, 'test_connection'):
                email_status = "ok" if self.email_repository.test_connection() else "error"
            
            return {
                "timestamp": datetime.now().isoformat(),
                "status": "operational",
                "email_service": email_status,
                "available_sources": self.news_repository.get_available_sources(),
                "statistics": stats
            }
            
        except Exception as e:
            return {
                "timestamp": datetime.now().isoformat(),
                "status": "error",
                "error": str(e)
            }