import smtplib
import ssl
import re
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Optional
import os
from datetime import datetime

from ...domain.repositories.email_repository import EmailRepository
from ...domain.entities.report import Report


class SMTPEmailRepository(EmailRepository):
    """Implementação do repositório de e-mail usando SMTP."""
    
    def __init__(self, smtp_server: str = None, smtp_port: int = None, 
                 username: str = None, password: str = None):
        """
        Inicializa o repositório de e-mail.
        
        Args:
            smtp_server: Servidor SMTP (ex: smtp.gmail.com)
            smtp_port: Porta SMTP (ex: 587 para TLS, 465 para SSL)
            username: E-mail do remetente
            password: Senha ou app password do e-mail
        """
        self.smtp_server = smtp_server or os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = smtp_port or int(os.getenv('SMTP_PORT', '587'))
        self.username = username or os.getenv('EMAIL_USERNAME')
        self.password = password or os.getenv('EMAIL_PASSWORD')
        
        if not all([self.smtp_server, self.smtp_port, self.username, self.password]):
            raise ValueError("Configurações de e-mail incompletas. Verifique as variáveis de ambiente.")
    
    def validate_email(self, email: str) -> bool:
        """Valida se um e-mail tem formato correto."""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    async def send_report(self, report: Report, recipient_email: str, 
                         subject: Optional[str] = None) -> bool:
        """Envia um relatório por e-mail em formato texto."""
        if not self.validate_email(recipient_email):
            raise ValueError(f"E-mail inválido: {recipient_email}")
        
        if subject is None:
            subject = f"Relatório de Notícias sobre Adam Sandler - {report.generated_at.strftime('%d/%m/%Y')}"
        
        try:
            # Criar mensagem
            message = MIMEMultipart("alternative")
            message["Subject"] = subject
            message["From"] = self.username
            message["To"] = recipient_email
            
            # Conteúdo em texto
            text_content = report.generate_summary()
            text_part = MIMEText(text_content, "plain", "utf-8")
            message.attach(text_part)
            
            # Enviar e-mail
            return await self._send_email(message, recipient_email)
            
        except Exception as e:
            print(f"Erro ao enviar relatório por e-mail: {str(e)}")
            return False
    
    async def send_html_report(self, report: Report, recipient_email: str,
                              subject: Optional[str] = None) -> bool:
        """Envia um relatório em formato HTML por e-mail."""
        if not self.validate_email(recipient_email):
            raise ValueError(f"E-mail inválido: {recipient_email}")
        
        if subject is None:
            subject = f"Relatório de Notícias sobre Adam Sandler - {report.generated_at.strftime('%d/%m/%Y')}"
        
        try:
            # Criar mensagem
            message = MIMEMultipart("alternative")
            message["Subject"] = subject
            message["From"] = self.username
            message["To"] = recipient_email
            
            # Conteúdo em texto (fallback)
            text_content = report.generate_summary()
            text_part = MIMEText(text_content, "plain", "utf-8")
            
            # Conteúdo em HTML
            html_content = report.to_html()
            html_part = MIMEText(html_content, "html", "utf-8")
            
            # Adicionar ambas as partes
            message.attach(text_part)
            message.attach(html_part)
            
            # Enviar e-mail
            return await self._send_email(message, recipient_email)
            
        except Exception as e:
            print(f"Erro ao enviar relatório HTML por e-mail: {str(e)}")
            return False
    
    async def send_multiple_reports(self, reports: List[Report], 
                                   recipient_emails: List[str],
                                   subject: Optional[str] = None) -> bool:
        """Envia múltiplos relatórios para múltiplos destinatários."""
        success_count = 0
        total_sends = len(reports) * len(recipient_emails)
        
        for report in reports:
            for email in recipient_emails:
                try:
                    if await self.send_html_report(report, email, subject):
                        success_count += 1
                except Exception as e:
                    print(f"Erro ao enviar relatório para {email}: {str(e)}")
                    continue
        
        success_rate = success_count / total_sends if total_sends > 0 else 0
        print(f"Enviados {success_count}/{total_sends} e-mails com sucesso ({success_rate:.1%})")
        
        return success_rate > 0.5  # Considera sucesso se mais de 50% foram enviados
    
    async def _send_email(self, message: MIMEMultipart, recipient_email: str) -> bool:
        """Envia um e-mail usando SMTP."""
        try:
            # Criar contexto SSL
            context = ssl.create_default_context()
            
            # Conectar ao servidor SMTP
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls(context=context)  # Habilitar segurança
                server.login(self.username, self.password)
                
                # Enviar e-mail
                text = message.as_string()
                server.sendmail(self.username, recipient_email, text)
                
                print(f"E-mail enviado com sucesso para {recipient_email}")
                return True
                
        except smtplib.SMTPAuthenticationError:
            print("Erro de autenticação SMTP. Verifique username e password.")
            return False
        except smtplib.SMTPRecipientsRefused:
            print(f"E-mail destinatário recusado: {recipient_email}")
            return False
        except smtplib.SMTPServerDisconnected:
            print("Conexão com servidor SMTP perdida.")
            return False
        except Exception as e:
            print(f"Erro inesperado ao enviar e-mail: {str(e)}")
            return False
    
    def test_connection(self) -> bool:
        """Testa a conexão com o servidor SMTP."""
        try:
            context = ssl.create_default_context()
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls(context=context)
                server.login(self.username, self.password)
                print("Conexão SMTP testada com sucesso!")
                return True
        except Exception as e:
            print(f"Erro ao testar conexão SMTP: {str(e)}")
            return False
    
    async def send_test_email(self, recipient_email: str) -> bool:
        """Envia um e-mail de teste."""
        if not self.validate_email(recipient_email):
            raise ValueError(f"E-mail inválido: {recipient_email}")
        
        try:
            # Criar relatório de teste
            from ...domain.entities.news import News
            
            test_news = News(
                title="Teste - Adam Sandler em novo filme",
                content="Este é um e-mail de teste do sistema de notícias sobre Adam Sandler.",
                url="https://example.com/test",
                source="Sistema de Teste",
                published_date=datetime.now()
            )
            
            test_report = Report(
                title="Relatório de Teste - Adam Sandler News Agent",
                generated_at=datetime.now()
            )
            test_report.add_news(test_news)
            
            return await self.send_html_report(
                test_report, 
                recipient_email, 
                "Teste - Adam Sandler News Agent"
            )
            
        except Exception as e:
            print(f"Erro ao enviar e-mail de teste: {str(e)}")
            return False