import aiohttp
import json
import os
from typing import Optional, Dict, Any
from datetime import datetime
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()


class OpenRouterService:
    """Serviço para integração com OpenRouter API."""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv('OPENROUTER_API_KEY')
        self.base_url = "https://openrouter.ai/api/v1"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/adam-sandler-news-agent",
            "X-Title": "Adam Sandler News Agent"
        }
        
        # Modelo padrão - pode ser configurado
        self.default_model = "anthropic/claude-3.5-sonnet"
        
    async def analyze_news(self, news_title: str, news_content: str, 
                          news_url: str, news_source: str) -> Optional[Dict[str, Any]]:
        """Analisa uma notícia usando LLM via OpenRouter."""
        
        prompt = self._create_analysis_prompt(news_title, news_content, news_url, news_source)
        
        try:
            async with aiohttp.ClientSession() as session:
                payload = {
                    "model": self.default_model,
                    "messages": [
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    "max_tokens": 800,  # Reduzido para economizar créditos
                    "temperature": 0.7
                }
                
                async with session.post(
                    f"{self.base_url}/chat/completions",
                    headers=self.headers,
                    json=payload,
                    timeout=60
                ) as response:
                    
                    if response.status == 200:
                        result = await response.json()
                        analysis_text = result['choices'][0]['message']['content']
                        
                        return {
                            "analysis": analysis_text,
                            "model_used": self.default_model,
                            "analyzed_at": datetime.now().isoformat(),
                            "tokens_used": result.get('usage', {}).get('total_tokens', 0),
                            "success": True
                        }
                    else:
                        error_text = await response.text()
                        print(f"❌ Erro na API OpenRouter: {response.status} - {error_text}")
                        return {
                            "analysis": "Erro ao analisar notícia",
                            "error": f"Status {response.status}: {error_text}",
                            "success": False
                        }
                        
        except Exception as e:
            print(f"❌ Erro ao conectar com OpenRouter: {str(e)}")
            return {
                "analysis": "Erro de conexão ao analisar notícia",
                "error": str(e),
                "success": False
            }
    
    def _create_analysis_prompt(self, title: str, content: str, url: str, source: str) -> str:
        """Cria o prompt customizado para análise da notícia."""
        
        prompt = f"""
Você é um especialista em análise de notícias sobre entretenimento e celebridades. 
Analise a seguinte notícia sobre Adam Sandler e forneça uma análise detalhada.

**NOTÍCIA:**
Título: {title}
Fonte: {source}
URL: {url}

Conteúdo:
{content}

**INSTRUÇÕES PARA ANÁLISE:**

1. **RESUMO EXECUTIVO** (2-3 frases):
   - Resuma os pontos principais da notícia

2. **RELEVÂNCIA PARA ADAM SANDLER** (1-2 parágrafos):
   - Explique como esta notícia se relaciona com Adam Sandler
   - Qual o impacto ou importância para sua carreira

3. **CLASSIFICAÇÃO**:
   - Categoria: [Filme/TV/Negócios/Vida Pessoal/Outros]
   - Importância: [Alta/Média/Baixa]
   - Sentimento: [Positivo/Neutro/Negativo]

**FORMATO DE RESPOSTA:**
Forneça a análise em HTML bem formatado, usando tags apropriadas como <h3>, <p>, <strong>, <em>, etc.
Mantenha um tom profissional mas acessível.
"""
        
        return prompt
    
    async def test_connection(self) -> bool:
        """Testa a conexão com OpenRouter API."""
        try:
            async with aiohttp.ClientSession() as session:
                payload = {
                    "model": self.default_model,
                    "messages": [
                        {
                            "role": "user",
                            "content": "Responda apenas 'OK' para testar a conexão."
                        }
                    ],
                    "max_tokens": 10
                }
                
                async with session.post(
                    f"{self.base_url}/chat/completions",
                    headers=self.headers,
                    json=payload,
                    timeout=30
                ) as response:
                    
                    return response.status == 200
                    
        except Exception as e:
            print(f"❌ Erro no teste de conexão: {str(e)}")
            return False
    
    def set_model(self, model_name: str):
        """Define o modelo a ser usado."""
        self.default_model = model_name
    
    def get_available_models(self) -> list:
        """Retorna lista de modelos recomendados."""
        return [
            "anthropic/claude-3.5-sonnet",
            "openai/gpt-4o",
            "openai/gpt-4o-mini",
            "google/gemini-pro-1.5",
            "meta-llama/llama-3.1-70b-instruct"
        ]