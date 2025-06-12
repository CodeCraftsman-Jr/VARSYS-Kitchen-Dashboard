"""
AI & Machine Learning Engine
Advanced AI-powered analytics, predictions, and recommendations
"""

import os
import json
import logging
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
import sqlite3
from sklearn.ensemble import RandomForestRegressor, IsolationForest
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error
import warnings
warnings.filterwarnings('ignore')

# Import activity tracker
try:
    from .activity_tracker import track_user_action, track_system_event, track_performance_start, track_performance_end
except ImportError:
    def track_user_action(*args, **kwargs): pass
    def track_system_event(*args, **kwargs): pass
    def track_performance_start(*args, **kwargs): pass
    def track_performance_end(*args, **kwargs): pass

class PredictionType(Enum):
    """Types of predictions available"""
    SALES_FORECAST = "sales_forecast"
    DEMAND_PREDICTION = "demand_prediction"
    INVENTORY_OPTIMIZATION = "inventory_optimization"
    PRICE_OPTIMIZATION = "price_optimization"
    CUSTOMER_BEHAVIOR = "customer_behavior"

class InsightType(Enum):
    """Types of AI insights"""
    TREND_ANALYSIS = "trend_analysis"
    ANOMALY_DETECTION = "anomaly_detection"
    RECOMMENDATION = "recommendation"
    OPTIMIZATION = "optimization"
    PREDICTION = "prediction"

