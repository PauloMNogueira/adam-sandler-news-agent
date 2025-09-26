import os
import json
import subprocess
from typing import Optional, Dict, Any, List
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()


class GitHubService:
    """Serviço para integração com GitHub e publicação no GitHub Pages."""
    
    def __init__(self, token: Optional[str] = None, repository: Optional[str] = None):
        self.token = token or os.getenv('GITHUB_TOKEN')
        self.repository = repository or os.getenv('GITHUB_REPOSITORY')
        self.docs_dir = Path('docs')
        self.reports_index_file = self.docs_dir / 'reports.json'
        
        # Criar diretório docs se não existir
        self.docs_dir.mkdir(exist_ok=True)
    
    def is_configured(self) -> bool:
        """Verifica se o GitHub está configurado."""
        return bool(self.token and self.repository)
    
    def get_git_status(self) -> Dict[str, Any]:
        """Obtém o status do repositório Git."""
        try:
            # Verificar se é um repositório Git
            result = subprocess.run(['git', 'status', '--porcelain'], 
                                  capture_output=True, text=True, check=True)
            
            has_changes = bool(result.stdout.strip())
            
            # Obter branch atual
            branch_result = subprocess.run(['git', 'branch', '--show-current'], 
                                         capture_output=True, text=True, check=True)
            current_branch = branch_result.stdout.strip()
            
            return {
                'is_git_repo': True,
                'has_changes': has_changes,
                'current_branch': current_branch,
                'changes': result.stdout.strip().split('\n') if has_changes else []
            }
            
        except subprocess.CalledProcessError:
            return {
                'is_git_repo': False,
                'has_changes': False,
                'current_branch': None,
                'changes': []
            }
    
    def save_report_to_docs(self, report_html: str, report_title: str, 
                           news_count: int) -> Optional[str]:
        """Salva um relatório no diretório docs/ com timestamp."""
        try:
            # Gerar nome do arquivo com timestamp
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'relatorio_{timestamp}.html'
            filepath = self.docs_dir / filename
            
            # Salvar arquivo HTML
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(report_html)
            
            # Atualizar índice de relatórios
            self._update_reports_index(filename, report_title, news_count, timestamp)
            
            # Atualizar página principal
            self._update_index_page()
            
            print(f"📄 Relatório salvo em: {filepath}")
            return str(filepath)
            
        except Exception as e:
            print(f"❌ Erro ao salvar relatório: {e}")
            return None
    
    def _update_reports_index(self, filename: str, title: str, 
                             news_count: int, timestamp: str) -> None:
        """Atualiza o índice de relatórios em JSON."""
        try:
            # Carregar índice existente ou criar novo
            if self.reports_index_file.exists():
                with open(self.reports_index_file, 'r', encoding='utf-8') as f:
                    reports = json.load(f)
            else:
                reports = []
            
            # Adicionar novo relatório
            new_report = {
                'filename': filename,
                'title': title,
                'news_count': news_count,
                'timestamp': timestamp,
                'date': datetime.strptime(timestamp, '%Y%m%d_%H%M%S').strftime('%d/%m/%Y %H:%M'),
                'generated_at': datetime.now().isoformat()
            }
            
            # Inserir no início da lista (mais recente primeiro)
            reports.insert(0, new_report)
            
            # Manter apenas os últimos 50 relatórios
            reports = reports[:50]
            
            # Salvar índice atualizado
            with open(self.reports_index_file, 'w', encoding='utf-8') as f:
                json.dump(reports, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            print(f"❌ Erro ao atualizar índice de relatórios: {e}")
    
    def _update_index_page(self) -> None:
        """Atualiza a página principal com os relatórios mais recentes."""
        try:
            if not self.reports_index_file.exists():
                return
            
            # Carregar relatórios
            with open(self.reports_index_file, 'r', encoding='utf-8') as f:
                reports = json.load(f)
            
            # Ler template da página principal
            index_file = self.docs_dir / 'index.html'
            with open(index_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Gerar JavaScript com dados dos relatórios
            reports_js = f"const reports = {json.dumps(reports, ensure_ascii=False)};"
            
            # Substituir a linha de reports vazios no JavaScript
            content = content.replace(
                'const reports = [];',
                reports_js
            )
            
            # Salvar página atualizada
            with open(index_file, 'w', encoding='utf-8') as f:
                f.write(content)
                
        except Exception as e:
            print(f"❌ Erro ao atualizar página principal: {e}")
    
    def commit_and_push_changes(self, commit_message: Optional[str] = None) -> bool:
        """Faz commit e push das mudanças para o GitHub."""
        if not self.is_configured():
            print("❌ GitHub não configurado. Configure GITHUB_TOKEN e GITHUB_REPOSITORY")
            return False
        
        try:
            # Verificar status do Git
            git_status = self.get_git_status()
            
            if not git_status['is_git_repo']:
                print("❌ Não é um repositório Git")
                return False
            
            if not git_status['has_changes']:
                print("ℹ️ Nenhuma mudança para fazer commit")
                return True
            
            # Configurar Git com token
            self._configure_git_credentials()
            
            # Adicionar arquivos do diretório docs
            subprocess.run(['git', 'add', 'docs/'], check=True)
            
            # Fazer commit
            if not commit_message:
                timestamp = datetime.now().strftime('%d/%m/%Y às %H:%M')
                commit_message = f"📰 Novo relatório de notícias - {timestamp}"
            
            subprocess.run(['git', 'commit', '-m', commit_message], check=True)
            
            # Push para o repositório
            subprocess.run(['git', 'push', 'origin', git_status['current_branch']], check=True)
            
            print(f"✅ Mudanças enviadas para GitHub: {self.repository}")
            print(f"🌐 Site disponível em: https://{self._get_github_pages_url()}")
            
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Erro no Git: {e}")
            return False
        except Exception as e:
            print(f"❌ Erro ao enviar para GitHub: {e}")
            return False
    
    def _configure_git_credentials(self) -> None:
        """Configura credenciais do Git para usar o token."""
        try:
            # Configurar URL remota com token
            remote_url = f"https://{self.token}@github.com/{self.repository}.git"
            subprocess.run(['git', 'remote', 'set-url', 'origin', remote_url], check=True)
            
            # Configurar usuário (necessário para commits)
            subprocess.run(['git', 'config', 'user.name', 'Adam Sandler News Bot'], check=True)
            subprocess.run(['git', 'config', 'user.email', 'bot@adamsandlernews.com'], check=True)
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Erro ao configurar credenciais Git: {e}")
            raise
    
    def _get_github_pages_url(self) -> str:
        """Obtém a URL do GitHub Pages."""
        if not self.repository:
            return ""
        
        # Formato: username.github.io/repository-name
        parts = self.repository.split('/')
        if len(parts) == 2:
            username, repo_name = parts
            return f"{username}.github.io/{repo_name}"
        
        return ""
    
    def get_github_pages_status(self) -> Dict[str, Any]:
        """Obtém informações sobre o status do GitHub Pages."""
        return {
            'configured': self.is_configured(),
            'repository': self.repository,
            'docs_directory': str(self.docs_dir),
            'pages_url': f"https://{self._get_github_pages_url()}" if self.is_configured() else None,
            'reports_count': len(self._get_reports_list()),
            'git_status': self.get_git_status()
        }
    
    def _get_reports_list(self) -> List[Dict[str, Any]]:
        """Obtém a lista de relatórios disponíveis."""
        try:
            if self.reports_index_file.exists():
                with open(self.reports_index_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return []
        except Exception:
            return []
    
    def initialize_repository(self) -> bool:
        """Inicializa o repositório Git se necessário."""
        try:
            git_status = self.get_git_status()
            
            if not git_status['is_git_repo']:
                print("📁 Inicializando repositório Git...")
                subprocess.run(['git', 'init'], check=True)
                
                # Criar .gitignore se não existir
                gitignore_path = Path('.gitignore')
                if not gitignore_path.exists():
                    with open(gitignore_path, 'w') as f:
                        f.write("__pycache__/\n*.pyc\n.env\n*.log\n")
                
                print("✅ Repositório Git inicializado")
            
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Erro ao inicializar repositório: {e}")
            return False