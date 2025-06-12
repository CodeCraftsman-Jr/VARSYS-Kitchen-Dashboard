"""
Cohere AI Integration Module
Uses Cohere's free tier API for AI-powered insights instead of local ML training
"""

import os
import json
import logging
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import pandas as pd

class CohereAIEngine:
    """Cohere AI integration for kitchen dashboard insights"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.logger = logging.getLogger(__name__)
        
        # Get API key from environment or parameter
        self.api_key = api_key or os.getenv('COHERE_API_KEY')
        
        if not self.api_key:
            self.logger.warning("No Cohere API key provided. AI features will be limited.")
            self.enabled = False
        else:
            self.enabled = True
            
        self.base_url = "https://api.cohere.ai/v1"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # Cache for responses to avoid repeated API calls
        self.response_cache = {}
        self.cache_duration = 3600  # 1 hour
        
    def is_enabled(self) -> bool:
        """Check if Cohere AI is enabled"""
        return self.enabled
    
    def _make_request(self, endpoint: str, data: Dict) -> Optional[Dict]:
        """Make request to Cohere API with error handling"""
        if not self.enabled:
            return None
            
        try:
            url = f"{self.base_url}/{endpoint}"
            response = requests.post(url, headers=self.headers, json=data, timeout=30)
            
            if response.status_code == 200:
                return response.json()
            else:
                self.logger.error(f"Cohere API error: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            self.logger.error(f"Error making Cohere API request: {e}")
            return None
    
    def _get_cached_response(self, cache_key: str) -> Optional[Dict]:
        """Get cached response if still valid"""
        if cache_key in self.response_cache:
            cached_data = self.response_cache[cache_key]
            if datetime.now() - cached_data['timestamp'] < timedelta(seconds=self.cache_duration):
                return cached_data['response']
        return None
    
    def _cache_response(self, cache_key: str, response: Dict):
        """Cache API response"""
        self.response_cache[cache_key] = {
            'response': response,
            'timestamp': datetime.now()
        }
    
    def generate_sales_insights(self, sales_data: pd.DataFrame) -> Dict[str, Any]:
        """Generate sales insights using Cohere AI"""
        cache_key = f"sales_insights_{len(sales_data)}"
        cached = self._get_cached_response(cache_key)
        if cached:
            return cached
            
        try:
            # Prepare sales summary for AI analysis
            if sales_data.empty:
                return {"error": "No sales data available"}
            
            # Create summary statistics
            total_sales = sales_data['total_amount'].sum() if 'total_amount' in sales_data.columns else 0
            avg_order_value = sales_data['total_amount'].mean() if 'total_amount' in sales_data.columns else 0
            total_orders = len(sales_data)
            
            # Get top selling items
            if 'item_name' in sales_data.columns:
                top_items = sales_data.groupby('item_name')['quantity'].sum().head(5).to_dict()
            else:
                top_items = {}
            
            # Create prompt for Cohere
            prompt = f"""
            Analyze this kitchen business sales data and provide insights:
            
            Sales Summary:
            - Total Sales: ₹{total_sales:.2f}
            - Average Order Value: ₹{avg_order_value:.2f}
            - Total Orders: {total_orders}
            - Top Selling Items: {json.dumps(top_items, indent=2)}
            
            Please provide:
            1. Key performance insights
            2. Sales trends analysis
            3. Recommendations for improvement
            4. Potential growth opportunities
            
            Keep the response concise and actionable for a kitchen business owner.
            """
            
            data = {
                "model": "command-light",
                "prompt": prompt,
                "max_tokens": 500,
                "temperature": 0.7
            }
            
            response = self._make_request("generate", data)
            
            if response and 'generations' in response:
                insights = {
                    "ai_insights": response['generations'][0]['text'].strip(),
                    "summary_stats": {
                        "total_sales": total_sales,
                        "avg_order_value": avg_order_value,
                        "total_orders": total_orders,
                        "top_items": top_items
                    },
                    "generated_at": datetime.now().isoformat()
                }
                
                self._cache_response(cache_key, insights)
                return insights
            else:
                return {"error": "Failed to generate insights"}
                
        except Exception as e:
            self.logger.error(f"Error generating sales insights: {e}")
            return {"error": str(e)}
    
    def generate_inventory_recommendations(self, inventory_data: pd.DataFrame, sales_data: pd.DataFrame) -> Dict[str, Any]:
        """Generate inventory management recommendations"""
        cache_key = f"inventory_rec_{len(inventory_data)}_{len(sales_data)}"
        cached = self._get_cached_response(cache_key)
        if cached:
            return cached
            
        try:
            # Analyze inventory levels
            low_stock_items = []
            if 'quantity' in inventory_data.columns and 'reorder_level' in inventory_data.columns:
                low_stock = inventory_data[inventory_data['quantity'] <= inventory_data['reorder_level']]
                low_stock_items = low_stock['item_name'].tolist() if 'item_name' in low_stock.columns else []
            
            # Calculate inventory turnover
            if not sales_data.empty and 'item_name' in sales_data.columns:
                sales_by_item = sales_data.groupby('item_name')['quantity'].sum().to_dict()
            else:
                sales_by_item = {}
            
            prompt = f"""
            Analyze this kitchen inventory data and provide recommendations:
            
            Inventory Status:
            - Total Items: {len(inventory_data)}
            - Low Stock Items: {low_stock_items}
            - Sales by Item: {json.dumps(dict(list(sales_by_item.items())[:10]), indent=2)}
            
            Please provide:
            1. Inventory optimization recommendations
            2. Reorder suggestions
            3. Cost reduction opportunities
            4. Waste reduction strategies
            
            Focus on practical advice for a kitchen business.
            """
            
            data = {
                "model": "command-light",
                "prompt": prompt,
                "max_tokens": 400,
                "temperature": 0.6
            }
            
            response = self._make_request("generate", data)
            
            if response and 'generations' in response:
                recommendations = {
                    "ai_recommendations": response['generations'][0]['text'].strip(),
                    "low_stock_items": low_stock_items,
                    "inventory_stats": {
                        "total_items": len(inventory_data),
                        "low_stock_count": len(low_stock_items)
                    },
                    "generated_at": datetime.now().isoformat()
                }
                
                self._cache_response(cache_key, recommendations)
                return recommendations
            else:
                return {"error": "Failed to generate recommendations"}
                
        except Exception as e:
            self.logger.error(f"Error generating inventory recommendations: {e}")
            return {"error": str(e)}
    
    def generate_pricing_suggestions(self, pricing_data: Dict, market_data: Dict = None) -> Dict[str, Any]:
        """Generate pricing optimization suggestions"""
        cache_key = f"pricing_suggestions_{hash(str(pricing_data))}"
        cached = self._get_cached_response(cache_key)
        if cached:
            return cached
            
        try:
            prompt = f"""
            Analyze this kitchen business pricing data and suggest optimizations:
            
            Current Pricing Data:
            {json.dumps(pricing_data, indent=2)}
            
            Please provide:
            1. Pricing strategy recommendations
            2. Competitive positioning advice
            3. Profit margin optimization
            4. Dynamic pricing suggestions
            
            Consider factors like cost, competition, and customer value perception.
            """
            
            data = {
                "model": "command-light",
                "prompt": prompt,
                "max_tokens": 400,
                "temperature": 0.6
            }
            
            response = self._make_request("generate", data)
            
            if response and 'generations' in response:
                suggestions = {
                    "ai_suggestions": response['generations'][0]['text'].strip(),
                    "pricing_data": pricing_data,
                    "generated_at": datetime.now().isoformat()
                }
                
                self._cache_response(cache_key, suggestions)
                return suggestions
            else:
                return {"error": "Failed to generate pricing suggestions"}
                
        except Exception as e:
            self.logger.error(f"Error generating pricing suggestions: {e}")
            return {"error": str(e)}
    
    def generate_business_summary(self, all_data: Dict[str, pd.DataFrame]) -> Dict[str, Any]:
        """Generate comprehensive business summary and insights"""
        cache_key = f"business_summary_{datetime.now().strftime('%Y-%m-%d')}"
        cached = self._get_cached_response(cache_key)
        if cached:
            return cached
            
        try:
            # Prepare business overview
            summary_stats = {}
            
            if 'sales' in all_data and not all_data['sales'].empty:
                sales_df = all_data['sales']
                summary_stats['sales'] = {
                    'total_revenue': sales_df['total_amount'].sum() if 'total_amount' in sales_df.columns else 0,
                    'total_orders': len(sales_df),
                    'avg_order_value': sales_df['total_amount'].mean() if 'total_amount' in sales_df.columns else 0
                }
            
            if 'inventory' in all_data and not all_data['inventory'].empty:
                inventory_df = all_data['inventory']
                summary_stats['inventory'] = {
                    'total_items': len(inventory_df),
                    'total_value': inventory_df['total_value'].sum() if 'total_value' in inventory_df.columns else 0
                }
            
            prompt = f"""
            Provide a comprehensive business analysis for this kitchen business:
            
            Business Overview:
            {json.dumps(summary_stats, indent=2)}
            
            Please provide:
            1. Overall business health assessment
            2. Key performance indicators analysis
            3. Strategic recommendations for growth
            4. Risk factors and mitigation strategies
            5. Next steps for business improvement
            
            Make it actionable and specific to food service industry.
            """
            
            data = {
                "model": "command-light",
                "prompt": prompt,
                "max_tokens": 600,
                "temperature": 0.7
            }
            
            response = self._make_request("generate", data)
            
            if response and 'generations' in response:
                business_summary = {
                    "ai_analysis": response['generations'][0]['text'].strip(),
                    "summary_stats": summary_stats,
                    "generated_at": datetime.now().isoformat()
                }
                
                self._cache_response(cache_key, business_summary)
                return business_summary
            else:
                return {"error": "Failed to generate business summary"}
                
        except Exception as e:
            self.logger.error(f"Error generating business summary: {e}")
            return {"error": str(e)}
    
    def clear_cache(self):
        """Clear response cache"""
        self.response_cache.clear()
        self.logger.info("Cohere AI response cache cleared")
