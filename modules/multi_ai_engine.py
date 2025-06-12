"""
Multi-AI Engine
Support for multiple AI API providers with easy switching
"""

import os
import json
import logging
import requests
import pandas as pd
from datetime import datetime
from typing import Dict, List, Optional, Any
from enum import Enum

class AIProvider(Enum):
    """Available AI providers"""
    COHERE = "cohere"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE_GEMINI = "google_gemini"
    HUGGINGFACE = "huggingface"
    GROQ = "groq"

class MultiAIEngine:
    """Multi-provider AI engine for kitchen dashboard analytics"""
    
    def __init__(self, data: Dict[str, pd.DataFrame]):
        self.data = data
        self.logger = logging.getLogger(__name__)
        self.current_provider = None
        self.api_keys = self._load_api_keys()
        self.available_providers = self._check_available_providers()
        
    def _load_api_keys(self) -> Dict[str, str]:
        """Load API keys from environment variables"""
        api_keys = {}
        
        # Check for various API keys
        key_mappings = {
            AIProvider.COHERE: "COHERE_API_KEY",
            AIProvider.OPENAI: "OPENAI_API_KEY", 
            AIProvider.ANTHROPIC: "ANTHROPIC_API_KEY",
            AIProvider.GOOGLE_GEMINI: "GOOGLE_API_KEY",
            AIProvider.HUGGINGFACE: "HUGGINGFACE_API_KEY",
            AIProvider.GROQ: "GROQ_API_KEY"
        }
        
        for provider, env_var in key_mappings.items():
            key = os.getenv(env_var)
            if key:
                api_keys[provider] = key
                self.logger.info(f"Found API key for {provider.value}")
        
        return api_keys
    
    def _check_available_providers(self) -> List[AIProvider]:
        """Check which AI providers are available"""
        available = []
        
        for provider in AIProvider:
            if provider in self.api_keys:
                # Test the API key
                if self._test_provider(provider):
                    available.append(provider)
                    self.logger.info(f"{provider.value} is available")
                else:
                    self.logger.warning(f"{provider.value} API key invalid")
            else:
                self.logger.debug(f"No API key found for {provider.value}")
        
        return available
    
    def _test_provider(self, provider: AIProvider) -> bool:
        """Test if a provider's API key is valid"""
        try:
            if provider == AIProvider.COHERE:
                return self._test_cohere()
            elif provider == AIProvider.OPENAI:
                return self._test_openai()
            elif provider == AIProvider.ANTHROPIC:
                return self._test_anthropic()
            elif provider == AIProvider.GOOGLE_GEMINI:
                return self._test_google_gemini()
            elif provider == AIProvider.HUGGINGFACE:
                return self._test_huggingface()
            elif provider == AIProvider.GROQ:
                return self._test_groq()
            return False
        except Exception as e:
            self.logger.error(f"Error testing {provider.value}: {e}")
            return False
    
    def _test_cohere(self) -> bool:
        """Test Cohere API"""
        try:
            import cohere
            co = cohere.Client(self.api_keys[AIProvider.COHERE])
            # Simple test call with minimal usage
            response = co.generate(
                model='command-light',
                prompt="Hi",
                max_tokens=1,
                temperature=0
            )
            return response is not None
        except ImportError:
            # Cohere library not installed
            return False
        except Exception as e:
            # API key might be invalid or other error
            self.logger.debug(f"Cohere test failed: {e}")
            return False
    
    def _test_openai(self) -> bool:
        """Test OpenAI API"""
        try:
            headers = {
                "Authorization": f"Bearer {self.api_keys[AIProvider.OPENAI]}",
                "Content-Type": "application/json"
            }
            response = requests.get(
                "https://api.openai.com/v1/models",
                headers=headers,
                timeout=10
            )
            return response.status_code == 200
        except Exception:
            return False
    
    def _test_anthropic(self) -> bool:
        """Test Anthropic Claude API"""
        try:
            headers = {
                "x-api-key": self.api_keys[AIProvider.ANTHROPIC],
                "Content-Type": "application/json",
                "anthropic-version": "2023-06-01"
            }
            data = {
                "model": "claude-3-haiku-20240307",
                "max_tokens": 5,
                "messages": [{"role": "user", "content": "Test"}]
            }
            response = requests.post(
                "https://api.anthropic.com/v1/messages",
                headers=headers,
                json=data,
                timeout=10
            )
            return response.status_code == 200
        except Exception:
            return False
    
    def _test_google_gemini(self) -> bool:
        """Test Google Gemini API"""
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={self.api_keys[AIProvider.GOOGLE_GEMINI]}"
            data = {
                "contents": [{"parts": [{"text": "Test"}]}]
            }
            response = requests.post(url, json=data, timeout=10)
            return response.status_code == 200
        except Exception:
            return False
    
    def _test_huggingface(self) -> bool:
        """Test Hugging Face API"""
        try:
            headers = {
                "Authorization": f"Bearer {self.api_keys[AIProvider.HUGGINGFACE]}"
            }
            response = requests.get(
                "https://api-inference.huggingface.co/models/microsoft/DialoGPT-medium",
                headers=headers,
                timeout=10
            )
            return response.status_code == 200
        except Exception:
            return False
    
    def _test_groq(self) -> bool:
        """Test Groq API"""
        try:
            headers = {
                "Authorization": f"Bearer {self.api_keys[AIProvider.GROQ]}",
                "Content-Type": "application/json"
            }
            data = {
                "messages": [{"role": "user", "content": "Test"}],
                "model": "mixtral-8x7b-32768",
                "max_tokens": 5
            }
            response = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers=headers,
                json=data,
                timeout=10
            )
            return response.status_code == 200
        except Exception:
            return False
    
    def get_available_providers(self) -> List[Dict[str, str]]:
        """Get list of available AI providers"""
        providers = []
        
        provider_info = {
            AIProvider.COHERE: {
                "name": "Cohere",
                "description": "Advanced language model with business focus",
                "icon": "🧠",
                "strengths": ["Business Analysis", "Recommendations", "Text Generation"]
            },
            AIProvider.OPENAI: {
                "name": "OpenAI GPT",
                "description": "Most popular AI with excellent reasoning",
                "icon": "🤖",
                "strengths": ["General Intelligence", "Code Analysis", "Creative Tasks"]
            },
            AIProvider.ANTHROPIC: {
                "name": "Anthropic Claude",
                "description": "Safe and helpful AI assistant",
                "icon": "🎭",
                "strengths": ["Safety", "Analysis", "Long Context"]
            },
            AIProvider.GOOGLE_GEMINI: {
                "name": "Google Gemini",
                "description": "Google's multimodal AI model",
                "icon": "🌟",
                "strengths": ["Multimodal", "Fast", "Integration"]
            },
            AIProvider.HUGGINGFACE: {
                "name": "Hugging Face",
                "description": "Open source AI models",
                "icon": "🤗",
                "strengths": ["Open Source", "Variety", "Customizable"]
            },
            AIProvider.GROQ: {
                "name": "Groq",
                "description": "Ultra-fast AI inference",
                "icon": "⚡",
                "strengths": ["Speed", "Efficiency", "Real-time"]
            }
        }
        
        for provider in self.available_providers:
            info = provider_info[provider].copy()
            info["provider"] = provider.value
            info["status"] = "available"
            providers.append(info)
        
        return providers
    
    def set_provider(self, provider: str) -> bool:
        """Set the current AI provider"""
        try:
            provider_enum = AIProvider(provider)
            if provider_enum in self.available_providers:
                self.current_provider = provider_enum
                self.logger.info(f"Switched to {provider} AI provider")
                return True
            else:
                self.logger.error(f"Provider {provider} not available")
                return False
        except ValueError:
            self.logger.error(f"Unknown provider: {provider}")
            return False
    
    def get_current_provider(self) -> Optional[str]:
        """Get current AI provider"""
        return self.current_provider.value if self.current_provider else None
    
    def is_available(self) -> bool:
        """Check if any AI provider is available"""
        return len(self.available_providers) > 0

    def generate_sales_insights(self, sales_data: pd.DataFrame) -> Dict[str, Any]:
        """Generate sales insights using current AI provider"""
        if not self.current_provider:
            return {"error": "No AI provider selected"}

        try:
            # Prepare sales summary
            summary = self._prepare_sales_summary(sales_data)

            # Generate insights based on provider
            if self.current_provider == AIProvider.COHERE:
                return self._generate_cohere_insights(summary)
            elif self.current_provider == AIProvider.OPENAI:
                return self._generate_openai_insights(summary)
            elif self.current_provider == AIProvider.ANTHROPIC:
                return self._generate_anthropic_insights(summary)
            elif self.current_provider == AIProvider.GOOGLE_GEMINI:
                return self._generate_gemini_insights(summary)
            elif self.current_provider == AIProvider.HUGGINGFACE:
                return self._generate_huggingface_insights(summary)
            elif self.current_provider == AIProvider.GROQ:
                return self._generate_groq_insights(summary)
            else:
                return {"error": "Unsupported provider"}

        except Exception as e:
            self.logger.error(f"Error generating insights: {e}")
            return {"error": str(e)}

    def _prepare_sales_summary(self, sales_data: pd.DataFrame) -> str:
        """Prepare sales data summary for AI analysis"""
        if sales_data.empty:
            return "No sales data available"

        # Calculate key metrics
        total_revenue = sales_data['total_amount'].sum()
        total_orders = len(sales_data)
        avg_order_value = sales_data['total_amount'].mean()

        # Top items
        top_items = sales_data.groupby('item_name')['total_amount'].sum().sort_values(ascending=False).head(5)

        # Recent trends (last 7 days vs previous 7 days)
        if 'date' in sales_data.columns:
            sales_data['date'] = pd.to_datetime(sales_data['date'])
            recent_data = sales_data[sales_data['date'] >= sales_data['date'].max() - pd.Timedelta(days=7)]
            recent_revenue = recent_data['total_amount'].sum()
        else:
            recent_revenue = total_revenue

        summary = f"""
        Kitchen Sales Analysis:
        - Total Revenue: ₹{total_revenue:.2f}
        - Total Orders: {total_orders}
        - Average Order Value: ₹{avg_order_value:.2f}
        - Recent 7-day Revenue: ₹{recent_revenue:.2f}

        Top 5 Items by Revenue:
        {chr(10).join([f"- {item}: ₹{revenue:.2f}" for item, revenue in top_items.items()])}

        Please provide business insights and recommendations for this kitchen/restaurant.
        """

        return summary

    def _generate_cohere_insights(self, summary: str) -> Dict[str, Any]:
        """Generate insights using Cohere API"""
        try:
            import cohere
            co = cohere.Client(self.api_keys[AIProvider.COHERE])

            response = co.generate(
                model='command',
                prompt=f"{summary}\n\nProvide detailed business insights and actionable recommendations:",
                max_tokens=500,
                temperature=0.7
            )

            return {
                "provider": "Cohere",
                "ai_insights": response.generations[0].text.strip(),
                "confidence": 0.9,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {"error": f"Cohere API error: {e}"}

    def _generate_openai_insights(self, summary: str) -> Dict[str, Any]:
        """Generate insights using OpenAI API"""
        try:
            headers = {
                "Authorization": f"Bearer {self.api_keys[AIProvider.OPENAI]}",
                "Content-Type": "application/json"
            }

            data = {
                "model": "gpt-3.5-turbo",
                "messages": [
                    {"role": "system", "content": "You are a business analyst specializing in restaurant and kitchen operations."},
                    {"role": "user", "content": f"{summary}\n\nProvide detailed business insights and actionable recommendations:"}
                ],
                "max_tokens": 500,
                "temperature": 0.7
            }

            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                json=data,
                timeout=30
            )

            if response.status_code == 200:
                result = response.json()
                return {
                    "provider": "OpenAI GPT",
                    "ai_insights": result["choices"][0]["message"]["content"],
                    "confidence": 0.9,
                    "timestamp": datetime.now().isoformat()
                }
            else:
                return {"error": f"OpenAI API error: {response.status_code}"}

        except Exception as e:
            return {"error": f"OpenAI API error: {e}"}

    def _generate_anthropic_insights(self, summary: str) -> Dict[str, Any]:
        """Generate insights using Anthropic Claude API"""
        try:
            headers = {
                "x-api-key": self.api_keys[AIProvider.ANTHROPIC],
                "Content-Type": "application/json",
                "anthropic-version": "2023-06-01"
            }

            data = {
                "model": "claude-3-haiku-20240307",
                "max_tokens": 500,
                "messages": [
                    {"role": "user", "content": f"{summary}\n\nProvide detailed business insights and actionable recommendations:"}
                ]
            }

            response = requests.post(
                "https://api.anthropic.com/v1/messages",
                headers=headers,
                json=data,
                timeout=30
            )

            if response.status_code == 200:
                result = response.json()
                return {
                    "provider": "Anthropic Claude",
                    "ai_insights": result["content"][0]["text"],
                    "confidence": 0.9,
                    "timestamp": datetime.now().isoformat()
                }
            else:
                return {"error": f"Anthropic API error: {response.status_code}"}

        except Exception as e:
            return {"error": f"Anthropic API error: {e}"}

    def _generate_gemini_insights(self, summary: str) -> Dict[str, Any]:
        """Generate insights using Google Gemini API"""
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={self.api_keys[AIProvider.GOOGLE_GEMINI]}"

            data = {
                "contents": [
                    {"parts": [{"text": f"{summary}\n\nProvide detailed business insights and actionable recommendations:"}]}
                ]
            }

            response = requests.post(url, json=data, timeout=30)

            if response.status_code == 200:
                result = response.json()
                return {
                    "provider": "Google Gemini",
                    "ai_insights": result["candidates"][0]["content"]["parts"][0]["text"],
                    "confidence": 0.9,
                    "timestamp": datetime.now().isoformat()
                }
            else:
                return {"error": f"Gemini API error: {response.status_code}"}

        except Exception as e:
            return {"error": f"Gemini API error: {e}"}

    def _generate_huggingface_insights(self, summary: str) -> Dict[str, Any]:
        """Generate insights using Hugging Face API"""
        try:
            headers = {
                "Authorization": f"Bearer {self.api_keys[AIProvider.HUGGINGFACE]}",
                "Content-Type": "application/json"
            }

            data = {
                "inputs": f"{summary}\n\nProvide detailed business insights and actionable recommendations:",
                "parameters": {"max_length": 500, "temperature": 0.7}
            }

            response = requests.post(
                "https://api-inference.huggingface.co/models/microsoft/DialoGPT-large",
                headers=headers,
                json=data,
                timeout=30
            )

            if response.status_code == 200:
                result = response.json()
                return {
                    "provider": "Hugging Face",
                    "ai_insights": result[0]["generated_text"] if result else "No insights generated",
                    "confidence": 0.8,
                    "timestamp": datetime.now().isoformat()
                }
            else:
                return {"error": f"Hugging Face API error: {response.status_code}"}

        except Exception as e:
            return {"error": f"Hugging Face API error: {e}"}

    def _generate_groq_insights(self, summary: str) -> Dict[str, Any]:
        """Generate insights using Groq API"""
        try:
            headers = {
                "Authorization": f"Bearer {self.api_keys[AIProvider.GROQ]}",
                "Content-Type": "application/json"
            }

            data = {
                "messages": [
                    {"role": "system", "content": "You are a business analyst specializing in restaurant and kitchen operations."},
                    {"role": "user", "content": f"{summary}\n\nProvide detailed business insights and actionable recommendations:"}
                ],
                "model": "mixtral-8x7b-32768",
                "max_tokens": 500,
                "temperature": 0.7
            }

            response = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers=headers,
                json=data,
                timeout=30
            )

            if response.status_code == 200:
                result = response.json()
                return {
                    "provider": "Groq",
                    "ai_insights": result["choices"][0]["message"]["content"],
                    "confidence": 0.9,
                    "timestamp": datetime.now().isoformat()
                }
            else:
                return {"error": f"Groq API error: {response.status_code}"}

        except Exception as e:
            return {"error": f"Groq API error: {e}"}

# Global instance
_multi_ai_engine = None

def get_multi_ai_engine(data: Dict[str, pd.DataFrame]) -> MultiAIEngine:
    """Get or create the multi-AI engine instance"""
    global _multi_ai_engine
    if _multi_ai_engine is None:
        _multi_ai_engine = MultiAIEngine(data)
    return _multi_ai_engine
