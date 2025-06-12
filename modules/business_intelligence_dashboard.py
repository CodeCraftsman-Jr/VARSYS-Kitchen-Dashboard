"""
Business Intelligence Dashboard
Advanced analytics and reporting dashboard with interactive visualizations
"""

import os
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import pandas as pd
import numpy as np
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QComboBox, QDateEdit, QTabWidget,
                             QScrollArea, QFrame, QGridLayout, QGroupBox,
                             QProgressBar, QTextEdit, QSplitter, QFileDialog,
                             QMessageBox, QTableWidget, QTableWidgetItem,
                             QHeaderView)
from PySide6.QtCore import Qt, Signal, QTimer, QDate, QThread
from PySide6.QtGui import QFont, QColor, QPalette, QPixmap, QPainter
# Import matplotlib with fallback
try:
    import matplotlib.pyplot as plt
    import seaborn as sns
    from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
    from matplotlib.figure import Figure
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    # Create dummy classes for fallback
    class Figure: pass
    class FigureCanvas: pass

# Import analytics engine
try:
    from .analytics_engine import get_analytics_engine, AnalyticsResult, BusinessInsight, ReportType
    from .activity_tracker import track_user_action, track_system_event
except ImportError:
    get_analytics_engine = None
    AnalyticsResult = None
    BusinessInsight = None
    ReportType = None
    def track_user_action(*args, **kwargs): pass
    def track_system_event(*args, **kwargs): pass

class MetricCard(QFrame):
    """Modern metric display card"""
    
    def __init__(self, title: str, value: str, change: str = "", trend: str = "stable", parent=None):
        super().__init__(parent)
        self.init_ui(title, value, change, trend)
    
    def init_ui(self, title: str, value: str, change: str, trend: str):
        """Initialize metric card UI"""
        self.setFixedHeight(120)
        self.setStyleSheet(self.get_card_style(trend))
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(8)
        
        # Title
        title_label = QLabel(title)
        title_label.setStyleSheet("color: #64748b; font-size: 12px; font-weight: 500;")
        layout.addWidget(title_label)
        
        # Value
        value_label = QLabel(value)
        value_label.setStyleSheet("color: #0f172a; font-size: 24px; font-weight: 700;")
        layout.addWidget(value_label)
        
        # Change indicator
        if change:
            change_layout = QHBoxLayout()
            
            # Trend indicator
            trend_indicator = QLabel("↗" if trend == "up" else "↘" if trend == "down" else "→")
            trend_indicator.setStyleSheet(f"color: {self.get_trend_color(trend)}; font-size: 16px; font-weight: 600;")
            change_layout.addWidget(trend_indicator)
            
            # Change text
            change_label = QLabel(change)
            change_label.setStyleSheet(f"color: {self.get_trend_color(trend)}; font-size: 12px; font-weight: 500;")
            change_layout.addWidget(change_label)
            
            change_layout.addStretch()
            layout.addLayout(change_layout)
        
        layout.addStretch()
    
    def get_card_style(self, trend: str):
        """Get card styling based on trend"""
        base_style = """
            QFrame {
                background-color: white;
                border: 1px solid #e2e8f0;
                border-radius: 12px;
                margin: 4px;
            }
            QFrame:hover {
                border-color: #cbd5e1;
                background-color: rgba(59, 130, 246, 0.05);
            }
        """
        
        if trend == "up":
            base_style += """
                QFrame {
                    border-left: 4px solid #10b981;
                }
            """
        elif trend == "down":
            base_style += """
                QFrame {
                    border-left: 4px solid #ef4444;
                }
            """
        else:
            base_style += """
                QFrame {
                    border-left: 4px solid #6b7280;
                }
            """
        
        return base_style
    
    def get_trend_color(self, trend: str):
        """Get color for trend"""
        colors = {
            "up": "#10b981",
            "down": "#ef4444",
            "stable": "#6b7280"
        }
        return colors.get(trend, "#6b7280")

