#!/usr/bin/env python3
"""
Notification Business Intelligence System
Advanced analytics, reporting, and business insights for notifications
"""

import sys
import os
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import statistics
import math

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from modules.enhanced_notification_system import get_notification_manager

class MetricType(Enum):
    """Types of business metrics"""
    VOLUME = "volume"
    ENGAGEMENT = "engagement"
    PERFORMANCE = "performance"
    EFFICIENCY = "efficiency"
    QUALITY = "quality"
    COST = "cost"

class TimeGranularity(Enum):
    """Time granularity for analytics"""
    MINUTE = "minute"
    HOUR = "hour"
    DAY = "day"
    WEEK = "week"
    MONTH = "month"
    QUARTER = "quarter"
    YEAR = "year"

@dataclass
class BusinessMetric:
    """Business metric definition"""
    metric_id: str
    name: str
    description: str
    metric_type: MetricType
    value: float
    unit: str
    target_value: Optional[float] = None
    threshold_warning: Optional[float] = None
    threshold_critical: Optional[float] = None
    trend: Optional[str] = None  # "up", "down", "stable"
    change_percent: Optional[float] = None

@dataclass
class AnalyticsReport:
    """Comprehensive analytics report"""
    report_id: str
    title: str
    generated_at: datetime
    period_start: datetime
    period_end: datetime
    metrics: List[BusinessMetric]
    insights: List[str]
    recommendations: List[str]
    charts_data: Dict[str, Any]
    executive_summary: str

