"""
Advanced Reporting System
Comprehensive report generation with PDF export, Excel export, and automated scheduling
"""

import os
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
import pandas as pd
import numpy as np
from dataclasses import dataclass, asdict
from enum import Enum
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QComboBox, QDateEdit, QTabWidget,
                             QScrollArea, QFrame, QGridLayout, QGroupBox,
                             QProgressBar, QTextEdit, QSplitter, QFileDialog,
                             QMessageBox, QTableWidget, QTableWidgetItem,
                             QHeaderView, QCheckBox, QSpinBox, QFormLayout,
                             QLineEdit)
from PySide6.QtCore import Qt, Signal, QTimer, QDate, QThread
from PySide6.QtGui import QFont, QColor, QPalette

# Import for PDF generation
try:
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.lib import colors
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

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

class ReportFormat(Enum):
    """Report output formats"""
    PDF = "pdf"
    EXCEL = "excel"
    CSV = "csv"
    JSON = "json"

class ReportSection(Enum):
    """Report sections"""
    EXECUTIVE_SUMMARY = "executive_summary"
    REVENUE_ANALYSIS = "revenue_analysis"
    COST_ANALYSIS = "cost_analysis"
    INVENTORY_REPORT = "inventory_report"
    WASTE_ANALYSIS = "waste_analysis"
    RECIPE_PERFORMANCE = "recipe_performance"
    BUSINESS_INSIGHTS = "business_insights"
    RECOMMENDATIONS = "recommendations"

@dataclass
class ReportConfig:
    """Report configuration"""
    title: str
    format: ReportFormat
    sections: List[ReportSection]
    date_range: Tuple[datetime, datetime]
    include_charts: bool = True
    include_insights: bool = True
    include_recommendations: bool = True
    custom_filters: Optional[Dict] = None