class InsightCard(QFrame):
    """Business insight display card"""
    
    def __init__(self, insight: BusinessInsight, parent=None):
        super().__init__(parent)
        self.insight = insight
        self.init_ui()
    
    def init_ui(self):
        """Initialize insight card UI"""
        self.setStyleSheet(self.get_card_style())
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(8)
        
        # Header with impact indicator
        header_layout = QHBoxLayout()
        
        title_label = QLabel(self.insight.title)
        title_label.setStyleSheet("color: #0f172a; font-size: 14px; font-weight: 600;")
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        impact_label = QLabel(self.insight.impact.upper())
        impact_label.setStyleSheet(f"""
            color: {self.get_impact_color()};
            font-size: 10px;
            font-weight: 600;
            padding: 2px 8px;
            background-color: {self.get_impact_bg_color()};
            border-radius: 4px;
        """)
        header_layout.addWidget(impact_label)
        
        layout.addLayout(header_layout)
        
        # Description
        desc_label = QLabel(self.insight.description)
        desc_label.setStyleSheet("color: #475569; font-size: 12px; line-height: 1.4;")
        desc_label.setWordWrap(True)
        layout.addWidget(desc_label)
        
        # Recommendation
        rec_label = QLabel(f"💡 {self.insight.recommendation}")
        rec_label.setStyleSheet("color: #1e293b; font-size: 11px; font-style: italic; margin-top: 4px;")
        rec_label.setWordWrap(True)
        layout.addWidget(rec_label)
    
    def get_card_style(self):
        """Get card styling based on impact"""
        base_style = """
            QFrame {
                background-color: white;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                margin: 2px;
            }
            QFrame:hover {
                border-color: #cbd5e1;
            }
        """
        
        if self.insight.impact == "high":
            base_style += "QFrame { border-left: 4px solid #ef4444; }"
        elif self.insight.impact == "medium":
            base_style += "QFrame { border-left: 4px solid #f59e0b; }"
        else:
            base_style += "QFrame { border-left: 4px solid #3b82f6; }"
        
        return base_style
    
    def get_impact_color(self):
        """Get color for impact level"""
        colors = {
            "high": "#dc2626",
            "medium": "#d97706",
            "low": "#2563eb"
        }
        return colors.get(self.insight.impact, "#6b7280")
    
    def get_impact_bg_color(self):
        """Get background color for impact level"""
        colors = {
            "high": "rgba(239, 68, 68, 0.1)",
            "medium": "rgba(245, 158, 11, 0.1)",
            "low": "rgba(59, 130, 246, 0.1)"
        }
        return colors.get(self.insight.impact, "rgba(107, 114, 128, 0.1)")

class ChartWidget(QWidget):
    """Custom chart widget using matplotlib"""

    def __init__(self, parent=None):
        super().__init__(parent)

        if MATPLOTLIB_AVAILABLE:
            self.figure = Figure(figsize=(8, 6), dpi=100)
            self.canvas = FigureCanvas(self.figure)

            layout = QVBoxLayout(self)
            layout.addWidget(self.canvas)

            # Set matplotlib style
            try:
                plt.style.use('seaborn-v0_8-whitegrid')
            except:
                # Fallback to default style
                pass
            self.figure.patch.set_facecolor('white')
        else:
            # Fallback to simple label
            layout = QVBoxLayout(self)
            fallback_label = QLabel("Charts require matplotlib\nInstall with: pip install matplotlib")
            fallback_label.setAlignment(Qt.AlignCenter)
            fallback_label.setStyleSheet("color: #64748b; font-size: 14px; padding: 40px;")
            layout.addWidget(fallback_label)
    
    def plot_revenue_trend(self, data: List[float], labels: List[str] = None):
        """Plot revenue trend chart"""
        if not MATPLOTLIB_AVAILABLE:
            return

        self.figure.clear()
        ax = self.figure.add_subplot(111)
        
        if not labels:
            labels = [f"Day {i+1}" for i in range(len(data))]
        
        ax.plot(labels, data, marker='o', linewidth=2, markersize=6, color='#3b82f6')
        ax.fill_between(labels, data, alpha=0.3, color='#3b82f6')
        
        ax.set_title('Revenue Trend', fontsize=14, fontweight='bold', pad=20)
        ax.set_ylabel('Revenue ($)', fontsize=12)
        ax.grid(True, alpha=0.3)
        
        # Rotate x-axis labels if needed
        if len(labels) > 7:
            plt.setp(ax.get_xticklabels(), rotation=45, ha='right')
        
        self.figure.tight_layout()
        self.canvas.draw()
    
    def plot_category_distribution(self, data: Dict[str, int]):
        """Plot category distribution pie chart"""
        if not MATPLOTLIB_AVAILABLE:
            return

        self.figure.clear()
        ax = self.figure.add_subplot(111)
        
        labels = list(data.keys())
        sizes = list(data.values())
        colors = plt.cm.Set3(np.linspace(0, 1, len(labels)))
        
        wedges, texts, autotexts = ax.pie(sizes, labels=labels, autopct='%1.1f%%', 
                                         colors=colors, startangle=90)
        
        ax.set_title('Category Distribution', fontsize=14, fontweight='bold', pad=20)
        
        # Improve text readability
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
        
        self.figure.tight_layout()
        self.canvas.draw()
    
    def plot_cost_breakdown(self, categories: List[str], values: List[float]):
        """Plot cost breakdown bar chart"""
        if not MATPLOTLIB_AVAILABLE:
            return

        self.figure.clear()
        ax = self.figure.add_subplot(111)
        
        bars = ax.bar(categories, values, color='#ef4444', alpha=0.7)
        
        # Add value labels on bars
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'${height:.0f}', ha='center', va='bottom', fontweight='bold')
        
        ax.set_title('Cost Breakdown', fontsize=14, fontweight='bold', pad=20)
        ax.set_ylabel('Cost ($)', fontsize=12)
        
        # Rotate x-axis labels if needed
        if len(categories) > 5:
            plt.setp(ax.get_xticklabels(), rotation=45, ha='right')
        
        self.figure.tight_layout()
        self.canvas.draw()

