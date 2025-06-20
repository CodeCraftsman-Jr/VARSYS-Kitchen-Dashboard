#!/usr/bin/env python3
"""
AI-Powered Notification Intelligence
Advanced AI features for smart notification processing and insights
"""

import sys
import os
import re
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
import hashlib
import random

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from modules.enhanced_notification_system import get_notification_manager

class NotificationSentiment(Enum):
    """Notification sentiment analysis results"""
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"
    URGENT = "urgent"
    CRITICAL = "critical"

class NotificationIntent(Enum):
    """Detected notification intent"""
    INFORMATIONAL = "informational"
    ACTION_REQUIRED = "action_required"
    ALERT = "alert"
    CONFIRMATION = "confirmation"
    WARNING = "warning"
    ERROR = "error"

@dataclass
class AIAnalysisResult:
    """AI analysis result for a notification"""
    sentiment: NotificationSentiment
    intent: NotificationIntent
    urgency_score: float  # 0.0 to 1.0
    confidence: float     # 0.0 to 1.0
    keywords: List[str]
    suggested_actions: List[str]
    similar_notifications: List[str]
    risk_level: str
    estimated_response_time: int  # minutes

class NotificationAI:
    """AI-powered notification analysis and intelligence"""
    
    def __init__(self):
        self.sentiment_keywords = self._load_sentiment_keywords()
        self.intent_patterns = self._load_intent_patterns()
        self.urgency_indicators = self._load_urgency_indicators()
        self.action_patterns = self._load_action_patterns()
        self.notification_history = []
        self.learning_data = {}
        
    def _load_sentiment_keywords(self) -> Dict[NotificationSentiment, List[str]]:
        """Load sentiment analysis keywords"""
        return {
            NotificationSentiment.POSITIVE: [
                'success', 'complete', 'finished', 'ready', 'available', 'working',
                'operational', 'restored', 'resolved', 'fixed', 'improved', 'optimized'
            ],
            NotificationSentiment.NEGATIVE: [
                'failed', 'error', 'broken', 'down', 'unavailable', 'lost', 'missing',
                'corrupted', 'damaged', 'expired', 'overdue', 'delayed'
            ],
            NotificationSentiment.URGENT: [
                'urgent', 'immediate', 'asap', 'emergency', 'critical', 'now',
                'quickly', 'immediately', 'priority', 'escalate'
            ],
            NotificationSentiment.CRITICAL: [
                'critical', 'severe', 'major', 'catastrophic', 'disaster', 'breach',
                'security', 'data loss', 'system down', 'outage'
            ]
        }
    
    def _load_intent_patterns(self) -> Dict[NotificationIntent, List[str]]:
        """Load intent detection patterns"""
        return {
            NotificationIntent.ACTION_REQUIRED: [
                r'please\s+\w+', r'need\s+to\s+\w+', r'must\s+\w+', r'should\s+\w+',
                r'action\s+required', r'approval\s+needed', r'review\s+required'
            ],
            NotificationIntent.ALERT: [
                r'alert', r'warning', r'attention', r'notice', r'detected',
                r'threshold\s+exceeded', r'limit\s+reached'
            ],
            NotificationIntent.CONFIRMATION: [
                r'confirmed', r'completed', r'successful', r'done', r'finished',
                r'processed', r'updated', r'saved'
            ],
            NotificationIntent.WARNING: [
                r'warning', r'caution', r'potential', r'risk', r'may\s+\w+',
                r'could\s+\w+', r'approaching'
            ],
            NotificationIntent.ERROR: [
                r'error', r'failed', r'exception', r'crash', r'timeout',
                r'connection\s+lost', r'unable\s+to'
            ]
        }
    
    def _load_urgency_indicators(self) -> List[Tuple[str, float]]:
        """Load urgency scoring indicators"""
        return [
            ('emergency', 1.0),
            ('critical', 0.9),
            ('urgent', 0.8),
            ('high priority', 0.7),
            ('immediate', 0.8),
            ('asap', 0.7),
            ('security', 0.8),
            ('breach', 0.9),
            ('down', 0.7),
            ('failed', 0.6),
            ('error', 0.5),
            ('warning', 0.4),
            ('info', 0.1),
            ('fyi', 0.1)
        ]
    
    def _load_action_patterns(self) -> Dict[str, List[str]]:
        """Load action suggestion patterns"""
        return {
            'system_error': [
                'Check system logs for detailed error information',
                'Restart the affected service',
                'Contact system administrator',
                'Verify system resources (CPU, memory, disk)'
            ],
            'security_alert': [
                'Review security logs immediately',
                'Check for unauthorized access attempts',
                'Verify user credentials and permissions',
                'Consider temporary access restrictions'
            ],
            'inventory_low': [
                'Place order for additional stock',
                'Check with suppliers for availability',
                'Review consumption patterns',
                'Consider alternative products'
            ],
            'staff_issue': [
                'Contact the staff member directly',
                'Review work schedule and assignments',
                'Check for coverage arrangements',
                'Update staff management system'
            ],
            'budget_exceeded': [
                'Review recent expenses and transactions',
                'Analyze budget allocation and usage',
                'Consider budget reallocation',
                'Implement expense controls'
            ]
        }
    
    def analyze_notification(self, notification: Dict[str, Any]) -> AIAnalysisResult:
        """Perform comprehensive AI analysis of a notification"""
        title = notification.get('title', '').lower()
        message = notification.get('message', '').lower()
        category = notification.get('category', '').lower()
        priority = notification.get('priority', 10)
        
        full_text = f"{title} {message}"
        
        # Sentiment analysis
        sentiment = self._analyze_sentiment(full_text)
        
        # Intent detection
        intent = self._detect_intent(full_text)
        
        # Urgency scoring
        urgency_score = self._calculate_urgency(full_text, priority, category)
        
        # Keyword extraction
        keywords = self._extract_keywords(full_text)
        
        # Action suggestions
        suggested_actions = self._suggest_actions(category, intent, keywords)
        
        # Find similar notifications
        similar_notifications = self._find_similar_notifications(notification)
        
        # Risk assessment
        risk_level = self._assess_risk(sentiment, urgency_score, category)
        
        # Response time estimation
        estimated_response_time = self._estimate_response_time(urgency_score, category)
        
        # Confidence calculation
        confidence = self._calculate_confidence(sentiment, intent, urgency_score)
        
        # Store for learning
        self._store_analysis_data(notification, {
            'sentiment': sentiment,
            'intent': intent,
            'urgency_score': urgency_score,
            'keywords': keywords
        })
        
        return AIAnalysisResult(
            sentiment=sentiment,
            intent=intent,
            urgency_score=urgency_score,
            confidence=confidence,
            keywords=keywords,
            suggested_actions=suggested_actions,
            similar_notifications=similar_notifications,
            risk_level=risk_level,
            estimated_response_time=estimated_response_time
        )
    
    def _analyze_sentiment(self, text: str) -> NotificationSentiment:
        """Analyze sentiment of notification text"""
        sentiment_scores = {}
        
        for sentiment, keywords in self.sentiment_keywords.items():
            score = sum(1 for keyword in keywords if keyword in text)
            sentiment_scores[sentiment] = score
        
        if sentiment_scores[NotificationSentiment.CRITICAL] > 0:
            return NotificationSentiment.CRITICAL
        elif sentiment_scores[NotificationSentiment.URGENT] > 0:
            return NotificationSentiment.URGENT
        elif sentiment_scores[NotificationSentiment.NEGATIVE] > sentiment_scores[NotificationSentiment.POSITIVE]:
            return NotificationSentiment.NEGATIVE
        elif sentiment_scores[NotificationSentiment.POSITIVE] > 0:
            return NotificationSentiment.POSITIVE
        else:
            return NotificationSentiment.NEUTRAL
    
    def _detect_intent(self, text: str) -> NotificationIntent:
        """Detect the intent of the notification"""
        intent_scores = {}
        
        for intent, patterns in self.intent_patterns.items():
            score = sum(1 for pattern in patterns if re.search(pattern, text, re.IGNORECASE))
            intent_scores[intent] = score
        
        if intent_scores:
            return max(intent_scores, key=intent_scores.get)
        else:
            return NotificationIntent.INFORMATIONAL
    
    def _calculate_urgency(self, text: str, priority: int, category: str) -> float:
        """Calculate urgency score based on multiple factors"""
        urgency_score = 0.0
        
        # Text-based urgency
        for indicator, score in self.urgency_indicators:
            if indicator in text:
                urgency_score = max(urgency_score, score)
        
        # Priority-based urgency (inverse relationship)
        priority_score = max(0, (20 - priority) / 20)
        urgency_score = max(urgency_score, priority_score)
        
        # Category-based urgency
        category_urgency = {
            'emergency': 1.0,
            'critical': 0.9,
            'security': 0.8,
            'error': 0.7,
            'warning': 0.5,
            'maintenance': 0.4,
            'info': 0.1
        }
        
        category_score = category_urgency.get(category, 0.3)
        urgency_score = max(urgency_score, category_score)
        
        return min(1.0, urgency_score)
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract important keywords from notification text"""
        # Simple keyword extraction (in production, use NLP libraries)
        words = re.findall(r'\b\w{4,}\b', text.lower())
        
        # Filter out common words
        stop_words = {
            'this', 'that', 'with', 'have', 'will', 'been', 'from', 'they',
            'know', 'want', 'been', 'good', 'much', 'some', 'time', 'very',
            'when', 'come', 'here', 'just', 'like', 'long', 'make', 'many',
            'over', 'such', 'take', 'than', 'them', 'well', 'were'
        }
        
        keywords = [word for word in words if word not in stop_words]
        
        # Return top keywords by frequency
        keyword_freq = {}
        for keyword in keywords:
            keyword_freq[keyword] = keyword_freq.get(keyword, 0) + 1
        
        return sorted(keyword_freq.keys(), key=lambda x: keyword_freq[x], reverse=True)[:5]
    
    def _suggest_actions(self, category: str, intent: NotificationIntent, keywords: List[str]) -> List[str]:
        """Suggest appropriate actions based on analysis"""
        actions = []
        
        # Category-based actions
        if category in self.action_patterns:
            actions.extend(self.action_patterns[category][:2])
        
        # Intent-based actions
        if intent == NotificationIntent.ACTION_REQUIRED:
            actions.append('Review the notification and take appropriate action')
        elif intent == NotificationIntent.ERROR:
            actions.append('Investigate the error and implement a fix')
        elif intent == NotificationIntent.WARNING:
            actions.append('Monitor the situation and prepare preventive measures')
        
        # Keyword-based actions
        for keyword in keywords:
            if keyword in ['password', 'login', 'access']:
                actions.append('Verify user credentials and access permissions')
                break
            elif keyword in ['backup', 'data', 'file']:
                actions.append('Check data integrity and backup status')
                break
            elif keyword in ['network', 'connection', 'server']:
                actions.append('Verify network connectivity and server status')
                break
        
        return list(set(actions))[:3]  # Remove duplicates and limit to 3
    
    def _find_similar_notifications(self, notification: Dict[str, Any]) -> List[str]:
        """Find similar notifications from history"""
        similar = []
        current_keywords = set(self._extract_keywords(
            f"{notification.get('title', '')} {notification.get('message', '')}"
        ))
        
        for hist_notification in self.notification_history[-50:]:  # Check last 50
            hist_keywords = set(self._extract_keywords(
                f"{hist_notification.get('title', '')} {hist_notification.get('message', '')}"
            ))
            
            # Calculate similarity based on keyword overlap
            if current_keywords and hist_keywords:
                similarity = len(current_keywords & hist_keywords) / len(current_keywords | hist_keywords)
                if similarity > 0.3:  # 30% similarity threshold
                    similar.append(hist_notification.get('title', 'Unknown'))
        
        return similar[:3]  # Return top 3 similar
    
    def _assess_risk(self, sentiment: NotificationSentiment, urgency_score: float, category: str) -> str:
        """Assess risk level of the notification"""
        if sentiment == NotificationSentiment.CRITICAL or urgency_score >= 0.8:
            return "HIGH"
        elif sentiment == NotificationSentiment.URGENT or urgency_score >= 0.6:
            return "MEDIUM"
        elif sentiment == NotificationSentiment.NEGATIVE or urgency_score >= 0.4:
            return "LOW"
        else:
            return "MINIMAL"
    
    def _estimate_response_time(self, urgency_score: float, category: str) -> int:
        """Estimate expected response time in minutes"""
        base_time = {
            'emergency': 5,
            'critical': 15,
            'security': 30,
            'error': 60,
            'warning': 120,
            'maintenance': 240,
            'info': 480
        }
        
        category_time = base_time.get(category, 120)
        
        # Adjust based on urgency
        if urgency_score >= 0.8:
            return min(category_time, 15)
        elif urgency_score >= 0.6:
            return min(category_time, 60)
        elif urgency_score >= 0.4:
            return category_time
        else:
            return category_time * 2
    
    def _calculate_confidence(self, sentiment: NotificationSentiment, 
                            intent: NotificationIntent, urgency_score: float) -> float:
        """Calculate confidence in the AI analysis"""
        confidence = 0.5  # Base confidence
        
        # Increase confidence based on clear indicators
        if sentiment in [NotificationSentiment.CRITICAL, NotificationSentiment.URGENT]:
            confidence += 0.2
        
        if intent != NotificationIntent.INFORMATIONAL:
            confidence += 0.1
        
        if urgency_score >= 0.7:
            confidence += 0.2
        
        return min(1.0, confidence)
    
    def _store_analysis_data(self, notification: Dict[str, Any], analysis: Dict[str, Any]):
        """Store analysis data for learning"""
        self.notification_history.append(notification)
        
        # Keep only recent history
        if len(self.notification_history) > 1000:
            self.notification_history = self.notification_history[-500:]
        
        # Store learning data
        category = notification.get('category', 'unknown')
        if category not in self.learning_data:
            self.learning_data[category] = []
        
        self.learning_data[category].append(analysis)
    
    def get_ai_insights(self) -> Dict[str, Any]:
        """Get AI insights and patterns from analyzed data"""
        insights = {
            'total_analyzed': len(self.notification_history),
            'category_patterns': {},
            'sentiment_distribution': {},
            'intent_distribution': {},
            'urgency_trends': [],
            'common_keywords': {},
            'response_time_analysis': {}
        }
        
        # Analyze patterns by category
        for category, analyses in self.learning_data.items():
            if analyses:
                avg_urgency = sum(a['urgency_score'] for a in analyses) / len(analyses)
                common_sentiment = max(set(a['sentiment'] for a in analyses), 
                                     key=lambda x: sum(1 for a in analyses if a['sentiment'] == x))
                
                insights['category_patterns'][category] = {
                    'average_urgency': round(avg_urgency, 2),
                    'common_sentiment': common_sentiment.value,
                    'total_notifications': len(analyses)
                }
        
        # Overall sentiment distribution
        all_sentiments = [a['sentiment'] for analyses in self.learning_data.values() for a in analyses]
        for sentiment in NotificationSentiment:
            count = sum(1 for s in all_sentiments if s == sentiment)
            insights['sentiment_distribution'][sentiment.value] = count
        
        # Overall intent distribution
        all_intents = [a['intent'] for analyses in self.learning_data.values() for a in analyses]
        for intent in NotificationIntent:
            count = sum(1 for i in all_intents if i == intent)
            insights['intent_distribution'][intent.value] = count
        
        return insights

def create_ai_demo():
    """Demonstrate AI-powered notification intelligence"""
    print("🤖 AI-Powered Notification Intelligence Demo")
    print("=" * 60)
    
    ai = NotificationAI()
    
    # Test notifications with various characteristics
    test_notifications = [
        {
            'id': 'ai_test_1',
            'title': 'Critical System Failure',
            'message': 'Database server has crashed and is unresponsive. Immediate action required to restore service.',
            'category': 'critical',
            'priority': 1
        },
        {
            'id': 'ai_test_2',
            'title': 'Low Stock Alert',
            'message': 'Coffee beans inventory is running low. Please place order with supplier soon.',
            'category': 'inventory',
            'priority': 8
        },
        {
            'id': 'ai_test_3',
            'title': 'Security Warning',
            'message': 'Multiple failed login attempts detected from IP 192.168.1.100. Review security logs.',
            'category': 'security',
            'priority': 4
        },
        {
            'id': 'ai_test_4',
            'title': 'Backup Completed',
            'message': 'Daily backup process completed successfully. All data has been saved.',
            'category': 'success',
            'priority': 12
        },
        {
            'id': 'ai_test_5',
            'title': 'Budget Exceeded',
            'message': 'Monthly food budget has been exceeded by 15%. Review expenses and consider cost controls.',
            'category': 'budget',
            'priority': 6
        }
    ]
    
    print(f"🧠 Analyzing {len(test_notifications)} notifications with AI:")
    
    for i, notification in enumerate(test_notifications, 1):
        print(f"\n{i}. Analyzing: {notification['title']}")
        
        analysis = ai.analyze_notification(notification)
        
        print(f"   🎭 Sentiment: {analysis.sentiment.value}")
        print(f"   🎯 Intent: {analysis.intent.value}")
        print(f"   ⚡ Urgency: {analysis.urgency_score:.2f}")
        print(f"   🎲 Confidence: {analysis.confidence:.2f}")
        print(f"   🏷️ Keywords: {', '.join(analysis.keywords[:3])}")
        print(f"   ⚠️ Risk Level: {analysis.risk_level}")
        print(f"   ⏱️ Est. Response: {analysis.estimated_response_time} minutes")
        
        if analysis.suggested_actions:
            print(f"   💡 Suggested Actions:")
            for action in analysis.suggested_actions[:2]:
                print(f"      • {action}")
        
        if analysis.similar_notifications:
            print(f"   🔗 Similar: {len(analysis.similar_notifications)} found")
    
    # Show AI insights
    print(f"\n🧠 AI Intelligence Insights:")
    insights = ai.get_ai_insights()
    
    print(f"   📊 Total Analyzed: {insights['total_analyzed']}")
    print(f"   📂 Categories: {len(insights['category_patterns'])}")
    
    if insights['sentiment_distribution']:
        print(f"   🎭 Sentiment Distribution:")
        for sentiment, count in insights['sentiment_distribution'].items():
            if count > 0:
                print(f"      • {sentiment.title()}: {count}")
    
    if insights['intent_distribution']:
        print(f"   🎯 Intent Distribution:")
        for intent, count in insights['intent_distribution'].items():
            if count > 0:
                print(f"      • {intent.replace('_', ' ').title()}: {count}")
    
    print(f"\n✅ AI intelligence demo completed!")
    print(f"🤖 AI Features: Sentiment analysis, intent detection, urgency scoring")
    print(f"💡 Smart Features: Action suggestions, similarity detection, risk assessment")
    
    return ai

if __name__ == "__main__":
    create_ai_demo()
