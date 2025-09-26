#!/usr/bin/env python3
"""
Adam Sandler News Agent - Interface CLI
Agente AI para buscar notícias sobre Adam Sandler e enviar relatórios por e-mail.
"""

import asyncio
import argparse
import sys
import os
from typing import Optional
from datetime import datetime
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Adicionar o diretório src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from src.infrastructure.web_scraping.news_repository_impl import WebScrapingNewsRepository
from src.infrastructure.email.email_repository_impl import SMTPEmailRepository
from src.application.use_cases.news_aggregator_use_case import NewsAggregatorUseCase


class AdamSandlerNewsAgentCLI:
    """Interface CLI para o Adam Sandler News Agent."""
    
    def __init__(self):
        self.news_repository = None
        self.email_repository = None
        self.use_case = None
    
    def setup_repositories(self):
        """Configura os repositórios necessários."""
        try:
            # Configurar repositório de notícias
            self.news_repository = WebScrapingNewsRepository()
            
            # Configurar repositório de e-mail
            self.email_repository = SMTPEmailRepository()
            
            # Configurar caso de uso
            self.use_case = NewsAggregatorUseCase(
                self.news_repository, 
                self.email_repository
            )
            
            return True
            
        except Exception as e:
            print(f"❌ Erro ao configurar repositórios: {str(e)}")
            print("\n💡 Dicas:")
            print("  • Verifique se as variáveis de ambiente estão configuradas")
            print("  • Execute: cp .env.example .env e configure seus dados")
            return False
    
    async def run_daily_report(self, email: str) -> bool:
        """Executa o relatório diário."""
        if not self.setup_repositories():
            return False
        
        return await self.use_case.execute_daily_news_report(email)
    
    async def run_search_only(self) -> bool:
        """Executa apenas a busca de notícias."""
        if not self.setup_repositories():
            return False
        
        news_list = await self.use_case.execute_news_search_only()
        
        if news_list:
            print(f"\n📰 Notícias encontradas ({len(news_list)}):")
            print("=" * 80)
            
            for i, news in enumerate(news_list[:10], 1):  # Mostrar apenas as 10 primeiras
                print(f"\n{i}. {news.title}")
                print(f"   📅 {news.published_date.strftime('%d/%m/%Y')}")
                print(f"   🌐 {news.source}")
                print(f"   🔗 {news.url}")
                print(f"\n   📝 CONTEÚDO COMPLETO:")
                print("   " + "-" * 50)
                # Exibir conteúdo completo com indentação
                content_lines = news.content.split('\n')
                for line in content_lines:
                    if line.strip():  # Só imprimir linhas não vazias
                        print(f"   {line}")
                print("   " + "-" * 50)
            
            if len(news_list) > 10:
                print(f"\n... e mais {len(news_list) - 10} notícias.")
        
        return len(news_list) > 0
    
    async def run_test(self, email: str) -> bool:
        """Executa teste do sistema."""
        if not self.setup_repositories():
            return False
        
        return await self.use_case.execute_test_workflow(email)
    
    async def generate_report_file(self, output_file: str) -> bool:
        """Gera relatório e salva em arquivo."""
        if not self.setup_repositories():
            return False
        
        # Gerar relatório com publicação automática no GitHub Pages
        report = await self.use_case.execute_report_generation_only(
            save_to_file=output_file, 
            publish_to_github=True
        )
        return report is not None
    
    async def show_status(self) -> bool:
        """Mostra status do sistema."""
        if not self.setup_repositories():
            return False
        
        status = await self.use_case.get_system_status()
        
        print("=== STATUS DO SISTEMA ===")
        print(f"⏰ Timestamp: {status.get('timestamp', 'N/A')}")
        print(f"🟢 Status: {status.get('status', 'unknown')}")
        print(f"📧 E-mail: {status.get('email_service', 'unknown')}")
        
        sources = status.get('available_sources', [])
        print(f"🌐 Fontes disponíveis ({len(sources)}):")
        for source in sources:
            print(f"  • {source}")
        
        stats = status.get('statistics', {})
        if stats and 'error' not in stats:
            print(f"\n📊 Estatísticas:")
            print(f"  • Notícias disponíveis: {stats.get('total_news_available', 0)}")
            print(f"  • Fontes ativas: {stats.get('sources_count', 0)}")
        
        return True
    
    def print_banner(self):
        """Imprime o banner do aplicativo."""
        print("=" * 60)
        print("🎬 ADAM SANDLER NEWS AGENT 🎬")
        print("Agente AI para notícias sobre Adam Sandler")
        print(f"Executado em: {datetime.now().strftime('%d/%m/%Y às %H:%M')}")
        print("=" * 60)
    
    def print_help(self):
        """Imprime ajuda personalizada."""
        print("\n🚀 COMO USAR:")
        print("\n1. Configurar variáveis de ambiente:")
        print("   cp .env.example .env")
        print("   # Edite o arquivo .env com suas configurações")
        print("\n2. Executar comandos:")
        print("   python -m src.interfaces.cli.main --email seu@email.com")
        print("   python -m src.interfaces.cli.main --search")
        print("   python -m src.interfaces.cli.main --test seu@email.com")
        print("\n📧 CONFIGURAÇÃO DE E-MAIL:")
        print("   • Gmail: Use senha de app (não a senha normal)")
        print("   • Outlook: Configure SMTP adequadamente")
        print("   • Outros: Verifique configurações SMTP")