class NotificationBusinessIntelligence:
    """Advanced business intelligence for notification system"""
    
    def __init__(self):
        self.notification_manager = get_notification_manager()
        self.historical_data = []
        self.kpi_targets = self._load_kpi_targets()
        self.cost_model = self._load_cost_model()
        
    def _load_kpi_targets(self) -> Dict[str, float]:
        """Load KPI targets for business metrics"""
        return {
            'notification_volume_daily': 1000,
            'response_rate_percent': 85.0,
            'resolution_time_minutes': 30.0,
            'user_satisfaction_score': 4.5,
            'system_availability_percent': 99.9,
            'cost_per_notification': 0.05,
            'false_positive_rate_percent': 5.0,
            'escalation_rate_percent': 10.0
        }
    
    def _load_cost_model(self) -> Dict[str, float]:
        """Load cost model for notification operations"""
        return {
            'notification_processing': 0.001,  # per notification
            'storage_per_gb_month': 0.10,
            'bandwidth_per_gb': 0.05,
            'sms_cost': 0.04,  # per SMS
            'email_cost': 0.001,  # per email
            'push_notification_cost': 0.0001,  # per push
            'staff_cost_per_hour': 50.0,
            'infrastructure_monthly': 500.0
        }
    
    def generate_comprehensive_report(self, start_date: datetime, 
                                    end_date: datetime) -> AnalyticsReport:
        """Generate comprehensive business intelligence report"""
        
        # Collect data
        notifications = self._get_notifications_in_period(start_date, end_date)
        
        # Calculate metrics
        metrics = self._calculate_business_metrics(notifications, start_date, end_date)
        
        # Generate insights
        insights = self._generate_insights(metrics, notifications)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(metrics, insights)
        
        # Prepare charts data
        charts_data = self._prepare_charts_data(notifications, start_date, end_date)
        
        # Generate executive summary
        executive_summary = self._generate_executive_summary(metrics, insights)
        
        report = AnalyticsReport(
            report_id=f"report_{int(time.time())}",
            title=f"Notification System Business Intelligence Report",
            generated_at=datetime.now(),
            period_start=start_date,
            period_end=end_date,
            metrics=metrics,
            insights=insights,
            recommendations=recommendations,
            charts_data=charts_data,
            executive_summary=executive_summary
        )
        
        return report
    
    def _get_notifications_in_period(self, start_date: datetime, 
                                   end_date: datetime) -> List[Dict[str, Any]]:
        """Get notifications within specified period"""
        all_notifications = self.notification_manager.get_notifications()
        
        period_notifications = []
        for notification in all_notifications:
            try:
                timestamp_str = notification.get('timestamp', '')
                if timestamp_str:
                    timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                    if start_date <= timestamp <= end_date:
                        period_notifications.append(notification)
            except:
                continue
        
        return period_notifications
    
    def _calculate_business_metrics(self, notifications: List[Dict[str, Any]], 
                                  start_date: datetime, 
                                  end_date: datetime) -> List[BusinessMetric]:
        """Calculate comprehensive business metrics"""
        metrics = []
        
        # Volume Metrics
        total_notifications = len(notifications)
        period_days = (end_date - start_date).days or 1
        daily_average = total_notifications / period_days
        
        metrics.append(BusinessMetric(
            metric_id="total_volume",
            name="Total Notifications",
            description="Total number of notifications sent in period",
            metric_type=MetricType.VOLUME,
            value=total_notifications,
            unit="notifications",
            target_value=self.kpi_targets.get('notification_volume_daily', 0) * period_days
        ))
        
        metrics.append(BusinessMetric(
            metric_id="daily_average",
            name="Daily Average Volume",
            description="Average notifications per day",
            metric_type=MetricType.VOLUME,
            value=daily_average,
            unit="notifications/day",
            target_value=self.kpi_targets.get('notification_volume_daily', 0)
        ))
        
        # Category Distribution
        category_counts = {}
        priority_distribution = []
        
        for notification in notifications:
            category = notification.get('category', 'unknown')
            category_counts[category] = category_counts.get(category, 0) + 1
            priority_distribution.append(notification.get('priority', 10))
        
        # Most active category
        if category_counts:
            most_active_category = max(category_counts, key=category_counts.get)
            category_percentage = (category_counts[most_active_category] / total_notifications) * 100
            
            metrics.append(BusinessMetric(
                metric_id="category_concentration",
                name="Category Concentration",
                description=f"Percentage of notifications in most active category ({most_active_category})",
                metric_type=MetricType.EFFICIENCY,
                value=category_percentage,
                unit="percent",
                threshold_warning=60.0,
                threshold_critical=80.0
            ))
        
        # Priority Analysis
        if priority_distribution:
            avg_priority = statistics.mean(priority_distribution)
            high_priority_count = sum(1 for p in priority_distribution if p <= 5)
            high_priority_rate = (high_priority_count / total_notifications) * 100
            
            metrics.append(BusinessMetric(
                metric_id="average_priority",
                name="Average Priority",
                description="Average priority level of notifications",
                metric_type=MetricType.QUALITY,
                value=avg_priority,
                unit="priority_level",
                target_value=8.0
            ))
            
            metrics.append(BusinessMetric(
                metric_id="high_priority_rate",
                name="High Priority Rate",
                description="Percentage of high priority notifications (priority ≤ 5)",
                metric_type=MetricType.QUALITY,
                value=high_priority_rate,
                unit="percent",
                target_value=15.0,
                threshold_warning=25.0,
                threshold_critical=40.0
            ))
        
        # Performance Metrics
        response_time_estimate = self._estimate_response_times(notifications)
        
        metrics.append(BusinessMetric(
            metric_id="estimated_response_time",
            name="Estimated Response Time",
            description="Estimated average response time for notifications",
            metric_type=MetricType.PERFORMANCE,
            value=response_time_estimate,
            unit="minutes",
            target_value=self.kpi_targets.get('resolution_time_minutes', 30)
        ))
        
        # Cost Metrics
        total_cost = self._calculate_total_cost(notifications, period_days)
        cost_per_notification = total_cost / max(total_notifications, 1)
        
        metrics.append(BusinessMetric(
            metric_id="total_cost",
            name="Total Operational Cost",
            description="Total cost of notification operations in period",
            metric_type=MetricType.COST,
            value=total_cost,
            unit="USD"
        ))
        
        metrics.append(BusinessMetric(
            metric_id="cost_per_notification",
            name="Cost per Notification",
            description="Average cost per notification",
            metric_type=MetricType.COST,
            value=cost_per_notification,
            unit="USD",
            target_value=self.kpi_targets.get('cost_per_notification', 0.05)
        ))
        
        # Efficiency Metrics
        system_efficiency = self._calculate_system_efficiency(notifications)
        
        metrics.append(BusinessMetric(
            metric_id="system_efficiency",
            name="System Efficiency Score",
            description="Overall system efficiency based on multiple factors",
            metric_type=MetricType.EFFICIENCY,
            value=system_efficiency,
            unit="score",
            target_value=85.0,
            threshold_warning=70.0,
            threshold_critical=50.0
        ))
        
        # Add trends to metrics
        self._add_trends_to_metrics(metrics)
        
        return metrics
    
    def _estimate_response_times(self, notifications: List[Dict[str, Any]]) -> float:
        """Estimate response times based on priority and category"""
        if not notifications:
            return 0.0
        
        response_times = []
        for notification in notifications:
            priority = notification.get('priority', 10)
            category = notification.get('category', 'info')
            
            # Base response time by priority
            if priority <= 3:
                base_time = 15  # Critical
            elif priority <= 6:
                base_time = 60  # High
            elif priority <= 10:
                base_time = 240  # Medium
            else:
                base_time = 480  # Low
            
            # Adjust by category
            category_multipliers = {
                'emergency': 0.5,
                'critical': 0.7,
                'security': 0.8,
                'error': 1.0,
                'warning': 1.2,
                'info': 1.5
            }
            
            multiplier = category_multipliers.get(category, 1.0)
            estimated_time = base_time * multiplier
            response_times.append(estimated_time)
        
        return statistics.mean(response_times)
    
    def _calculate_total_cost(self, notifications: List[Dict[str, Any]], 
                            period_days: int) -> float:
        """Calculate total operational cost"""
        total_cost = 0.0
        
        # Processing costs
        total_cost += len(notifications) * self.cost_model['notification_processing']
        
        # Infrastructure costs (prorated)
        total_cost += (self.cost_model['infrastructure_monthly'] / 30) * period_days
        
        # Storage costs (estimated)
        storage_gb = len(notifications) * 0.001  # 1KB per notification
        total_cost += storage_gb * self.cost_model['storage_per_gb_month'] * (period_days / 30)
        
        # Channel-specific costs (estimated distribution)
        push_notifications = len(notifications) * 0.7  # 70% push
        email_notifications = len(notifications) * 0.2  # 20% email
        sms_notifications = len(notifications) * 0.1   # 10% SMS
        
        total_cost += push_notifications * self.cost_model['push_notification_cost']
        total_cost += email_notifications * self.cost_model['email_cost']
        total_cost += sms_notifications * self.cost_model['sms_cost']
        
        return round(total_cost, 2)
    
    def _calculate_system_efficiency(self, notifications: List[Dict[str, Any]]) -> float:
        """Calculate overall system efficiency score"""
        if not notifications:
            return 0.0
        
        efficiency_factors = []
        
        # Priority distribution efficiency (balanced is better)
        priority_distribution = [n.get('priority', 10) for n in notifications]
        priority_variance = statistics.variance(priority_distribution) if len(priority_distribution) > 1 else 0
        priority_efficiency = max(0, 100 - (priority_variance / 10))
        efficiency_factors.append(priority_efficiency)
        
        # Category distribution efficiency
        categories = [n.get('category', 'unknown') for n in notifications]
        unique_categories = len(set(categories))
        category_efficiency = min(100, unique_categories * 10)  # More categories = better coverage
        efficiency_factors.append(category_efficiency)
        
        # Temporal distribution efficiency
        timestamps = []
        for n in notifications:
            try:
                timestamp_str = n.get('timestamp', '')
                if timestamp_str:
                    timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                    timestamps.append(timestamp.hour)
            except:
                continue
        
        if timestamps:
            hour_variance = statistics.variance(timestamps) if len(timestamps) > 1 else 0
            temporal_efficiency = max(0, 100 - (hour_variance / 2))
            efficiency_factors.append(temporal_efficiency)
        
        return statistics.mean(efficiency_factors) if efficiency_factors else 0.0
    
    def _add_trends_to_metrics(self, metrics: List[BusinessMetric]):
        """Add trend analysis to metrics"""
        # Simplified trend analysis (in production, compare with historical data)
        for metric in metrics:
            if metric.target_value:
                if metric.value >= metric.target_value * 1.1:
                    metric.trend = "up"
                    metric.change_percent = ((metric.value - metric.target_value) / metric.target_value) * 100
                elif metric.value <= metric.target_value * 0.9:
                    metric.trend = "down"
                    metric.change_percent = ((metric.target_value - metric.value) / metric.target_value) * -100
                else:
                    metric.trend = "stable"
                    metric.change_percent = 0.0
    
    def _generate_insights(self, metrics: List[BusinessMetric], 
                          notifications: List[Dict[str, Any]]) -> List[str]:
        """Generate business insights from metrics"""
        insights = []
        
        # Volume insights
        volume_metric = next((m for m in metrics if m.metric_id == "total_volume"), None)
        if volume_metric and volume_metric.target_value:
            if volume_metric.value > volume_metric.target_value:
                insights.append(f"Notification volume is {volume_metric.change_percent:.1f}% above target, indicating high system activity")
            elif volume_metric.value < volume_metric.target_value * 0.8:
                insights.append(f"Notification volume is {abs(volume_metric.change_percent):.1f}% below target, suggesting potential underutilization")
        
        # Priority insights
        priority_metric = next((m for m in metrics if m.metric_id == "high_priority_rate"), None)
        if priority_metric:
            if priority_metric.value > 30:
                insights.append(f"High priority notification rate ({priority_metric.value:.1f}%) suggests potential alert fatigue risk")
            elif priority_metric.value < 5:
                insights.append(f"Very low high priority rate ({priority_metric.value:.1f}%) may indicate good system health")
        
        # Cost insights
        cost_metric = next((m for m in metrics if m.metric_id == "cost_per_notification"), None)
        if cost_metric and cost_metric.target_value:
            if cost_metric.value > cost_metric.target_value * 1.2:
                insights.append(f"Cost per notification ({cost_metric.value:.3f} USD) is significantly above target - optimization needed")
        
        # Efficiency insights
        efficiency_metric = next((m for m in metrics if m.metric_id == "system_efficiency"), None)
        if efficiency_metric:
            if efficiency_metric.value > 85:
                insights.append(f"System efficiency score ({efficiency_metric.value:.1f}) indicates excellent performance")
            elif efficiency_metric.value < 60:
                insights.append(f"System efficiency score ({efficiency_metric.value:.1f}) suggests need for optimization")
        
        return insights
    
    def _generate_recommendations(self, metrics: List[BusinessMetric], 
                                insights: List[str]) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []
        
        # Check each metric for recommendations
        for metric in metrics:
            if metric.threshold_critical and metric.value >= metric.threshold_critical:
                recommendations.append(f"CRITICAL: {metric.name} requires immediate attention - implement emergency measures")
            elif metric.threshold_warning and metric.value >= metric.threshold_warning:
                recommendations.append(f"WARNING: Monitor {metric.name} closely and prepare corrective actions")
        
        # Cost optimization recommendations
        cost_metric = next((m for m in metrics if m.metric_id == "cost_per_notification"), None)
        if cost_metric and cost_metric.target_value and cost_metric.value > cost_metric.target_value:
            recommendations.append("Consider implementing notification batching and deduplication to reduce costs")
        
        # Efficiency recommendations
        efficiency_metric = next((m for m in metrics if m.metric_id == "system_efficiency"), None)
        if efficiency_metric and efficiency_metric.value < 70:
            recommendations.append("Implement notification prioritization and filtering to improve system efficiency")
        
        # Volume recommendations
        volume_metric = next((m for m in metrics if m.metric_id == "daily_average"), None)
        if volume_metric and volume_metric.target_value:
            if volume_metric.value > volume_metric.target_value * 1.5:
                recommendations.append("High notification volume detected - consider implementing rate limiting")
        
        return recommendations
    
    def _prepare_charts_data(self, notifications: List[Dict[str, Any]], 
                           start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Prepare data for charts and visualizations"""
        charts_data = {}
        
        # Category distribution
        category_counts = {}
        for notification in notifications:
            category = notification.get('category', 'unknown')
            category_counts[category] = category_counts.get(category, 0) + 1
        
        charts_data['category_distribution'] = {
            'labels': list(category_counts.keys()),
            'values': list(category_counts.values())
        }
        
        # Priority distribution
        priority_counts = {}
        for notification in notifications:
            priority = notification.get('priority', 10)
            priority_range = f"{(priority//5)*5}-{(priority//5)*5+4}"
            priority_counts[priority_range] = priority_counts.get(priority_range, 0) + 1
        
        charts_data['priority_distribution'] = {
            'labels': list(priority_counts.keys()),
            'values': list(priority_counts.values())
        }
        
        # Hourly distribution
        hourly_counts = {str(i): 0 for i in range(24)}
        for notification in notifications:
            try:
                timestamp_str = notification.get('timestamp', '')
                if timestamp_str:
                    timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                    hour = str(timestamp.hour)
                    hourly_counts[hour] += 1
            except:
                continue
        
        charts_data['hourly_distribution'] = {
            'labels': list(hourly_counts.keys()),
            'values': list(hourly_counts.values())
        }
        
        return charts_data
    
    def _generate_executive_summary(self, metrics: List[BusinessMetric], 
                                  insights: List[str]) -> str:
        """Generate executive summary"""
        volume_metric = next((m for m in metrics if m.metric_id == "total_volume"), None)
        cost_metric = next((m for m in metrics if m.metric_id == "total_cost"), None)
        efficiency_metric = next((m for m in metrics if m.metric_id == "system_efficiency"), None)
        
        summary = f"""
EXECUTIVE SUMMARY

The notification system processed {volume_metric.value if volume_metric else 'N/A'} notifications during the reporting period. 

KEY HIGHLIGHTS:
• Total operational cost: ${cost_metric.value if cost_metric else 'N/A'}
• System efficiency score: {efficiency_metric.value:.1f}/100 if efficiency_metric else 'N/A'
• {len(insights)} key insights identified

BUSINESS IMPACT:
The notification system continues to be a critical component of operational efficiency. 
{insights[0] if insights else 'System performance is within normal parameters.'}

NEXT ACTIONS:
Review detailed metrics and implement recommended optimizations to maintain optimal performance.
        """.strip()
        
        return summary

def create_business_intelligence_demo():
    """Create business intelligence demo"""
    print("📊 Notification Business Intelligence Demo")
    print("=" * 60)
    
    bi_system = NotificationBusinessIntelligence()
    
    # Generate report for last 7 days
    end_date = datetime.now()
    start_date = end_date - timedelta(days=7)
    
    print(f"📈 Generating comprehensive BI report...")
    print(f"   Period: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
    
    report = bi_system.generate_comprehensive_report(start_date, end_date)
    
    print(f"\n📋 BUSINESS INTELLIGENCE REPORT")
    print(f"Report ID: {report.report_id}")
    print(f"Generated: {report.generated_at.strftime('%Y-%m-%d %H:%M:%S')}")
    
    print(f"\n📊 KEY BUSINESS METRICS:")
    for metric in report.metrics:
        status = ""
        if metric.threshold_critical and metric.value >= metric.threshold_critical:
            status = " 🔴 CRITICAL"
        elif metric.threshold_warning and metric.value >= metric.threshold_warning:
            status = " 🟡 WARNING"
        elif metric.target_value and metric.value >= metric.target_value:
            status = " 🟢 ON TARGET"
        
        trend_indicator = ""
        if metric.trend == "up":
            trend_indicator = " ↗️"
        elif metric.trend == "down":
            trend_indicator = " ↘️"
        elif metric.trend == "stable":
            trend_indicator = " ➡️"
        
        print(f"   • {metric.name}: {metric.value:.2f} {metric.unit}{status}{trend_indicator}")
        if metric.change_percent:
            print(f"     Change: {metric.change_percent:+.1f}% vs target")
    
    print(f"\n💡 BUSINESS INSIGHTS:")
    for i, insight in enumerate(report.insights, 1):
        print(f"   {i}. {insight}")
    
    print(f"\n🎯 RECOMMENDATIONS:")
    for i, recommendation in enumerate(report.recommendations, 1):
        print(f"   {i}. {recommendation}")
    
    print(f"\n📈 CHART DATA AVAILABLE:")
    for chart_name, chart_data in report.charts_data.items():
        print(f"   • {chart_name.replace('_', ' ').title()}: {len(chart_data['labels'])} data points")
    
    print(f"\n📋 EXECUTIVE SUMMARY:")
    print(report.executive_summary)
    
    print(f"\n✅ Business intelligence demo completed!")
    print(f"📊 Features: KPI tracking, cost analysis, efficiency metrics")
    print(f"💼 Capabilities: Executive reporting, trend analysis, recommendations")
    
    return bi_system, report

if __name__ == "__main__":
    create_business_intelligence_demo()