class ReportGenerator(QThread):
    """Background thread for report generation"""
    
    progress_updated = Signal(int)
    report_completed = Signal(str)
    error_occurred = Signal(str)
    
    def __init__(self, config: ReportConfig, data: Dict[str, pd.DataFrame], analytics_engine, parent=None):
        super().__init__(parent)
        self.config = config
        self.data = data
        self.analytics_engine = analytics_engine
        self.logger = logging.getLogger(__name__)
    
    def run(self):
        """Generate report in background"""
        try:
            self.progress_updated.emit(10)
            
            # Generate report based on format
            if self.config.format == ReportFormat.PDF:
                output_path = self.generate_pdf_report()
            elif self.config.format == ReportFormat.EXCEL:
                output_path = self.generate_excel_report()
            elif self.config.format == ReportFormat.CSV:
                output_path = self.generate_csv_report()
            elif self.config.format == ReportFormat.JSON:
                output_path = self.generate_json_report()
            else:
                raise ValueError(f"Unsupported report format: {self.config.format}")
            
            self.progress_updated.emit(100)
            self.report_completed.emit(output_path)
            
        except Exception as e:
            self.logger.error(f"Error generating report: {e}")
            self.error_occurred.emit(str(e))
    
    def generate_pdf_report(self) -> str:
        """Generate PDF report"""
        if not REPORTLAB_AVAILABLE:
            raise ImportError("ReportLab is required for PDF generation")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{self.config.title.replace(' ', '_')}_{timestamp}.pdf"
        output_path = os.path.join("reports", filename)
        
        # Ensure reports directory exists
        os.makedirs("reports", exist_ok=True)
        
        # Create PDF document
        doc = SimpleDocTemplate(output_path, pagesize=A4)
        styles = getSampleStyleSheet()
        story = []
        
        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            alignment=1  # Center alignment
        )
        story.append(Paragraph(self.config.title, title_style))
        story.append(Spacer(1, 20))
        
        # Report metadata
        meta_data = [
            ['Report Generated:', datetime.now().strftime("%Y-%m-%d %H:%M:%S")],
            ['Date Range:', f"{self.config.date_range[0].strftime('%Y-%m-%d')} to {self.config.date_range[1].strftime('%Y-%m-%d')}"],
            ['Sections Included:', ', '.join([s.value.replace('_', ' ').title() for s in self.config.sections])]
        ]
        
        meta_table = Table(meta_data, colWidths=[2*inch, 4*inch])
        meta_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ]))
        story.append(meta_table)
        story.append(Spacer(1, 30))
        
        self.progress_updated.emit(30)
        
        # Generate sections
        for section in self.config.sections:
            story.extend(self.generate_pdf_section(section, styles))
            story.append(Spacer(1, 20))
        
        self.progress_updated.emit(80)
        
        # Build PDF
        doc.build(story)
        
        return output_path
    
    def generate_pdf_section(self, section: ReportSection, styles) -> List:
        """Generate a specific section for PDF report"""
        content = []
        
        # Section title
        content.append(Paragraph(section.value.replace('_', ' ').title(), styles['Heading2']))
        content.append(Spacer(1, 12))
        
        if section == ReportSection.EXECUTIVE_SUMMARY:
            content.extend(self.generate_executive_summary_pdf(styles))
        elif section == ReportSection.REVENUE_ANALYSIS:
            content.extend(self.generate_revenue_analysis_pdf(styles))
        elif section == ReportSection.COST_ANALYSIS:
            content.extend(self.generate_cost_analysis_pdf(styles))
        elif section == ReportSection.INVENTORY_REPORT:
            content.extend(self.generate_inventory_report_pdf(styles))
        elif section == ReportSection.BUSINESS_INSIGHTS:
            content.extend(self.generate_insights_pdf(styles))
        
        return content
    
    def generate_executive_summary_pdf(self, styles) -> List:
        """Generate executive summary section"""
        content = []
        
        if self.analytics_engine:
            metrics = self.analytics_engine.get_metrics()
            
            summary_text = "This report provides a comprehensive analysis of business performance. "
            
            if 'total_revenue' in metrics:
                revenue = metrics['total_revenue']
                summary_text += f"Total revenue for the period was ${revenue.value:,.2f}, "
                if revenue.change_percentage > 0:
                    summary_text += f"representing a {revenue.change_percentage:.1f}% increase from the previous period. "
                else:
                    summary_text += f"representing a {abs(revenue.change_percentage):.1f}% decrease from the previous period. "
            
            content.append(Paragraph(summary_text, styles['Normal']))
        else:
            content.append(Paragraph("Analytics data not available.", styles['Normal']))
        
        return content
    
    def generate_revenue_analysis_pdf(self, styles) -> List:
        """Generate revenue analysis section"""
        content = []
        
        if 'sales' in self.data and not self.data['sales'].empty:
            sales_df = self.data['sales']
            
            # Revenue summary table
            if 'total_amount' in sales_df.columns:
                total_revenue = sales_df['total_amount'].sum()
                avg_order = sales_df['total_amount'].mean()
                order_count = len(sales_df)
                
                revenue_data = [
                    ['Metric', 'Value'],
                    ['Total Revenue', f"${total_revenue:,.2f}"],
                    ['Average Order Value', f"${avg_order:.2f}"],
                    ['Total Orders', f"{order_count:,}"]
                ]
                
                revenue_table = Table(revenue_data, colWidths=[3*inch, 2*inch])
                revenue_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 12),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                content.append(revenue_table)
        else:
            content.append(Paragraph("No sales data available for analysis.", styles['Normal']))
        
        return content
    
    def generate_cost_analysis_pdf(self, styles) -> List:
        """Generate cost analysis section"""
        content = []
        
        cost_summary = "Cost analysis includes inventory costs, waste costs, and operational expenses. "
        
        if 'inventory' in self.data and not self.data['inventory'].empty:
            inventory_df = self.data['inventory']
            if 'cost_per_unit' in inventory_df.columns and 'quantity' in inventory_df.columns:
                inventory_df['total_cost'] = inventory_df['cost_per_unit'] * inventory_df['quantity']
                total_inventory_cost = inventory_df['total_cost'].sum()
                cost_summary += f"Total inventory value is ${total_inventory_cost:,.2f}. "
        
        if 'waste' in self.data and not self.data['waste'].empty:
            waste_df = self.data['waste']
            if 'cost' in waste_df.columns:
                total_waste_cost = waste_df['cost'].sum()
                cost_summary += f"Total waste cost is ${total_waste_cost:,.2f}. "
        
        content.append(Paragraph(cost_summary, styles['Normal']))
        
        return content
    
    def generate_inventory_report_pdf(self, styles) -> List:
        """Generate inventory report section"""
        content = []
        
        if 'inventory' in self.data and not self.data['inventory'].empty:
            inventory_df = self.data['inventory']
            
            # Low stock items
            if 'quantity' in inventory_df.columns:
                low_stock = inventory_df[inventory_df['quantity'] < 10]
                
                if not low_stock.empty:
                    content.append(Paragraph("Low Stock Items:", styles['Heading3']))
                    
                    low_stock_data = [['Item', 'Current Quantity', 'Category']]
                    for _, item in low_stock.iterrows():
                        low_stock_data.append([
                            item.get('name', 'Unknown'),
                            str(item.get('quantity', 0)),
                            item.get('category', 'Unknown')
                        ])
                    
                    low_stock_table = Table(low_stock_data, colWidths=[2*inch, 1.5*inch, 1.5*inch])
                    low_stock_table.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                        ('FONTSIZE', (0, 0), (-1, 0), 10),
                        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                        ('GRID', (0, 0), (-1, -1), 1, colors.black)
                    ]))
                    content.append(low_stock_table)
                else:
                    content.append(Paragraph("No low stock items found.", styles['Normal']))
        else:
            content.append(Paragraph("No inventory data available.", styles['Normal']))
        
        return content
    
    def generate_insights_pdf(self, styles) -> List:
        """Generate business insights section"""
        content = []
        
        if self.analytics_engine:
            insights = self.analytics_engine.get_insights()
            
            if insights:
                for insight in insights:
                    # Insight title
                    content.append(Paragraph(f"• {insight.title}", styles['Heading4']))
                    
                    # Insight description
                    content.append(Paragraph(insight.description, styles['Normal']))
                    
                    # Recommendation
                    if insight.recommendation:
                        rec_style = ParagraphStyle(
                            'Recommendation',
                            parent=styles['Normal'],
                            leftIndent=20,
                            fontName='Helvetica-Oblique'
                        )
                        content.append(Paragraph(f"Recommendation: {insight.recommendation}", rec_style))
                    
                    content.append(Spacer(1, 12))
            else:
                content.append(Paragraph("No business insights available at this time.", styles['Normal']))
        else:
            content.append(Paragraph("Analytics engine not available.", styles['Normal']))
        
        return content
    
    def generate_excel_report(self) -> str:
        """Generate Excel report"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{self.config.title.replace(' ', '_')}_{timestamp}.xlsx"
        output_path = os.path.join("reports", filename)
        
        # Ensure reports directory exists
        os.makedirs("reports", exist_ok=True)
        
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            # Summary sheet
            summary_data = {
                'Report Title': [self.config.title],
                'Generated At': [datetime.now().strftime("%Y-%m-%d %H:%M:%S")],
                'Date Range': [f"{self.config.date_range[0].strftime('%Y-%m-%d')} to {self.config.date_range[1].strftime('%Y-%m-%d')}"]
            }
            summary_df = pd.DataFrame(summary_data)
            summary_df.to_excel(writer, sheet_name='Summary', index=False)
            
            self.progress_updated.emit(40)
            
            # Data sheets
            for table_name, df in self.data.items():
                if not df.empty:
                    # Limit to 1000 rows for performance
                    export_df = df.head(1000) if len(df) > 1000 else df
                    export_df.to_excel(writer, sheet_name=table_name.title(), index=False)
            
            self.progress_updated.emit(70)
            
            # Analytics sheet
            if self.analytics_engine:
                metrics = self.analytics_engine.get_metrics()
                if metrics:
                    analytics_data = []
                    for metric_name, metric in metrics.items():
                        analytics_data.append({
                            'Metric': metric_name,
                            'Value': metric.value,
                            'Change %': metric.change_percentage,
                            'Trend': metric.trend,
                            'Period': metric.period,
                            'Timestamp': metric.timestamp
                        })
                    
                    analytics_df = pd.DataFrame(analytics_data)
                    analytics_df.to_excel(writer, sheet_name='Analytics', index=False)
        
        return output_path
    
    def generate_csv_report(self) -> str:
        """Generate CSV report (combined data)"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{self.config.title.replace(' ', '_')}_{timestamp}.csv"
        output_path = os.path.join("reports", filename)
        
        # Ensure reports directory exists
        os.makedirs("reports", exist_ok=True)
        
        # Combine all data into one CSV
        combined_data = []
        
        for table_name, df in self.data.items():
            if not df.empty:
                df_copy = df.copy()
                df_copy['source_table'] = table_name
                combined_data.append(df_copy)
        
        if combined_data:
            combined_df = pd.concat(combined_data, ignore_index=True, sort=False)
            combined_df.to_csv(output_path, index=False)
        else:
            # Create empty CSV with headers
            pd.DataFrame({'message': ['No data available']}).to_csv(output_path, index=False)
        
        return output_path
    
    def generate_json_report(self) -> str:
        """Generate JSON report"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{self.config.title.replace(' ', '_')}_{timestamp}.json"
        output_path = os.path.join("reports", filename)
        
        # Ensure reports directory exists
        os.makedirs("reports", exist_ok=True)
        
        report_data = {
            "report_metadata": {
                "title": self.config.title,
                "generated_at": datetime.now().isoformat(),
                "date_range": {
                    "start": self.config.date_range[0].isoformat(),
                    "end": self.config.date_range[1].isoformat()
                },
                "sections": [s.value for s in self.config.sections]
            },
            "data": {},
            "analytics": {},
            "insights": []
        }
        
        # Add data
        for table_name, df in self.data.items():
            if not df.empty:
                # Convert to dict, limiting rows for performance
                export_df = df.head(1000) if len(df) > 1000 else df
                report_data["data"][table_name] = export_df.to_dict('records')
        
        # Add analytics
        if self.analytics_engine:
            metrics = self.analytics_engine.get_metrics()
            report_data["analytics"] = {k: asdict(v) for k, v in metrics.items()}
            
            insights = self.analytics_engine.get_insights()
            report_data["insights"] = [asdict(insight) for insight in insights]
        
        with open(output_path, 'w') as f:
            json.dump(report_data, f, indent=2, default=str)
        
        return output_path

class AdvancedReporting(QWidget):
    """Advanced reporting interface"""
    
    def __init__(self, data: Dict[str, pd.DataFrame], parent=None):
        super().__init__(parent)
        self.logger = logging.getLogger(__name__)
        self.data = data
        
        # Get analytics engine
        if get_analytics_engine:
            self.analytics_engine = get_analytics_engine(data)
        else:
            self.analytics_engine = None
        
        # Initialize UI
        self.init_ui()
        
        self.logger.info("Advanced Reporting initialized")
        track_system_event("advanced_reporting", "initialized", "Advanced reporting system started")
    
    def init_ui(self):
        """Initialize the user interface"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Header
        header_label = QLabel("Advanced Reporting")
        header_label.setStyleSheet("font-size: 24px; font-weight: 700; color: #0f172a;")
        layout.addWidget(header_label)
        
        # Report configuration
        self.create_report_config(layout)
        
        # Progress and status
        self.create_progress_section(layout)
    
    def create_report_config(self, parent_layout):
        """Create report configuration section"""
        config_group = QGroupBox("Report Configuration")
        config_layout = QFormLayout(config_group)
        
        # Report title
        self.title_input = QLineEdit()
        self.title_input.setText("Business Analytics Report")
        self.title_input.setStyleSheet("padding: 8px; border: 1px solid #d1d5db; border-radius: 4px;")
        config_layout.addRow("Report Title:", self.title_input)
        
        # Report format
        self.format_combo = QComboBox()
        self.format_combo.addItems(["PDF", "Excel", "CSV", "JSON"])
        self.format_combo.setStyleSheet("padding: 8px; border: 1px solid #d1d5db; border-radius: 4px;")
        config_layout.addRow("Format:", self.format_combo)
        
        # Date range
        date_layout = QHBoxLayout()
        self.start_date = QDateEdit()
        self.start_date.setDate(QDate.currentDate().addDays(-30))
        self.start_date.setStyleSheet("padding: 8px; border: 1px solid #d1d5db; border-radius: 4px;")
        
        self.end_date = QDateEdit()
        self.end_date.setDate(QDate.currentDate())
        self.end_date.setStyleSheet("padding: 8px; border: 1px solid #d1d5db; border-radius: 4px;")
        
        date_layout.addWidget(self.start_date)
        date_layout.addWidget(QLabel("to"))
        date_layout.addWidget(self.end_date)
        config_layout.addRow("Date Range:", date_layout)
        
        # Report sections
        sections_layout = QVBoxLayout()
        self.section_checkboxes = {}
        
        sections = [
            ("Executive Summary", ReportSection.EXECUTIVE_SUMMARY),
            ("Revenue Analysis", ReportSection.REVENUE_ANALYSIS),
            ("Cost Analysis", ReportSection.COST_ANALYSIS),
            ("Inventory Report", ReportSection.INVENTORY_REPORT),
            ("Waste Analysis", ReportSection.WASTE_ANALYSIS),
            ("Recipe Performance", ReportSection.RECIPE_PERFORMANCE),
            ("Business Insights", ReportSection.BUSINESS_INSIGHTS),
            ("Recommendations", ReportSection.RECOMMENDATIONS)
        ]
        
        for display_name, section in sections:
            checkbox = QCheckBox(display_name)
            checkbox.setChecked(True)
            self.section_checkboxes[section] = checkbox
            sections_layout.addWidget(checkbox)
        
        config_layout.addRow("Include Sections:", sections_layout)
        
        # Generate button
        self.generate_btn = QPushButton("Generate Report")
        self.generate_btn.setStyleSheet("""
            QPushButton {
                background-color: #3b82f6;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 24px;
                font-weight: 600;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #2563eb;
            }
            QPushButton:disabled {
                background-color: #9ca3af;
            }
        """)
        self.generate_btn.clicked.connect(self.generate_report)
        config_layout.addRow("", self.generate_btn)
        
        parent_layout.addWidget(config_group)
    
    def create_progress_section(self, parent_layout):
        """Create progress and status section"""
        progress_group = QGroupBox("Report Generation Status")
        progress_layout = QVBoxLayout(progress_group)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #d1d5db;
                border-radius: 4px;
                text-align: center;
                height: 20px;
            }
            QProgressBar::chunk {
                background-color: #3b82f6;
                border-radius: 3px;
            }
        """)
        progress_layout.addWidget(self.progress_bar)
        
        # Status label
        self.status_label = QLabel("Ready to generate report")
        self.status_label.setStyleSheet("color: #64748b; font-size: 12px; padding: 8px;")
        progress_layout.addWidget(self.status_label)
        
        parent_layout.addWidget(progress_group)
    
    def generate_report(self):
        """Generate report based on configuration"""
        try:
            track_user_action("advanced_reporting", "generate_report", "Starting report generation")
            
            # Get configuration
            config = self.get_report_config()
            
            # Validate configuration
            if not config.sections:
                QMessageBox.warning(self, "Configuration Error", "Please select at least one report section.")
                return
            
            # Disable generate button and show progress
            self.generate_btn.setEnabled(False)
            self.progress_bar.setVisible(True)
            self.progress_bar.setValue(0)
            self.status_label.setText("Generating report...")
            
            # Start report generation in background
            self.report_generator = ReportGenerator(config, self.data, self.analytics_engine)
            self.report_generator.progress_updated.connect(self.on_progress_updated)
            self.report_generator.report_completed.connect(self.on_report_completed)
            self.report_generator.error_occurred.connect(self.on_report_error)
            self.report_generator.start()
            
        except Exception as e:
            self.logger.error(f"Error starting report generation: {e}")
            QMessageBox.critical(self, "Generation Error", f"Error starting report generation: {str(e)}")
            self.reset_ui()
    
    def get_report_config(self) -> ReportConfig:
        """Get current report configuration"""
        # Get selected sections
        selected_sections = []
        for section, checkbox in self.section_checkboxes.items():
            if checkbox.isChecked():
                selected_sections.append(section)
        
        # Get date range
        start_date = self.start_date.date().toPython()
        end_date = self.end_date.date().toPython()
        
        # Convert start_date to datetime
        start_datetime = datetime.combine(start_date, datetime.min.time())
        end_datetime = datetime.combine(end_date, datetime.max.time())
        
        # Get format
        format_text = self.format_combo.currentText().lower()
        report_format = ReportFormat(format_text)
        
        return ReportConfig(
            title=self.title_input.text(),
            format=report_format,
            sections=selected_sections,
            date_range=(start_datetime, end_datetime),
            include_charts=True,
            include_insights=True,
            include_recommendations=True
        )
    
    def on_progress_updated(self, value: int):
        """Handle progress update"""
        self.progress_bar.setValue(value)
    
    def on_report_completed(self, output_path: str):
        """Handle report completion"""
        self.status_label.setText(f"Report generated successfully: {output_path}")
        QMessageBox.information(self, "Report Complete", f"Report has been generated successfully!\n\nSaved to: {output_path}")
        track_user_action("advanced_reporting", "report_completed", f"Report generated: {output_path}")
        self.reset_ui()
    
    def on_report_error(self, error_message: str):
        """Handle report generation error"""
        self.status_label.setText(f"Error: {error_message}")
        QMessageBox.critical(self, "Report Error", f"Error generating report:\n\n{error_message}")
        self.reset_ui()
    
    def reset_ui(self):
        """Reset UI to initial state"""
        self.generate_btn.setEnabled(True)
        self.progress_bar.setVisible(False)
        self.progress_bar.setValue(0)
