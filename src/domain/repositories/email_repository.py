from abc import ABC, abstractmethod
from typing import List, Optional
from ..entities.report import Report


class EmailRepository(ABC):
    """Interface para repositório de e-mail."""
    
    @abstractmethod
    async def send_report(self, report: Report, recipient_email: str, 
                         subject: Optional[str] = None) -> bool:
        """Envia um relatório por e-mail."""
        pass
    
    @abstractmethod
    async def send_html_report(self, report: Report, recipient_email: str,
                              subject: Optional[str] = None) -> bool:
        """Envia um relatório em formato HTML por e-mail."""
        pass
    
    @abstractmethod
    async def send_multiple_reports(self, reports: List[Report], 
                                   recipient_emails: List[str],
                                   subject: Optional[str] = None) -> bool:
        """Envia múltiplos relatórios para múltiplos destinatários."""
        pass
    
    @abstractmethod
    def validate_email(self, email: str) -> bool:
        """Valida se um e-mail tem formato correto."""
        pass