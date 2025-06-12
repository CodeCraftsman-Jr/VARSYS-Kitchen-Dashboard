"""
Advanced Analytics Engine
Comprehensive business intelligence and analytics system for kitchen dashboard
"""

import os
import json
import logging
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import matplotlib.pyplot as plt
import seaborn as sns
from PySide6.QtCore import QObject, Signal, QTimer, QThread
from PySide6.QtWidgets import QApplication

# Import activity tracker
try:
    from .activity_tracker import track_user_action, track_performance_start, track_performance_end, track_system_event
except ImportError:
    def track_user_action(*args, **kwargs): pass
    def track_performance_start(*args, **kwargs): pass
    def track_performance_end(*args, **kwargs): pass
    def track_system_event(*args, **kwargs): pass

class AnalyticsMetric(Enum):
    """Types of analytics metrics"""
    REVENUE = "revenue"
    PROFIT = "profit"
    COST = "cost"
    INVENTORY_VALUE = "inventory_value"
    WASTE_COST = "waste_cost"
    EFFICIENCY = "efficiency"
    CUSTOMER_SATISFACTION = "customer_satisfaction"
    INGREDIENT_USAGE = "ingredient_usage"
    RECIPE_POPULARITY = "recipe_popularity"
    SEASONAL_TRENDS = "seasonal_trends"

class ReportType(Enum):
    """Types of reports"""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"
    CUSTOM = "custom"

@dataclass
class AnalyticsResult:
    """Data structure for analytics results"""
    metric: str
    value: float
    change_percentage: float
    trend: str  # "up", "down", "stable"
    period: str
    timestamp: str
    metadata: Optional[Dict] = None

@dataclass
class BusinessInsight:
    """Data structure for business insights"""
    title: str
    description: str
    impact: str  # "high", "medium", "low"
    category: str
    recommendation: str
    data_points: List[float]
    timestamp: str