class AIMLEngine:
    """
    AI & Machine Learning Engine that provides:
    - Predictive analytics for sales and demand
    - Smart recommendations for menu and pricing
    - Anomaly detection for unusual patterns
    - Natural language query processing
    - Automated business insights
    """
    
    def __init__(self, data: Dict[str, pd.DataFrame]):
        self.logger = logging.getLogger(__name__)
        self.data = data
        
        # ML Models
        self.models = {}
        self.scalers = {}
        self.encoders = {}
        
        # AI Insights storage
        self.insights_db_path = "ai_insights.db"
        self.init_insights_database()
        
        # Model training status
        self.models_trained = False
        self.last_training_time = None
        
        # Initialize models
        self.initialize_models()
        
        self.logger.info("AI & ML Engine initialized")
        track_system_event("ai_ml_engine", "initialized", "AI & Machine Learning engine started")
    
    def init_insights_database(self):
        """Initialize AI insights database"""
        try:
            with sqlite3.connect(self.insights_db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS ai_insights (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        insight_type TEXT NOT NULL,
                        category TEXT NOT NULL,
                        title TEXT NOT NULL,
                        description TEXT NOT NULL,
                        confidence REAL NOT NULL,
                        data TEXT,
                        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                        is_active BOOLEAN DEFAULT 1
                    )
                """)
                
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS predictions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        prediction_type TEXT NOT NULL,
                        target_date TEXT NOT NULL,
                        predicted_value REAL NOT NULL,
                        confidence REAL NOT NULL,
                        model_used TEXT NOT NULL,
                        input_data TEXT,
                        created_at TEXT DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS model_performance (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        model_name TEXT NOT NULL,
                        model_type TEXT NOT NULL,
                        accuracy REAL,
                        mae REAL,
                        rmse REAL,
                        training_date TEXT DEFAULT CURRENT_TIMESTAMP,
                        data_size INTEGER
                    )
                """)
                
                conn.commit()
                self.logger.info("AI insights database initialized")
                
        except Exception as e:
            self.logger.error(f"Error initializing AI insights database: {e}")
    
    def initialize_models(self):
        """Initialize ML models"""
        try:
            # Sales forecasting model
            self.models['sales_forecast'] = RandomForestRegressor(
                n_estimators=100, random_state=42, max_depth=10
            )
            
            # Demand prediction model
            self.models['demand_prediction'] = RandomForestRegressor(
                n_estimators=50, random_state=42, max_depth=8
            )
            
            # Price optimization model
            self.models['price_optimization'] = LinearRegression()
            
            # Anomaly detection model
            self.models['anomaly_detection'] = IsolationForest(
                contamination=0.1, random_state=42
            )
            
            # Initialize scalers and encoders
            self.scalers['sales'] = StandardScaler()
            self.scalers['demand'] = StandardScaler()
            self.scalers['price'] = StandardScaler()
            
            self.encoders['category'] = LabelEncoder()
            self.encoders['item'] = LabelEncoder()
            
            self.logger.info("ML models initialized")
            
        except Exception as e:
            self.logger.error(f"Error initializing ML models: {e}")
    
    def train_models(self) -> Dict[str, Any]:
        """Train all ML models with current data"""
        operation_id = f"train_models_{datetime.now().timestamp()}"
        track_performance_start(operation_id, "ai_ml_engine", "train_models")
        
        try:
            training_results = {}
            
            # Train sales forecasting model
            if 'sales' in self.data and not self.data['sales'].empty:
                sales_result = self.train_sales_forecast_model()
                training_results['sales_forecast'] = sales_result
            
            # Train demand prediction model
            if 'inventory' in self.data and 'sales' in self.data:
                demand_result = self.train_demand_prediction_model()
                training_results['demand_prediction'] = demand_result
            
            # Train price optimization model
            if 'sales' in self.data and 'items' in self.data:
                price_result = self.train_price_optimization_model()
                training_results['price_optimization'] = price_result
            
            # Train anomaly detection model
            anomaly_result = self.train_anomaly_detection_model()
            training_results['anomaly_detection'] = anomaly_result
            
            self.models_trained = True
            self.last_training_time = datetime.now()
            
            # Store training results
            self.store_model_performance(training_results)
            
            track_performance_end(operation_id, "ai_ml_engine", "train_models",
                                metadata={"models_trained": len(training_results)})
            
            self.logger.info(f"Successfully trained {len(training_results)} ML models")
            return training_results
            
        except Exception as e:
            self.logger.error(f"Error training ML models: {e}")
            track_performance_end(operation_id, "ai_ml_engine", "train_models",
                                metadata={"error": str(e)})
            return {}
    
    def train_sales_forecast_model(self) -> Dict[str, Any]:
        """Train sales forecasting model"""
        try:
            sales_df = self.data['sales'].copy()
            
            # Prepare features
            sales_df['date'] = pd.to_datetime(sales_df.get('date', sales_df.get('order_date', datetime.now())))
            sales_df['day_of_week'] = sales_df['date'].dt.dayofweek
            sales_df['month'] = sales_df['date'].dt.month
            sales_df['day_of_month'] = sales_df['date'].dt.day
            
            # Create features
            features = ['day_of_week', 'month', 'day_of_month']
            if 'item_count' in sales_df.columns:
                features.append('item_count')
            if 'customer_rating' in sales_df.columns:
                features.append('customer_rating')
            
            # Target variable
            target = 'total_amount' if 'total_amount' in sales_df.columns else 'amount'
            
            # Prepare data
            X = sales_df[features].fillna(0)
            y = sales_df[target].fillna(0)
            
            if len(X) < 10:  # Need minimum data for training
                return {"error": "Insufficient data for training"}
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
            
            # Scale features
            X_train_scaled = self.scalers['sales'].fit_transform(X_train)
            X_test_scaled = self.scalers['sales'].transform(X_test)
            
            # Train model
            self.models['sales_forecast'].fit(X_train_scaled, y_train)
            
            # Evaluate model
            y_pred = self.models['sales_forecast'].predict(X_test_scaled)
            mae = mean_absolute_error(y_test, y_pred)
            rmse = np.sqrt(mean_squared_error(y_test, y_pred))
            
            return {
                "model": "sales_forecast",
                "mae": mae,
                "rmse": rmse,
                "data_size": len(X),
                "features": features
            }
            
        except Exception as e:
            self.logger.error(f"Error training sales forecast model: {e}")
            return {"error": str(e)}
    
    def train_demand_prediction_model(self) -> Dict[str, Any]:
        """Train demand prediction model"""
        try:
            # Combine sales and inventory data
            sales_df = self.data['sales'].copy()
            inventory_df = self.data['inventory'].copy()
            
            # Aggregate sales by item
            if 'item_name' in sales_df.columns and 'quantity' in sales_df.columns:
                # Check if required columns exist in sales data
                sales_columns = ['quantity']
                if 'total_amount' in sales_df.columns:
                    sales_columns.append('total_amount')
                elif 'amount' in sales_df.columns:
                    sales_columns.append('amount')

                item_sales = sales_df.groupby('item_name')[sales_columns].sum().reset_index()

                # Merge with inventory (check for correct column name)
                inventory_name_col = 'item_name' if 'item_name' in inventory_df.columns else 'name'
                merged_df = pd.merge(item_sales, inventory_df,
                                   left_on='item_name', right_on=inventory_name_col, how='inner', suffixes=('_sales', '_inv'))

                # Create features - be specific about which quantity column to use
                features = []
                if 'quantity_sales' in merged_df.columns:
                    features.append('quantity_sales')
                elif 'quantity' in merged_df.columns:
                    features.append('quantity')

                if 'total_amount' in merged_df.columns:
                    features.append('total_amount')
                elif 'amount' in merged_df.columns:
                    features.append('amount')

                # Add inventory features
                if 'quantity_inv' in merged_df.columns:
                    features.append('quantity_inv')
                if 'reorder_level' in merged_df.columns:
                    features.append('reorder_level')

                # Target: future demand (using sales quantity as proxy)
                target = 'quantity_sales' if 'quantity_sales' in merged_df.columns else 'quantity'

                if not features or target not in merged_df.columns:
                    return {"error": "Required columns not found after merge"}

                X = merged_df[features].fillna(0)
                y = merged_df[target].fillna(0)
                
                if len(X) < 5:
                    return {"error": "Insufficient data for training"}
                
                # Train model
                X_scaled = self.scalers['demand'].fit_transform(X)
                self.models['demand_prediction'].fit(X_scaled, y)
                
                return {
                    "model": "demand_prediction",
                    "data_size": len(X),
                    "features": features
                }
            
            return {"error": "No item_name column found in sales data"}
            
        except Exception as e:
            self.logger.error(f"Error training demand prediction model: {e}")
            return {"error": str(e)}
    
    def train_price_optimization_model(self) -> Dict[str, Any]:
        """Train price optimization model"""
        try:
            sales_df = self.data['sales'].copy()
            
            # Create price-related features
            if 'unit_price' in sales_df.columns and 'quantity' in sales_df.columns:
                features = ['unit_price', 'quantity']
                if 'customer_rating' in sales_df.columns:
                    features.append('customer_rating')
                
                target = 'total_amount'
                
                X = sales_df[features].fillna(0)
                y = sales_df[target].fillna(0)
                
                if len(X) < 5:
                    return {"error": "Insufficient data for training"}
                
                # Train model
                X_scaled = self.scalers['price'].fit_transform(X)
                self.models['price_optimization'].fit(X_scaled, y)
                
                return {
                    "model": "price_optimization",
                    "data_size": len(X),
                    "features": features
                }
            
            return {"error": "Required price columns not found"}
            
        except Exception as e:
            self.logger.error(f"Error training price optimization model: {e}")
            return {"error": str(e)}
    
    def train_anomaly_detection_model(self) -> Dict[str, Any]:
        """Train anomaly detection model"""
        try:
            # Use sales data for anomaly detection
            if 'sales' in self.data and not self.data['sales'].empty:
                sales_df = self.data['sales'].copy()
                
                # Create features for anomaly detection
                features = []
                if 'total_amount' in sales_df.columns:
                    features.append('total_amount')
                if 'quantity' in sales_df.columns:
                    features.append('quantity')
                if 'unit_price' in sales_df.columns:
                    features.append('unit_price')
                
                if not features:
                    return {"error": "No suitable features for anomaly detection"}
                
                X = sales_df[features].fillna(0)
                
                # Train anomaly detection model
                self.models['anomaly_detection'].fit(X)
                
                return {
                    "model": "anomaly_detection",
                    "data_size": len(X),
                    "features": features
                }
            
            return {"error": "No sales data available"}
            
        except Exception as e:
            self.logger.error(f"Error training anomaly detection model: {e}")
            return {"error": str(e)}
    
    def generate_sales_forecast(self, days_ahead: int = 7) -> List[Dict[str, Any]]:
        """Generate sales forecast for specified days ahead"""
        try:
            if not self.models_trained or 'sales_forecast' not in self.models:
                return []
            
            forecasts = []
            base_date = datetime.now()
            
            for i in range(days_ahead):
                target_date = base_date + timedelta(days=i+1)
                
                # Create features for prediction
                features = [
                    target_date.weekday(),  # day_of_week
                    target_date.month,      # month
                    target_date.day         # day_of_month
                ]
                
                # Add average values for other features
                if 'sales' in self.data:
                    sales_df = self.data['sales']
                    if 'item_count' in sales_df.columns:
                        features.append(sales_df['item_count'].mean())
                    if 'customer_rating' in sales_df.columns:
                        features.append(sales_df['customer_rating'].mean())
                
                # Make prediction
                X_pred = np.array(features).reshape(1, -1)
                X_pred_scaled = self.scalers['sales'].transform(X_pred)
                prediction = self.models['sales_forecast'].predict(X_pred_scaled)[0]
                
                forecasts.append({
                    "date": target_date.strftime("%Y-%m-%d"),
                    "predicted_sales": round(prediction, 2),
                    "confidence": 0.85,  # Placeholder confidence
                    "day_of_week": target_date.strftime("%A")
                })
            
            # Store predictions
            self.store_predictions(PredictionType.SALES_FORECAST, forecasts)
            
            track_user_action("ai_ml_engine", "sales_forecast_generated", f"Generated {days_ahead} day sales forecast")
            return forecasts
            
        except Exception as e:
            self.logger.error(f"Error generating sales forecast: {e}")
            return []
    
    def detect_anomalies(self) -> List[Dict[str, Any]]:
        """Detect anomalies in current data"""
        try:
            if not self.models_trained or 'anomaly_detection' not in self.models:
                return []
            
            anomalies = []
            
            if 'sales' in self.data and not self.data['sales'].empty:
                sales_df = self.data['sales'].copy()
                
                # Prepare features
                features = []
                if 'total_amount' in sales_df.columns:
                    features.append('total_amount')
                if 'quantity' in sales_df.columns:
                    features.append('quantity')
                if 'unit_price' in sales_df.columns:
                    features.append('unit_price')
                
                if features:
                    X = sales_df[features].fillna(0)
                    
                    # Detect anomalies
                    anomaly_scores = self.models['anomaly_detection'].decision_function(X)
                    anomaly_labels = self.models['anomaly_detection'].predict(X)
                    
                    # Find anomalous records
                    for i, (score, label) in enumerate(zip(anomaly_scores, anomaly_labels)):
                        if label == -1:  # Anomaly detected
                            anomaly_data = {
                                "index": i,
                                "anomaly_score": float(score),
                                "data": sales_df.iloc[i].to_dict(),
                                "type": "sales_anomaly",
                                "severity": "high" if score < -0.5 else "medium"
                            }
                            anomalies.append(anomaly_data)
            
            # Store anomalies as insights
            for anomaly in anomalies:
                self.store_insight(
                    InsightType.ANOMALY_DETECTION,
                    "sales",
                    f"Unusual {anomaly['type']} detected",
                    f"Anomaly score: {anomaly['anomaly_score']:.3f}",
                    0.9,
                    json.dumps(anomaly)
                )
            
            track_user_action("ai_ml_engine", "anomalies_detected", f"Detected {len(anomalies)} anomalies")
            return anomalies
            
        except Exception as e:
            self.logger.error(f"Error detecting anomalies: {e}")
            return []
    
    def generate_recommendations(self) -> List[Dict[str, Any]]:
        """Generate AI-powered business recommendations"""
        try:
            recommendations = []
            top_items = None  # Initialize to avoid UnboundLocalError

            # Analyze sales data for recommendations
            if 'sales' in self.data and not self.data['sales'].empty:
                sales_df = self.data['sales']

                # Top performing items
                if 'item_name' in sales_df.columns and 'total_amount' in sales_df.columns:
                    top_items = sales_df.groupby('item_name')['total_amount'].sum().sort_values(ascending=False).head(5)

                    recommendations.append({
                        "type": "menu_optimization",
                        "title": "Promote Top Performing Items",
                        "description": f"Focus marketing on top 5 items: {', '.join(top_items.index[:3])}",
                        "confidence": 0.85,
                        "impact": "high",
                        "data": top_items.to_dict()
                    })

                # Low performing items
                if top_items is not None and len(top_items) > 0:
                    low_items = sales_df.groupby('item_name')['total_amount'].sum().sort_values().head(3)
                    
                    recommendations.append({
                        "type": "menu_optimization",
                        "title": "Review Low Performing Items",
                        "description": f"Consider removing or improving: {', '.join(low_items.index)}",
                        "confidence": 0.75,
                        "impact": "medium",
                        "data": low_items.to_dict()
                    })
            
            # Inventory optimization recommendations
            if 'inventory' in self.data and not self.data['inventory'].empty:
                inventory_df = self.data['inventory']
                
                # Low stock items
                if 'current_stock' in inventory_df.columns and 'reorder_level' in inventory_df.columns:
                    low_stock = inventory_df[inventory_df['current_stock'] <= inventory_df['reorder_level']]
                    
                    if not low_stock.empty:
                        recommendations.append({
                            "type": "inventory_management",
                            "title": "Restock Low Inventory Items",
                            "description": f"Reorder {len(low_stock)} items below reorder level",
                            "confidence": 0.95,
                            "impact": "high",
                            "data": low_stock['name'].tolist()
                        })
            
            # Store recommendations as insights
            for rec in recommendations:
                self.store_insight(
                    InsightType.RECOMMENDATION,
                    rec['type'],
                    rec['title'],
                    rec['description'],
                    rec['confidence'],
                    json.dumps(rec)
                )
            
            track_user_action("ai_ml_engine", "recommendations_generated", f"Generated {len(recommendations)} recommendations")
            return recommendations
            
        except Exception as e:
            self.logger.error(f"Error generating recommendations: {e}")
            return []
    
    def store_insight(self, insight_type: InsightType, category: str, title: str, 
                     description: str, confidence: float, data: str = None):
        """Store AI insight in database"""
        try:
            with sqlite3.connect(self.insights_db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    INSERT INTO ai_insights (insight_type, category, title, description, confidence, data)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (insight_type.value, category, title, description, confidence, data))
                
                conn.commit()
                
        except Exception as e:
            self.logger.error(f"Error storing AI insight: {e}")
    
    def store_predictions(self, prediction_type: PredictionType, predictions: List[Dict]):
        """Store predictions in database"""
        try:
            with sqlite3.connect(self.insights_db_path) as conn:
                cursor = conn.cursor()
                
                for pred in predictions:
                    cursor.execute("""
                        INSERT INTO predictions (prediction_type, target_date, predicted_value, 
                                               confidence, model_used, input_data)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (
                        prediction_type.value,
                        pred.get('date', ''),
                        pred.get('predicted_sales', 0),
                        pred.get('confidence', 0),
                        'sales_forecast',
                        json.dumps(pred)
                    ))
                
                conn.commit()
                
        except Exception as e:
            self.logger.error(f"Error storing predictions: {e}")
    
    def store_model_performance(self, training_results: Dict[str, Any]):
        """Store model performance metrics"""
        try:
            with sqlite3.connect(self.insights_db_path) as conn:
                cursor = conn.cursor()
                
                for model_name, result in training_results.items():
                    if 'error' not in result:
                        cursor.execute("""
                            INSERT INTO model_performance (model_name, model_type, mae, rmse, data_size)
                            VALUES (?, ?, ?, ?, ?)
                        """, (
                            model_name,
                            'regression' if 'forecast' in model_name or 'prediction' in model_name else 'classification',
                            result.get('mae', 0),
                            result.get('rmse', 0),
                            result.get('data_size', 0)
                        ))
                
                conn.commit()
                
        except Exception as e:
            self.logger.error(f"Error storing model performance: {e}")
    
    def get_ai_insights(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent AI insights"""
        try:
            with sqlite3.connect(self.insights_db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT insight_type, category, title, description, confidence, created_at
                    FROM ai_insights
                    WHERE is_active = 1
                    ORDER BY created_at DESC
                    LIMIT ?
                """, (limit,))
                
                insights = []
                for row in cursor.fetchall():
                    insights.append({
                        "type": row[0],
                        "category": row[1],
                        "title": row[2],
                        "description": row[3],
                        "confidence": row[4],
                        "created_at": row[5]
                    })
                
                return insights
                
        except Exception as e:
            self.logger.error(f"Error getting AI insights: {e}")
            return []
    
    def get_model_status(self) -> Dict[str, Any]:
        """Get current model training status and performance"""
        return {
            "models_trained": self.models_trained,
            "last_training_time": self.last_training_time.isoformat() if self.last_training_time else None,
            "available_models": list(self.models.keys()),
            "data_sources": list(self.data.keys()),
            "insights_count": len(self.get_ai_insights(100))
        }

# Global AI/ML engine instance
_ai_ml_engine = None

def get_ai_ml_engine(data: Dict[str, pd.DataFrame] = None):
    """Get global AI/ML engine instance"""
    global _ai_ml_engine
    if _ai_ml_engine is None and data is not None:
        _ai_ml_engine = AIMLEngine(data)
    return _ai_ml_engine