class BusinessIntelligenceDashboard(QWidget):
    """Advanced business intelligence dashboard"""
    
    def __init__(self, data: Dict[str, pd.DataFrame], parent=None):
        super().__init__(parent)
        self.logger = logging.getLogger(__name__)
        self.data = data
        
        # Initialize analytics engine
        if get_analytics_engine:
            self.analytics_engine = get_analytics_engine(data)
            if self.analytics_engine:
                self.analytics_engine.analytics_updated.connect(self.on_analytics_updated)
                self.analytics_engine.insight_generated.connect(self.on_insight_generated)
        else:
            self.analytics_engine = None
        
        # Initialize UI
        self.init_ui()
        
        # Load initial data
        self.refresh_dashboard()
        
        # Setup auto-refresh
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.refresh_dashboard)
        self.refresh_timer.start(300000)  # Refresh every 5 minutes
        
        self.logger.info("Business Intelligence Dashboard initialized")
        track_system_event("bi_dashboard", "initialized", "Business Intelligence Dashboard started")
    
    def init_ui(self):
        """Initialize the user interface"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Header
        self.create_header(layout)
        
        # Create tabs for different views
        self.create_tabs(layout)
    
    def create_header(self, parent_layout):
        """Create dashboard header"""
        header_layout = QHBoxLayout()
        
        # Title
        title_label = QLabel("Business Intelligence Dashboard")
        title_label.setStyleSheet("font-size: 28px; font-weight: 700; color: #0f172a;")
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        # Controls
        self.period_combo = QComboBox()
        self.period_combo.addItems(["Last 7 Days", "Last 30 Days", "Last 90 Days", "Last Year"])
        self.period_combo.setCurrentText("Last 30 Days")
        self.period_combo.currentTextChanged.connect(self.on_period_changed)
        self.period_combo.setStyleSheet("""
            QComboBox {
                padding: 8px 12px;
                border: 1px solid #d1d5db;
                border-radius: 6px;
                background-color: white;
                font-size: 12px;
            }
        """)
        header_layout.addWidget(self.period_combo)
        
        # Refresh button
        refresh_btn = QPushButton("Refresh")
        refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #3b82f6;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: 500;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #2563eb;
            }
        """)
        refresh_btn.clicked.connect(self.refresh_dashboard)
        header_layout.addWidget(refresh_btn)
        
        # Export button
        export_btn = QPushButton("Export Report")
        export_btn.setStyleSheet("""
            QPushButton {
                background-color: #10b981;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: 500;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #059669;
            }
        """)
        export_btn.clicked.connect(self.export_report)
        header_layout.addWidget(export_btn)
        
        parent_layout.addLayout(header_layout)
    
    def create_tabs(self, parent_layout):
        """Create tabbed interface"""
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabWidget::pane {
                background-color: white;
                border: 1px solid #e2e8f0;
                border-radius: 12px;
                margin-top: -1px;
            }
            QTabBar::tab {
                background-color: #f8fafc;
                border: 1px solid #e2e8f0;
                border-bottom: none;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                padding: 12px 20px;
                margin-right: 2px;
                font-size: 13px;
                font-weight: 500;
                color: #64748b;
            }
            QTabBar::tab:selected {
                background-color: white;
                border-bottom: 1px solid white;
                color: #0f172a;
            }
        """)
        
        # Overview tab
        self.create_overview_tab()
        
        # Revenue Analytics tab
        self.create_revenue_tab()
        
        # Cost Analysis tab
        self.create_cost_tab()
        
        # Inventory Analytics tab
        self.create_inventory_tab()
        
        # Business Insights tab
        self.create_insights_tab()
        
        parent_layout.addWidget(self.tabs)
    
    def create_overview_tab(self):
        """Create overview tab with key metrics"""
        overview_widget = QWidget()
        layout = QVBoxLayout(overview_widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Key metrics grid
        metrics_group = QGroupBox("Key Performance Indicators")
        metrics_layout = QGridLayout(metrics_group)
        metrics_layout.setSpacing(16)
        
        # Placeholder metric cards (will be populated with real data)
        self.revenue_card = MetricCard("Total Revenue", "$0", "0%", "stable")
        self.profit_card = MetricCard("Profit Margin", "0%", "0%", "stable")
        self.orders_card = MetricCard("Total Orders", "0", "0%", "stable")
        self.avg_order_card = MetricCard("Avg Order Value", "$0", "0%", "stable")
        
        metrics_layout.addWidget(self.revenue_card, 0, 0)
        metrics_layout.addWidget(self.profit_card, 0, 1)
        metrics_layout.addWidget(self.orders_card, 1, 0)
        metrics_layout.addWidget(self.avg_order_card, 1, 1)
        
        layout.addWidget(metrics_group)
        
        # Charts section
        charts_splitter = QSplitter(Qt.Horizontal)
        
        # Revenue trend chart
        self.revenue_chart = ChartWidget()
        charts_splitter.addWidget(self.revenue_chart)
        
        # Category distribution chart
        self.category_chart = ChartWidget()
        charts_splitter.addWidget(self.category_chart)
        
        layout.addWidget(charts_splitter)
        
        self.tabs.addTab(overview_widget, "Overview")
    
    def create_revenue_tab(self):
        """Create revenue analytics tab"""
        revenue_widget = QWidget()
        layout = QVBoxLayout(revenue_widget)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Revenue analytics content will be added here
        placeholder = QLabel("Revenue Analytics - Coming Soon")
        placeholder.setAlignment(Qt.AlignCenter)
        placeholder.setStyleSheet("color: #64748b; font-size: 16px;")
        layout.addWidget(placeholder)
        
        self.tabs.addTab(revenue_widget, "Revenue")
    
    def create_cost_tab(self):
        """Create cost analysis tab"""
        cost_widget = QWidget()
        layout = QVBoxLayout(cost_widget)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Cost analysis content will be added here
        placeholder = QLabel("Cost Analysis - Coming Soon")
        placeholder.setAlignment(Qt.AlignCenter)
        placeholder.setStyleSheet("color: #64748b; font-size: 16px;")
        layout.addWidget(placeholder)
        
        self.tabs.addTab(cost_widget, "Costs")
    
    def create_inventory_tab(self):
        """Create inventory analytics tab"""
        inventory_widget = QWidget()
        layout = QVBoxLayout(inventory_widget)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Inventory analytics content will be added here
        placeholder = QLabel("Inventory Analytics - Coming Soon")
        placeholder.setAlignment(Qt.AlignCenter)
        placeholder.setStyleSheet("color: #64748b; font-size: 16px;")
        layout.addWidget(placeholder)
        
        self.tabs.addTab(inventory_widget, "Inventory")
    
    def create_insights_tab(self):
        """Create business insights tab"""
        insights_widget = QWidget()
        layout = QVBoxLayout(insights_widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)
        
        # Insights header
        insights_header = QLabel("Business Insights & Recommendations")
        insights_header.setStyleSheet("font-size: 18px; font-weight: 600; color: #0f172a; margin-bottom: 10px;")
        layout.addWidget(insights_header)
        
        # Insights scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("QScrollArea { border: none; }")
        
        self.insights_widget = QWidget()
        self.insights_layout = QVBoxLayout(self.insights_widget)
        self.insights_layout.setSpacing(12)
        self.insights_layout.addStretch()
        
        scroll_area.setWidget(self.insights_widget)
        layout.addWidget(scroll_area)
        
        self.tabs.addTab(insights_widget, "Insights")
    
    def refresh_dashboard(self):
        """Refresh dashboard data"""
        try:
            track_user_action("bi_dashboard", "refresh", "Refreshing business intelligence dashboard")
            
            if not self.analytics_engine:
                self.logger.warning("Analytics engine not available")
                return
            
            # Get updated metrics
            metrics = self.analytics_engine.get_metrics(force_refresh=True)
            self.update_metric_cards(metrics)
            self.update_charts(metrics)
            
            # Get insights
            insights = self.analytics_engine.get_insights()
            self.update_insights(insights)
            
            self.logger.info("Dashboard refreshed successfully")
            
        except Exception as e:
            self.logger.error(f"Error refreshing dashboard: {e}")
    
    def update_metric_cards(self, metrics: Dict[str, AnalyticsResult]):
        """Update metric cards with latest data"""
        try:
            # Update revenue card
            if 'total_revenue' in metrics:
                revenue = metrics['total_revenue']
                self.revenue_card = MetricCard(
                    "Total Revenue",
                    f"${revenue.value:,.2f}",
                    f"{revenue.change_percentage:+.1f}%",
                    revenue.trend
                )
            
            # Update average order value card
            if 'avg_order_value' in metrics:
                aov = metrics['avg_order_value']
                self.avg_order_card = MetricCard(
                    "Avg Order Value",
                    f"${aov.value:.2f}",
                    f"{aov.change_percentage:+.1f}%",
                    aov.trend
                )
            
        except Exception as e:
            self.logger.error(f"Error updating metric cards: {e}")
    
    def update_charts(self, metrics: Dict[str, AnalyticsResult]):
        """Update charts with latest data"""
        try:
            # Update revenue trend chart
            if 'daily_revenue_trend' in metrics:
                trend_data = metrics['daily_revenue_trend'].metadata.get('trend_data', [])
                if trend_data:
                    self.revenue_chart.plot_revenue_trend(trend_data)
            
            # Update category distribution chart
            if 'category_distribution' in metrics:
                distribution = metrics['category_distribution'].metadata.get('distribution', {})
                if distribution:
                    self.category_chart.plot_category_distribution(distribution)
            
        except Exception as e:
            self.logger.error(f"Error updating charts: {e}")
    
    def update_insights(self, insights: List[BusinessInsight]):
        """Update insights display"""
        try:
            # Clear existing insights
            for i in reversed(range(self.insights_layout.count())):
                child = self.insights_layout.itemAt(i).widget()
                if child and isinstance(child, InsightCard):
                    child.deleteLater()
            
            # Add new insights
            for insight in insights:
                insight_card = InsightCard(insight)
                self.insights_layout.insertWidget(0, insight_card)
            
            if not insights:
                no_insights_label = QLabel("No insights available at this time.")
                no_insights_label.setAlignment(Qt.AlignCenter)
                no_insights_label.setStyleSheet("color: #64748b; font-size: 14px; padding: 40px;")
                self.insights_layout.insertWidget(0, no_insights_label)
            
        except Exception as e:
            self.logger.error(f"Error updating insights: {e}")
    
    def on_analytics_updated(self, metrics: Dict[str, AnalyticsResult]):
        """Handle analytics update signal"""
        self.update_metric_cards(metrics)
        self.update_charts(metrics)
    
    def on_insight_generated(self, insight: BusinessInsight):
        """Handle new insight signal"""
        # Add new insight to the top
        insight_card = InsightCard(insight)
        self.insights_layout.insertWidget(0, insight_card)
    
    def on_period_changed(self, period: str):
        """Handle period selection change"""
        track_user_action("bi_dashboard", "period_changed", f"Changed analysis period to {period}")
        self.refresh_dashboard()
    
    def export_report(self):
        """Export analytics report"""
        try:
            file_path, _ = QFileDialog.getSaveFileName(
                self, "Export Analytics Report", 
                f"analytics_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                "JSON Files (*.json);;All Files (*)"
            )
            
            if file_path and self.analytics_engine:
                success = self.analytics_engine.export_analytics_report(file_path)
                if success:
                    QMessageBox.information(self, "Export Complete", f"Analytics report exported to {file_path}")
                    track_user_action("bi_dashboard", "export_report", f"Exported analytics report to {file_path}")
                else:
                    QMessageBox.warning(self, "Export Failed", "Failed to export analytics report")
        
        except Exception as e:
            self.logger.error(f"Error exporting report: {e}")
            QMessageBox.critical(self, "Export Error", f"Error exporting report: {str(e)}")