def main():
    """Função principal da CLI."""
    parser = argparse.ArgumentParser(
        description="Adam Sandler News Agent - Busca notícias e envia relatórios",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos de uso:
  python -m src.interfaces.cli.main --email usuario@gmail.com
  python -m src.interfaces.cli.main --search
  python -m src.interfaces.cli.main --test usuario@gmail.com
  python -m src.interfaces.cli.main --generate-file relatorio.html
  python -m src.interfaces.cli.main --status
        """
    )
    
    parser.add_argument(
        '--email', '-e',
        type=str,
        help='E-mail para envio do relatório'
    )
    
    parser.add_argument(
        '--search', '-s',
        action='store_true',
        help='Apenas buscar notícias (não enviar e-mail)'
    )
    
    parser.add_argument(
        '--test', '-t',
        type=str,
        metavar='EMAIL',
        help='Testar sistema enviando e-mail de teste'
    )
    
    parser.add_argument(
        '--generate-file', '-f',
        type=str,
        metavar='ARQUIVO',
        help='Gerar relatório e salvar em arquivo'
    )
    
    parser.add_argument(
        '--status',
        action='store_true',
        help='Mostrar status do sistema'
    )
    
    parser.add_argument(
        '--help-setup',
        action='store_true',
        help='Mostrar ajuda de configuração'
    )
    
    args = parser.parse_args()
    
    cli = AdamSandlerNewsAgentCLI()
    cli.print_banner()
    
    # Mostrar ajuda de configuração
    if args.help_setup:
        cli.print_help()
        return 0
    
    # Verificar se pelo menos um comando foi especificado
    if not any([args.email, args.search, args.test, args.generate_file, args.status]):
        print("❌ Nenhum comando especificado!")
        print("Use --help para ver as opções disponíveis")
        print("Use --help-setup para ver ajuda de configuração")
        return 1
    
    async def run_async():
        """Executa comandos assíncronos."""
        try:
            # Executar comando apropriado
            if args.email:
                success = await cli.run_daily_report(args.email)
                return 0 if success else 1
            
            elif args.search:
                success = await cli.run_search_only()
                return 0 if success else 1
            
            elif args.test:
                success = await cli.run_test(args.test)
                return 0 if success else 1
            
            elif args.generate_file:
                success = await cli.generate_report_file(args.generate_file)
                return 0 if success else 1
            
            elif args.status:
                success = await cli.show_status()
                return 0 if success else 1
            
            return 1
            
        except KeyboardInterrupt:
            print("\n\n⚠️  Operação cancelada pelo usuário")
            return 1
        except Exception as e:
            print(f"\n❌ Erro inesperado: {str(e)}")
            return 1
    
    # Executar comando assíncrono
    try:
        exit_code = asyncio.run(run_async())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n⚠️  Operação cancelada pelo usuário")
        sys.exit(1)


if __name__ == "__main__":
    main()