class AnalyticsEngine(QObject):
    """
    Advanced analytics engine that provides:
    - Business intelligence metrics
    - Trend analysis and forecasting
    - Performance indicators
    - Cost analysis and optimization
    - Revenue and profit tracking
    - Inventory analytics
    - Waste analysis
    - Recipe performance metrics
    """

    analytics_updated = Signal(dict)
    insight_generated = Signal(BusinessInsight)

    def __init__(self, data: Dict[str, pd.DataFrame], parent=None):
        super().__init__(parent)
        self.logger = logging.getLogger(__name__)
        self.data = data

        # Analytics cache
        self.metrics_cache = {}
        self.insights_cache = []
        self.last_update = None

        # Configuration
        self.cache_duration = 300  # 5 minutes

        # Setup periodic analytics updates
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_analytics)
        self.update_timer.start(600000)  # Update every 10 minutes

        self.logger.info("Analytics Engine initialized")
        track_system_event("analytics_engine", "initialized", "Analytics engine started")

    def calculate_revenue_metrics(self, period_days: int = 30) -> Dict[str, AnalyticsResult]:
        """Calculate revenue-related metrics"""
        operation_id = f"revenue_metrics_{datetime.now().timestamp()}"
        track_performance_start(operation_id, "analytics_engine", "calculate_revenue_metrics")

        try:
            results = {}

            if 'sales' not in self.data or self.data['sales'].empty:
                return results

            sales_df = self.data['sales'].copy()

            # Ensure date column exists and is datetime
            if 'date' in sales_df.columns:
                sales_df['date'] = pd.to_datetime(sales_df['date'], errors='coerce')

                # Filter for the specified period
                end_date = datetime.now()
                start_date = end_date - timedelta(days=period_days)
                current_period = sales_df[
                    (sales_df['date'] >= start_date) & (sales_df['date'] <= end_date)
                ]

                # Previous period for comparison
                prev_start = start_date - timedelta(days=period_days)
                prev_end = start_date
                previous_period = sales_df[
                    (sales_df['date'] >= prev_start) & (sales_df['date'] < prev_end)
                ]

                # Total Revenue
                current_revenue = current_period['total_amount'].sum() if 'total_amount' in current_period.columns else 0
                previous_revenue = previous_period['total_amount'].sum() if 'total_amount' in previous_period.columns else 0

                revenue_change = ((current_revenue - previous_revenue) / previous_revenue * 100) if previous_revenue > 0 else 0
                revenue_trend = "up" if revenue_change > 5 else "down" if revenue_change < -5 else "stable"

                results['total_revenue'] = AnalyticsResult(
                    metric="total_revenue",
                    value=current_revenue,
                    change_percentage=revenue_change,
                    trend=revenue_trend,
                    period=f"{period_days}_days",
                    timestamp=datetime.now().isoformat(),
                    metadata={"previous_value": previous_revenue}
                )

                # Average Order Value
                current_orders = len(current_period)
                avg_order_value = current_revenue / current_orders if current_orders > 0 else 0

                prev_orders = len(previous_period)
                prev_avg_order = previous_revenue / prev_orders if prev_orders > 0 else 0

                aov_change = ((avg_order_value - prev_avg_order) / prev_avg_order * 100) if prev_avg_order > 0 else 0
                aov_trend = "up" if aov_change > 5 else "down" if aov_change < -5 else "stable"

                results['avg_order_value'] = AnalyticsResult(
                    metric="avg_order_value",
                    value=avg_order_value,
                    change_percentage=aov_change,
                    trend=aov_trend,
                    period=f"{period_days}_days",
                    timestamp=datetime.now().isoformat(),
                    metadata={"orders_count": current_orders}
                )

                # Daily Revenue Trend
                daily_revenue = current_period.groupby(current_period['date'].dt.date)['total_amount'].sum()
                revenue_trend_data = daily_revenue.values.tolist()

                results['daily_revenue_trend'] = AnalyticsResult(
                    metric="daily_revenue_trend",
                    value=daily_revenue.mean(),
                    change_percentage=0,  # Will be calculated based on trend
                    trend="stable",
                    period=f"{period_days}_days",
                    timestamp=datetime.now().isoformat(),
                    metadata={"trend_data": revenue_trend_data}
                )

            track_performance_end(operation_id, "analytics_engine", "calculate_revenue_metrics",
                                metadata={"metrics_calculated": len(results)})

            return results

        except Exception as e:
            self.logger.error(f"Error calculating revenue metrics: {e}")
            track_performance_end(operation_id, "analytics_engine", "calculate_revenue_metrics",
                                metadata={"error": str(e)})
            return {}

    def calculate_cost_metrics(self, period_days: int = 30) -> Dict[str, AnalyticsResult]:
        """Calculate cost-related metrics"""
        operation_id = f"cost_metrics_{datetime.now().timestamp()}"
        track_performance_start(operation_id, "analytics_engine", "calculate_cost_metrics")

        try:
            results = {}

            # Inventory costs
            if 'inventory' in self.data and not self.data['inventory'].empty:
                inventory_df = self.data['inventory'].copy()

                # Calculate total inventory value
                if 'cost_per_unit' in inventory_df.columns and 'quantity' in inventory_df.columns:
                    inventory_df['total_value'] = inventory_df['cost_per_unit'] * inventory_df['quantity']
                    total_inventory_value = inventory_df['total_value'].sum()

                    results['inventory_value'] = AnalyticsResult(
                        metric="inventory_value",
                        value=total_inventory_value,
                        change_percentage=0,  # Would need historical data
                        trend="stable",
                        period=f"{period_days}_days",
                        timestamp=datetime.now().isoformat(),
                        metadata={"items_count": len(inventory_df)}
                    )

            # Waste costs
            if 'waste' in self.data and not self.data['waste'].empty:
                waste_df = self.data['waste'].copy()

                if 'cost' in waste_df.columns:
                    total_waste_cost = waste_df['cost'].sum()

                    results['waste_cost'] = AnalyticsResult(
                        metric="waste_cost",
                        value=total_waste_cost,
                        change_percentage=0,  # Would need historical data
                        trend="stable",
                        period=f"{period_days}_days",
                        timestamp=datetime.now().isoformat(),
                        metadata={"waste_items": len(waste_df)}
                    )

            # Budget analysis
            if 'budget' in self.data and not self.data['budget'].empty:
                budget_df = self.data['budget'].copy()

                if 'amount' in budget_df.columns:
                    total_budget = budget_df['amount'].sum()

                    results['total_budget'] = AnalyticsResult(
                        metric="total_budget",
                        value=total_budget,
                        change_percentage=0,
                        trend="stable",
                        period=f"{period_days}_days",
                        timestamp=datetime.now().isoformat(),
                        metadata={"budget_categories": len(budget_df)}
                    )

            track_performance_end(operation_id, "analytics_engine", "calculate_cost_metrics",
                                metadata={"metrics_calculated": len(results)})

            return results

        except Exception as e:
            self.logger.error(f"Error calculating cost metrics: {e}")
            track_performance_end(operation_id, "analytics_engine", "calculate_cost_metrics",
                                metadata={"error": str(e)})
            return {}

    def calculate_inventory_analytics(self) -> Dict[str, AnalyticsResult]:
        """Calculate inventory analytics"""
        operation_id = f"inventory_analytics_{datetime.now().timestamp()}"
        track_performance_start(operation_id, "analytics_engine", "calculate_inventory_analytics")

        try:
            results = {}

            if 'inventory' not in self.data or self.data['inventory'].empty:
                return results

            inventory_df = self.data['inventory'].copy()

            # Low stock items
            if 'quantity' in inventory_df.columns:
                low_stock_threshold = 10  # Configurable
                low_stock_items = inventory_df[inventory_df['quantity'] < low_stock_threshold]

                results['low_stock_count'] = AnalyticsResult(
                    metric="low_stock_count",
                    value=len(low_stock_items),
                    change_percentage=0,
                    trend="stable",
                    period="current",
                    timestamp=datetime.now().isoformat(),
                    metadata={"threshold": low_stock_threshold, "items": low_stock_items['name'].tolist() if 'name' in low_stock_items.columns else []}
                )

            # Category distribution
            if 'category' in inventory_df.columns:
                category_counts = inventory_df['category'].value_counts()

                results['category_distribution'] = AnalyticsResult(
                    metric="category_distribution",
                    value=len(category_counts),
                    change_percentage=0,
                    trend="stable",
                    period="current",
                    timestamp=datetime.now().isoformat(),
                    metadata={"distribution": category_counts.to_dict()}
                )

            # Inventory turnover (if we had historical data)
            # This would require tracking inventory changes over time

            track_performance_end(operation_id, "analytics_engine", "calculate_inventory_analytics",
                                metadata={"metrics_calculated": len(results)})

            return results

        except Exception as e:
            self.logger.error(f"Error calculating inventory analytics: {e}")
            track_performance_end(operation_id, "analytics_engine", "calculate_inventory_analytics",
                                metadata={"error": str(e)})
            return {}

    def calculate_recipe_analytics(self) -> Dict[str, AnalyticsResult]:
        """Calculate recipe performance analytics"""
        operation_id = f"recipe_analytics_{datetime.now().timestamp()}"
        track_performance_start(operation_id, "analytics_engine", "calculate_recipe_analytics")

        try:
            results = {}

            if 'recipes' not in self.data or self.data['recipes'].empty:
                return results

            recipes_df = self.data['recipes'].copy()

            # Recipe count by category
            if 'category' in recipes_df.columns:
                category_counts = recipes_df['category'].value_counts()

                results['recipes_by_category'] = AnalyticsResult(
                    metric="recipes_by_category",
                    value=len(category_counts),
                    change_percentage=0,
                    trend="stable",
                    period="current",
                    timestamp=datetime.now().isoformat(),
                    metadata={"distribution": category_counts.to_dict()}
                )

            # Average preparation time
            if 'prep_time' in recipes_df.columns:
                avg_prep_time = recipes_df['prep_time'].mean()

                results['avg_prep_time'] = AnalyticsResult(
                    metric="avg_prep_time",
                    value=avg_prep_time,
                    change_percentage=0,
                    trend="stable",
                    period="current",
                    timestamp=datetime.now().isoformat(),
                    metadata={"unit": "minutes"}
                )

            # Recipe complexity (based on number of ingredients)
            if 'recipe_ingredients' in self.data and not self.data['recipe_ingredients'].empty:
                ingredients_df = self.data['recipe_ingredients'].copy()

                if 'recipe_id' in ingredients_df.columns:
                    complexity = ingredients_df.groupby('recipe_id').size()
                    avg_complexity = complexity.mean()

                    results['avg_recipe_complexity'] = AnalyticsResult(
                        metric="avg_recipe_complexity",
                        value=avg_complexity,
                        change_percentage=0,
                        trend="stable",
                        period="current",
                        timestamp=datetime.now().isoformat(),
                        metadata={"unit": "ingredients_per_recipe"}
                    )

            track_performance_end(operation_id, "analytics_engine", "calculate_recipe_analytics",
                                metadata={"metrics_calculated": len(results)})

            return results

        except Exception as e:
            self.logger.error(f"Error calculating recipe analytics: {e}")
            track_performance_end(operation_id, "analytics_engine", "calculate_recipe_analytics",
                                metadata={"error": str(e)})
            return {}

    def generate_business_insights(self, metrics: Dict[str, AnalyticsResult]) -> List[BusinessInsight]:
        """Generate actionable business insights from metrics"""
        insights = []

        try:
            # Revenue insights
            if 'total_revenue' in metrics:
                revenue_metric = metrics['total_revenue']
                if revenue_metric.change_percentage < -10:
                    insights.append(BusinessInsight(
                        title="Revenue Decline Alert",
                        description=f"Revenue has decreased by {abs(revenue_metric.change_percentage):.1f}% compared to the previous period.",
                        impact="high",
                        category="revenue",
                        recommendation="Review pricing strategy, analyze customer feedback, and consider promotional campaigns.",
                        data_points=[revenue_metric.value, revenue_metric.metadata.get('previous_value', 0)],
                        timestamp=datetime.now().isoformat()
                    ))
                elif revenue_metric.change_percentage > 15:
                    insights.append(BusinessInsight(
                        title="Strong Revenue Growth",
                        description=f"Revenue has increased by {revenue_metric.change_percentage:.1f}% compared to the previous period.",
                        impact="high",
                        category="revenue",
                        recommendation="Analyze successful strategies and scale them. Consider expanding popular offerings.",
                        data_points=[revenue_metric.value, revenue_metric.metadata.get('previous_value', 0)],
                        timestamp=datetime.now().isoformat()
                    ))

            # Inventory insights
            if 'low_stock_count' in metrics:
                low_stock = metrics['low_stock_count']
                if low_stock.value > 5:
                    insights.append(BusinessInsight(
                        title="Multiple Low Stock Items",
                        description=f"You have {int(low_stock.value)} items running low on stock.",
                        impact="medium",
                        category="inventory",
                        recommendation="Review and reorder low stock items to avoid stockouts. Consider implementing automatic reorder points.",
                        data_points=[low_stock.value],
                        timestamp=datetime.now().isoformat()
                    ))

            # Waste insights
            if 'waste_cost' in metrics:
                waste_metric = metrics['waste_cost']
                if waste_metric.value > 1000:  # Configurable threshold
                    insights.append(BusinessInsight(
                        title="High Waste Costs",
                        description=f"Food waste costs are at ${waste_metric.value:.2f}, which may be impacting profitability.",
                        impact="medium",
                        category="waste",
                        recommendation="Implement better inventory rotation, portion control, and waste tracking to reduce costs.",
                        data_points=[waste_metric.value],
                        timestamp=datetime.now().isoformat()
                    ))

            self.insights_cache = insights

            # Emit insights
            for insight in insights:
                self.insight_generated.emit(insight)

            return insights

        except Exception as e:
            self.logger.error(f"Error generating business insights: {e}")
            return []

    def update_analytics(self):
        """Update all analytics metrics"""
        try:
            track_user_action("analytics_engine", "update_analytics", "Updating analytics metrics")

            # Check if cache is still valid
            if (self.last_update and
                (datetime.now() - self.last_update).seconds < self.cache_duration):
                return self.metrics_cache

            # Calculate all metrics
            revenue_metrics = self.calculate_revenue_metrics()
            cost_metrics = self.calculate_cost_metrics()
            inventory_metrics = self.calculate_inventory_analytics()
            recipe_metrics = self.calculate_recipe_analytics()

            # Combine all metrics
            all_metrics = {
                **revenue_metrics,
                **cost_metrics,
                **inventory_metrics,
                **recipe_metrics
            }

            # Generate insights
            insights = self.generate_business_insights(all_metrics)

            # Update cache
            self.metrics_cache = all_metrics
            self.last_update = datetime.now()

            # Emit updated analytics
            self.analytics_updated.emit(all_metrics)

            self.logger.info(f"Analytics updated: {len(all_metrics)} metrics, {len(insights)} insights")

            return all_metrics

        except Exception as e:
            self.logger.error(f"Error updating analytics: {e}")
            return {}

    def get_metrics(self, force_refresh: bool = False) -> Dict[str, AnalyticsResult]:
        """Get current analytics metrics"""
        if force_refresh or not self.metrics_cache:
            return self.update_analytics()
        return self.metrics_cache

    def get_insights(self) -> List[BusinessInsight]:
        """Get current business insights"""
        return self.insights_cache

    def export_analytics_report(self, file_path: str, report_type: ReportType = ReportType.MONTHLY) -> bool:
        """Export analytics report to file"""
        try:
            metrics = self.get_metrics(force_refresh=True)
            insights = self.get_insights()

            report_data = {
                "report_type": report_type.value,
                "generated_at": datetime.now().isoformat(),
                "metrics": {k: asdict(v) for k, v in metrics.items()},
                "insights": [asdict(insight) for insight in insights],
                "summary": {
                    "total_metrics": len(metrics),
                    "total_insights": len(insights),
                    "high_impact_insights": len([i for i in insights if i.impact == "high"])
                }
            }

            with open(file_path, 'w') as f:
                json.dump(report_data, f, indent=2)

            track_user_action("analytics_engine", "export_report", f"Exported analytics report to {file_path}")
            return True

        except Exception as e:
            self.logger.error(f"Error exporting analytics report: {e}")
            return False

# Global analytics engine instance
_analytics_engine = None

def get_analytics_engine(data: Dict[str, pd.DataFrame] = None):
    """Get global analytics engine instance"""
    global _analytics_engine
    if _analytics_engine is None and data is not None:
        _analytics_engine = AnalyticsEngine(data)
    return _analytics_engine