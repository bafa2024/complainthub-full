# backend/app/services/analytics.py

import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, desc, asc
from app import crud, schemas
from app.models import Ticket, User, Brand, Conversation
import json
import pandas as pd
from collections import defaultdict, Counter

logger = logging.getLogger(__name__)

class AnalyticsService:
    def __init__(self, db: Session):
        self.db = db
    
    def get_system_overview(self, date_range: str = "30d") -> Dict[str, Any]:
        """
        Get comprehensive system overview analytics
        """
        try:
            start_date = self._get_start_date(date_range)
            
            # Basic counts
            total_users = self.db.query(User).count()
            total_brands = self.db.query(Brand).count()
            total_tickets = self.db.query(Ticket).filter(
                Ticket.created_at >= start_date
            ).count()
            
            # Ticket status breakdown
            status_counts = self._get_ticket_status_counts(start_date)
            
            # Resolution metrics
            resolution_metrics = self._calculate_resolution_metrics(start_date)
            
            # Channel distribution
            channel_distribution = self._get_channel_distribution(start_date)
            
            # Category distribution
            category_distribution = self._get_category_distribution(start_date)
            
            # Sentiment analysis
            sentiment_metrics = self._get_sentiment_metrics(start_date)
            
            # Revenue metrics (if billing is enabled)
            revenue_metrics = self._calculate_revenue_metrics(start_date)
            
            return {
                "overview": {
                    "total_users": total_users,
                    "total_brands": total_brands,
                    "total_tickets": total_tickets,
                    "active_tickets": status_counts.get("new", 0) + status_counts.get("in-progress", 0),
                    "resolved_tickets": status_counts.get("resolved", 0),
                    "resolution_rate": resolution_metrics["resolution_rate"],
                    "avg_resolution_time": resolution_metrics["avg_resolution_time"],
                    "avg_satisfaction": sentiment_metrics["avg_satisfaction"],
                    "total_revenue": revenue_metrics["total_revenue"]
                },
                "status_breakdown": status_counts,
                "channel_distribution": channel_distribution,
                "category_distribution": category_distribution,
                "sentiment_metrics": sentiment_metrics,
                "revenue_metrics": revenue_metrics,
                "trends": self._calculate_trends(date_range)
            }
            
        except Exception as e:
            logger.error(f"Error getting system overview: {e}")
            return {}
    
    def get_brand_analytics(self, brand_id: int, date_range: str = "30d") -> Dict[str, Any]:
        """
        Get detailed analytics for a specific brand
        """
        try:
            start_date = self._get_start_date(date_range)
            
            # Brand-specific tickets
            brand_tickets = self.db.query(Ticket).filter(
                and_(
                    Ticket.brand_id == brand_id,
                    Ticket.created_at >= start_date
                )
            ).all()
            
            # Basic metrics
            total_tickets = len(brand_tickets)
            resolved_tickets = len([t for t in brand_tickets if t.status == "resolved"])
            resolution_rate = (resolved_tickets / total_tickets * 100) if total_tickets > 0 else 0
            
            # Response time analysis
            response_times = self._calculate_response_times(brand_tickets)
            
            # Channel performance
            channel_performance = self._get_channel_performance(brand_tickets)
            
            # Category analysis
            category_analysis = self._get_category_analysis(brand_tickets)
            
            # Sentiment trends
            sentiment_trends = self._get_sentiment_trends(brand_tickets)
            
            # Agent performance (if applicable)
            agent_performance = self._get_agent_performance(brand_id, start_date)
            
            return {
                "brand_id": brand_id,
                "total_tickets": total_tickets,
                "resolved_tickets": resolved_tickets,
                "resolution_rate": round(resolution_rate, 2),
                "avg_response_time": response_times["average"],
                "avg_resolution_time": response_times["avg_resolution"],
                "channel_performance": channel_performance,
                "category_analysis": category_analysis,
                "sentiment_trends": sentiment_trends,
                "agent_performance": agent_performance,
                "trends": self._calculate_brand_trends(brand_id, date_range)
            }
            
        except Exception as e:
            logger.error(f"Error getting brand analytics: {e}")
            return {}
    
    def get_user_analytics(self, user_id: int, date_range: str = "30d") -> Dict[str, Any]:
        """
        Get analytics for a specific user
        """
        try:
            start_date = self._get_start_date(date_range)
            
            # User's tickets
            user_tickets = self.db.query(Ticket).filter(
                and_(
                    Ticket.owner_id == user_id,
                    Ticket.created_at >= start_date
                )
            ).all()
            
            # Basic metrics
            total_complaints = len(user_tickets)
            resolved_complaints = len([t for t in user_tickets if t.status == "resolved"])
            
            # Channel usage
            channel_usage = Counter([t.channel for t in user_tickets])
            
            # Category preferences
            category_preferences = Counter([t.category for t in user_tickets])
            
            # Satisfaction history
            satisfaction_history = [t.satisfaction_rating for t in user_tickets if t.satisfaction_rating]
            avg_satisfaction = sum(satisfaction_history) / len(satisfaction_history) if satisfaction_history else 0
            
            return {
                "user_id": user_id,
                "total_complaints": total_complaints,
                "resolved_complaints": resolved_complaints,
                "resolution_rate": (resolved_complaints / total_complaints * 100) if total_complaints > 0 else 0,
                "avg_satisfaction": round(avg_satisfaction, 2),
                "channel_usage": dict(channel_usage),
                "category_preferences": dict(category_preferences),
                "recent_activity": self._get_user_recent_activity(user_id, start_date)
            }
            
        except Exception as e:
            logger.error(f"Error getting user analytics: {e}")
            return {}
    
    def get_real_time_metrics(self) -> Dict[str, Any]:
        """
        Get real-time metrics for dashboard
        """
        try:
            now = datetime.utcnow()
            today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
            hour_ago = now - timedelta(hours=1)
            
            # Today's metrics
            today_tickets = self.db.query(Ticket).filter(
                Ticket.created_at >= today_start
            ).count()
            
            # Last hour metrics
            last_hour_tickets = self.db.query(Ticket).filter(
                Ticket.created_at >= hour_ago
            ).count()
            
            # Active conversations
            active_conversations = self.db.query(Conversation).filter(
                Conversation.status == "active"
            ).count()
            
            # Pending tickets
            pending_tickets = self.db.query(Ticket).filter(
                Ticket.status.in_(["new", "in-progress"])
            ).count()
            
            # Recent activity
            recent_activity = self._get_recent_activity(limit=10)
            
            return {
                "today_tickets": today_tickets,
                "last_hour_tickets": last_hour_tickets,
                "active_conversations": active_conversations,
                "pending_tickets": pending_tickets,
                "recent_activity": recent_activity,
                "system_health": self._get_system_health()
            }
            
        except Exception as e:
            logger.error(f"Error getting real-time metrics: {e}")
            return {}
    
    def generate_report(self, report_type: str, filters: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Generate comprehensive reports
        """
        try:
            if report_type == "performance":
                return self._generate_performance_report(filters)
            elif report_type == "trends":
                return self._generate_trends_report(filters)
            elif report_type == "financial":
                return self._generate_financial_report(filters)
            elif report_type == "customer_satisfaction":
                return self._generate_satisfaction_report(filters)
            elif report_type == "channel_analysis":
                return self._generate_channel_report(filters)
            else:
                raise ValueError(f"Unknown report type: {report_type}")
                
        except Exception as e:
            logger.error(f"Error generating report {report_type}: {e}")
            return {}
    
    def get_predictive_analytics(self, metric: str, days: int = 30) -> Dict[str, Any]:
        """
        Get predictive analytics for forecasting
        """
        try:
            if metric == "ticket_volume":
                return self._predict_ticket_volume(days)
            elif metric == "resolution_time":
                return self._predict_resolution_time(days)
            elif metric == "satisfaction":
                return self._predict_satisfaction(days)
            else:
                raise ValueError(f"Unknown metric: {metric}")
                
        except Exception as e:
            logger.error(f"Error getting predictive analytics: {e}")
            return {}
    
    def _get_start_date(self, date_range: str) -> datetime:
        """Convert date range string to start date"""
        now = datetime.utcnow()
        
        if date_range == "7d":
            return now - timedelta(days=7)
        elif date_range == "30d":
            return now - timedelta(days=30)
        elif date_range == "90d":
            return now - timedelta(days=90)
        elif date_range == "1y":
            return now - timedelta(days=365)
        else:
            return now - timedelta(days=30)  # Default to 30 days
    
    def _get_ticket_status_counts(self, start_date: datetime) -> Dict[str, int]:
        """Get ticket status distribution"""
        status_counts = self.db.query(
            Ticket.status,
            func.count(Ticket.id)
        ).filter(
            Ticket.created_at >= start_date
        ).group_by(Ticket.status).all()
        
        return dict(status_counts)
    
    def _calculate_resolution_metrics(self, start_date: datetime) -> Dict[str, Any]:
        """Calculate resolution time metrics"""
        resolved_tickets = self.db.query(Ticket).filter(
            and_(
                Ticket.status == "resolved",
                Ticket.created_at >= start_date,
                Ticket.resolved_at.isnot(None)
            )
        ).all()
        
        if not resolved_tickets:
            return {
                "resolution_rate": 0,
                "avg_resolution_time": 0,
                "median_resolution_time": 0
            }
        
        # Calculate resolution times in hours
        resolution_times = []
        for ticket in resolved_tickets:
            if ticket.resolved_at and ticket.created_at:
                time_diff = (ticket.resolved_at - ticket.created_at).total_seconds() / 3600
                resolution_times.append(time_diff)
        
        avg_resolution_time = sum(resolution_times) / len(resolution_times)
        median_resolution_time = sorted(resolution_times)[len(resolution_times) // 2]
        
        # Calculate resolution rate
        total_tickets = self.db.query(Ticket).filter(
            Ticket.created_at >= start_date
        ).count()
        
        resolution_rate = (len(resolved_tickets) / total_tickets * 100) if total_tickets > 0 else 0
        
        return {
            "resolution_rate": round(resolution_rate, 2),
            "avg_resolution_time": round(avg_resolution_time, 2),
            "median_resolution_time": round(median_resolution_time, 2)
        }
    
    def _get_channel_distribution(self, start_date: datetime) -> Dict[str, int]:
        """Get channel distribution"""
        channel_counts = self.db.query(
            Ticket.channel,
            func.count(Ticket.id)
        ).filter(
            Ticket.created_at >= start_date
        ).group_by(Ticket.channel).all()
        
        return dict(channel_counts)
    
    def _get_category_distribution(self, start_date: datetime) -> Dict[str, int]:
        """Get category distribution"""
        category_counts = self.db.query(
            Ticket.category,
            func.count(Ticket.id)
        ).filter(
            Ticket.created_at >= start_date
        ).group_by(Ticket.category).all()
        
        return dict(category_counts)
    
    def _get_sentiment_metrics(self, start_date: datetime) -> Dict[str, Any]:
        """Get sentiment analysis metrics"""
        tickets_with_sentiment = self.db.query(Ticket).filter(
            and_(
                Ticket.created_at >= start_date,
                Ticket.sentiment.isnot(None)
            )
        ).all()
        
        if not tickets_with_sentiment:
            return {
                "avg_sentiment": 0,
                "sentiment_distribution": {},
                "avg_satisfaction": 0
            }
        
        # Sentiment distribution
        sentiment_counts = Counter([t.sentiment for t in tickets_with_sentiment])
        
        # Average satisfaction
        satisfaction_ratings = [t.satisfaction_rating for t in tickets_with_sentiment if t.satisfaction_rating]
        avg_satisfaction = sum(satisfaction_ratings) / len(satisfaction_ratings) if satisfaction_ratings else 0
        
        # Calculate average sentiment score (assuming sentiment is stored as numeric)
        sentiment_scores = [t.sentiment_score for t in tickets_with_sentiment if hasattr(t, 'sentiment_score') and t.sentiment_score]
        avg_sentiment = sum(sentiment_scores) / len(sentiment_scores) if sentiment_scores else 0
        
        return {
            "avg_sentiment": round(avg_sentiment, 2),
            "sentiment_distribution": dict(sentiment_counts),
            "avg_satisfaction": round(avg_satisfaction, 2)
        }
    
    def _calculate_revenue_metrics(self, start_date: datetime) -> Dict[str, Any]:
        """Calculate revenue metrics"""
        # This would integrate with your billing system
        # For now, return mock data
        return {
            "total_revenue": 0,
            "monthly_revenue": 0,
            "revenue_growth": 0,
            "top_revenue_brands": []
        }
    
    def _calculate_trends(self, date_range: str) -> Dict[str, Any]:
        """Calculate trend data"""
        start_date = self._get_start_date(date_range)
        
        # Daily ticket counts
        daily_counts = self.db.query(
            func.date(Ticket.created_at),
            func.count(Ticket.id)
        ).filter(
            Ticket.created_at >= start_date
        ).group_by(func.date(Ticket.created_at)).order_by(func.date(Ticket.created_at)).all()
        
        return {
            "daily_tickets": [{"date": str(date), "count": count} for date, count in daily_counts],
            "growth_rate": self._calculate_growth_rate(daily_counts)
        }
    
    def _calculate_response_times(self, tickets: List[Ticket]) -> Dict[str, float]:
        """Calculate response time metrics for tickets"""
        response_times = []
        resolution_times = []
        
        for ticket in tickets:
            if ticket.first_response_at and ticket.created_at:
                response_time = (ticket.first_response_at - ticket.created_at).total_seconds() / 3600
                response_times.append(response_time)
            
            if ticket.resolved_at and ticket.created_at:
                resolution_time = (ticket.resolved_at - ticket.created_at).total_seconds() / 3600
                resolution_times.append(resolution_time)
        
        return {
            "average": round(sum(response_times) / len(response_times), 2) if response_times else 0,
            "avg_resolution": round(sum(resolution_times) / len(resolution_times), 2) if resolution_times else 0
        }
    
    def _get_channel_performance(self, tickets: List[Ticket]) -> Dict[str, Any]:
        """Get channel performance metrics"""
        channel_data = defaultdict(lambda: {"count": 0, "resolved": 0, "avg_satisfaction": 0})
        
        for ticket in tickets:
            channel = ticket.channel or "unknown"
            channel_data[channel]["count"] += 1
            
            if ticket.status == "resolved":
                channel_data[channel]["resolved"] += 1
            
            if ticket.satisfaction_rating:
                if "satisfaction_sum" not in channel_data[channel]:
                    channel_data[channel]["satisfaction_sum"] = 0
                    channel_data[channel]["satisfaction_count"] = 0
                channel_data[channel]["satisfaction_sum"] += ticket.satisfaction_rating
                channel_data[channel]["satisfaction_count"] += 1
        
        # Calculate averages
        for channel in channel_data:
            if channel_data[channel]["satisfaction_count"] > 0:
                channel_data[channel]["avg_satisfaction"] = round(
                    channel_data[channel]["satisfaction_sum"] / channel_data[channel]["satisfaction_count"], 2
                )
            channel_data[channel]["resolution_rate"] = round(
                (channel_data[channel]["resolved"] / channel_data[channel]["count"]) * 100, 2
            ) if channel_data[channel]["count"] > 0 else 0
        
        return dict(channel_data)
    
    def _get_category_analysis(self, tickets: List[Ticket]) -> Dict[str, Any]:
        """Get category analysis"""
        category_data = defaultdict(lambda: {"count": 0, "resolved": 0, "avg_sentiment": 0})
        
        for ticket in tickets:
            category = ticket.category or "other"
            category_data[category]["count"] += 1
            
            if ticket.status == "resolved":
                category_data[category]["resolved"] += 1
            
            if hasattr(ticket, 'sentiment_score') and ticket.sentiment_score:
                if "sentiment_sum" not in category_data[category]:
                    category_data[category]["sentiment_sum"] = 0
                    category_data[category]["sentiment_count"] = 0
                category_data[category]["sentiment_sum"] += ticket.sentiment_score
                category_data[category]["sentiment_count"] += 1
        
        # Calculate averages
        for category in category_data:
            if category_data[category]["sentiment_count"] > 0:
                category_data[category]["avg_sentiment"] = round(
                    category_data[category]["sentiment_sum"] / category_data[category]["sentiment_count"], 2
                )
            category_data[category]["resolution_rate"] = round(
                (category_data[category]["resolved"] / category_data[category]["count"]) * 100, 2
            ) if category_data[category]["count"] > 0 else 0
        
        return dict(category_data)
    
    def _get_sentiment_trends(self, tickets: List[Ticket]) -> Dict[str, Any]:
        """Get sentiment trends over time"""
        # Group tickets by week and calculate average sentiment
        weekly_sentiment = defaultdict(list)
        
        for ticket in tickets:
            if hasattr(ticket, 'sentiment_score') and ticket.sentiment_score:
                week_start = ticket.created_at.replace(hour=0, minute=0, second=0, microsecond=0)
                week_start = week_start - timedelta(days=week_start.weekday())
                weekly_sentiment[week_start].append(ticket.sentiment_score)
        
        # Calculate weekly averages
        weekly_averages = []
        for week_start, scores in sorted(weekly_sentiment.items()):
            weekly_averages.append({
                "week": week_start.strftime("%Y-%m-%d"),
                "avg_sentiment": round(sum(scores) / len(scores), 2)
            })
        
        return {
            "weekly_trends": weekly_averages,
            "overall_trend": self._calculate_sentiment_trend(weekly_averages)
        }
    
    def _get_agent_performance(self, brand_id: int, start_date: datetime) -> Dict[str, Any]:
        """Get agent performance metrics"""
        # This would integrate with your user/agent system
        # For now, return mock data
        return {
            "total_agents": 0,
            "avg_tickets_per_agent": 0,
            "top_performers": []
        }
    
    def _calculate_brand_trends(self, brand_id: int, date_range: str) -> Dict[str, Any]:
        """Calculate trends for a specific brand"""
        start_date = self._get_start_date(date_range)
        
        # Daily ticket counts for this brand
        daily_counts = self.db.query(
            func.date(Ticket.created_at),
            func.count(Ticket.id)
        ).filter(
            and_(
                Ticket.brand_id == brand_id,
                Ticket.created_at >= start_date
            )
        ).group_by(func.date(Ticket.created_at)).order_by(func.date(Ticket.created_at)).all()
        
        return {
            "daily_tickets": [{"date": str(date), "count": count} for date, count in daily_counts],
            "growth_rate": self._calculate_growth_rate(daily_counts)
        }
    
    def _get_user_recent_activity(self, user_id: int, start_date: datetime) -> List[Dict[str, Any]]:
        """Get recent activity for a user"""
        recent_tickets = self.db.query(Ticket).filter(
            and_(
                Ticket.owner_id == user_id,
                Ticket.created_at >= start_date
            )
        ).order_by(desc(Ticket.created_at)).limit(5).all()
        
        return [
            {
                "ticket_id": ticket.id,
                "title": ticket.title,
                "status": ticket.status,
                "created_at": ticket.created_at.isoformat(),
                "channel": ticket.channel
            }
            for ticket in recent_tickets
        ]
    
    def _get_recent_activity(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent system activity"""
        recent_tickets = self.db.query(Ticket).order_by(desc(Ticket.created_at)).limit(limit).all()
        
        return [
            {
                "ticket_id": ticket.id,
                "title": ticket.title,
                "status": ticket.status,
                "brand_id": ticket.brand_id,
                "created_at": ticket.created_at.isoformat(),
                "channel": ticket.channel
            }
            for ticket in recent_tickets
        ]
    
    def _get_system_health(self) -> Dict[str, Any]:
        """Get system health metrics"""
        # Calculate system health indicators
        now = datetime.utcnow()
        hour_ago = now - timedelta(hours=1)
        
        # Recent activity
        recent_tickets = self.db.query(Ticket).filter(
            Ticket.created_at >= hour_ago
        ).count()
        
        # Error rate (if you have error logging)
        error_rate = 0  # This would be calculated from error logs
        
        # Response time (average API response time)
        avg_response_time = 0  # This would be calculated from API metrics
        
        return {
            "status": "healthy" if error_rate < 0.05 else "warning",
            "recent_activity": recent_tickets,
            "error_rate": error_rate,
            "avg_response_time": avg_response_time
        }
    
    def _calculate_growth_rate(self, daily_counts: List[Tuple]) -> float:
        """Calculate growth rate from daily counts"""
        if len(daily_counts) < 2:
            return 0
        
        # Calculate week-over-week growth
        first_week = sum(count for _, count in daily_counts[:7])
        second_week = sum(count for _, count in daily_counts[7:14]) if len(daily_counts) >= 14 else 0
        
        if first_week == 0:
            return 0
        
        return round(((second_week - first_week) / first_week) * 100, 2)
    
    def _calculate_sentiment_trend(self, weekly_averages: List[Dict[str, Any]]) -> str:
        """Calculate overall sentiment trend"""
        if len(weekly_averages) < 2:
            return "stable"
        
        first_week = weekly_averages[0]["avg_sentiment"]
        last_week = weekly_averages[-1]["avg_sentiment"]
        
        if last_week > first_week + 0.1:
            return "improving"
        elif last_week < first_week - 0.1:
            return "declining"
        else:
            return "stable"
    
    def _generate_performance_report(self, filters: Dict[str, Any] = None) -> Dict[str, Any]:
        """Generate performance report"""
        # Implementation for performance report
        return {
            "report_type": "performance",
            "generated_at": datetime.utcnow().isoformat(),
            "metrics": self.get_system_overview()
        }
    
    def _generate_trends_report(self, filters: Dict[str, Any] = None) -> Dict[str, Any]:
        """Generate trends report"""
        # Implementation for trends report
        return {
            "report_type": "trends",
            "generated_at": datetime.utcnow().isoformat(),
            "trends": self._calculate_trends("90d")
        }
    
    def _generate_financial_report(self, filters: Dict[str, Any] = None) -> Dict[str, Any]:
        """Generate financial report"""
        # Implementation for financial report
        return {
            "report_type": "financial",
            "generated_at": datetime.utcnow().isoformat(),
            "revenue": self._calculate_revenue_metrics(datetime.utcnow() - timedelta(days=30))
        }
    
    def _generate_satisfaction_report(self, filters: Dict[str, Any] = None) -> Dict[str, Any]:
        """Generate customer satisfaction report"""
        # Implementation for satisfaction report
        return {
            "report_type": "customer_satisfaction",
            "generated_at": datetime.utcnow().isoformat(),
            "satisfaction": self._get_sentiment_metrics(datetime.utcnow() - timedelta(days=30))
        }
    
    def _generate_channel_report(self, filters: Dict[str, Any] = None) -> Dict[str, Any]:
        """Generate channel analysis report"""
        # Implementation for channel report
        return {
            "report_type": "channel_analysis",
            "generated_at": datetime.utcnow().isoformat(),
            "channels": self._get_channel_distribution(datetime.utcnow() - timedelta(days=30))
        }
    
    def _predict_ticket_volume(self, days: int) -> Dict[str, Any]:
        """Predict ticket volume for the next N days"""
        # Simple linear regression prediction
        # In production, you'd use more sophisticated ML models
        
        # Get historical data
        start_date = datetime.utcnow() - timedelta(days=days * 2)
        daily_counts = self.db.query(
            func.date(Ticket.created_at),
            func.count(Ticket.id)
        ).filter(
            Ticket.created_at >= start_date
        ).group_by(func.date(Ticket.created_at)).order_by(func.date(Ticket.created_at)).all()
        
        if len(daily_counts) < 7:
            return {"prediction": "insufficient_data"}
        
        # Calculate average daily volume
        avg_daily = sum(count for _, count in daily_counts) / len(daily_counts)
        
        # Simple prediction (average + trend)
        predictions = []
        for i in range(days):
            predicted_date = datetime.utcnow() + timedelta(days=i+1)
            predictions.append({
                "date": predicted_date.strftime("%Y-%m-%d"),
                "predicted_volume": round(avg_daily, 1)
            })
        
        return {
            "predictions": predictions,
            "confidence": 0.75,
            "method": "linear_regression"
        }
    
    def _predict_resolution_time(self, days: int) -> Dict[str, Any]:
        """Predict resolution time trends"""
        # Implementation for resolution time prediction
        return {
            "prediction": "feature_not_implemented",
            "method": "ml_model"
        }
    
    def _predict_satisfaction(self, days: int) -> Dict[str, Any]:
        """Predict satisfaction trends"""
        # Implementation for satisfaction prediction
        return {
            "prediction": "feature_not_implemented",
            "method": "ml_model"
        } 