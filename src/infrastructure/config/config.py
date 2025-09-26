"""
Configurações do sistema Adam Sandler News Agent.
"""

import os
from typing import Optional
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()


class Config:
    """Classe de configuração centralizada."""
    
    # Email Configuration
    SMTP_SERVER: str = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
    SMTP_PORT: int = int(os.getenv('SMTP_PORT', '587'))
    SMTP_USERNAME: str = os.getenv('SMTP_USERNAME', '')
    SMTP_PASSWORD: str = os.getenv('SMTP_PASSWORD', '')
    SMTP_USE_TLS: bool = os.getenv('SMTP_USE_TLS', 'true').lower() == 'true'
    
    # Email Recipients
    DEFAULT_EMAIL_RECIPIENT: str = os.getenv('DEFAULT_EMAIL_RECIPIENT', '')
    
    # News Search Configuration
    SEARCH_QUERY: str = os.getenv('SEARCH_QUERY', 'Adam Sandler')
    MAX_NEWS_PER_SOURCE: int = int(os.getenv('MAX_NEWS_PER_SOURCE', '10'))
    NEWS_RELEVANCE_THRESHOLD: float = float(os.getenv('NEWS_RELEVANCE_THRESHOLD', '0.7'))
    
    # OpenRouter AI Configuration
    OPENROUTER_API_KEY: str = os.getenv('OPENROUTER_API_KEY', '')
    OPENROUTER_MODEL: str = os.getenv('OPENROUTER_MODEL', 'anthropic/claude-3.5-sonnet')
    
    # Report Configuration
    REPORT_TITLE: str = os.getenv('REPORT_TITLE', 'Adam Sandler Daily News Report')
    REPORT_OUTPUT_DIR: str = os.getenv('REPORT_OUTPUT_DIR', 'reports')
    
    # System Configuration
    REQUEST_TIMEOUT: int = int(os.getenv('REQUEST_TIMEOUT', '30'))
    LOG_LEVEL: str = os.getenv('LOG_LEVEL', 'INFO')
    
    @classmethod
    def validate_openrouter_config(cls) -> bool:
        """Valida se as configurações do OpenRouter estão presentes."""
        return bool(cls.OPENROUTER_API_KEY)
    
    @classmethod
    def validate_email_config(cls) -> bool:
        """Valida se as configurações de email estão presentes."""
        return bool(cls.SMTP_USERNAME and cls.SMTP_PASSWORD and cls.DEFAULT_EMAIL_RECIPIENT)
    
    @classmethod
    def get_openrouter_config(cls) -> dict:
        """Retorna configurações do OpenRouter."""
        return {
            'api_key': cls.OPENROUTER_API_KEY,
            'model': cls.OPENROUTER_MODEL
        }
    
    @classmethod
    def get_email_config(cls) -> dict:
        """Retorna configurações de email."""
        return {
            'server': cls.SMTP_SERVER,
            'port': cls.SMTP_PORT,
            'username': cls.SMTP_USERNAME,
            'password': cls.SMTP_PASSWORD,
            'use_tls': cls.SMTP_USE_TLS,
            'default_recipient': cls.DEFAULT_EMAIL_RECIPIENT
        }