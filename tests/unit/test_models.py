"""
ATLAS Platform - Model Tests

This module contains unit tests for database models.
These tests verify that models can be imported and have the expected attributes.
"""

import uuid
from datetime import datetime, timedelta, timezone

import pytest


class TestModelsImport:
    """Tests that all models can be imported."""
    
    def test_models_import(self):
        """Test that all models can be imported without errors."""
        from backend.models import (
            User, Role, Permission,
            Organization, Project, ProjectInvite,
            Signal, Tag, Opportunity, SavedFilter,
            Evidence, EvidenceVersion,
            Source, Connector, CrawlJob,
            Report, ReportTag, ReportTemplate, ReportGenerationJob,
            Notification, UserNotificationPreference, NotificationLog,
            Subscription, Invoice, Payment, Plan, SubscriptionFeature,
            KnowledgeEntity, KnowledgeRelation, IntelligenceIndicator, UserActivity, CausalLink,
        )
        # If we get here, all models were imported successfully
        assert True
    
    def test_model_count(self):
        """Test that all expected models are available."""
        from backend import models
        
        expected_models = [
            'User', 'Role', 'Permission',
            'Organization', 'Project', 'ProjectInvite',
            'Signal', 'Tag', 'Opportunity', 'SavedFilter',
            'Evidence', 'EvidenceVersion',
            'Source', 'Connector', 'CrawlJob',
            'Report', 'ReportTag', 'ReportTemplate', 'ReportGenerationJob',
            'Notification', 'UserNotificationPreference', 'NotificationLog',
            'Subscription', 'Invoice', 'Payment', 'Plan', 'SubscriptionFeature',
            'KnowledgeEntity', 'KnowledgeRelation', 'IntelligenceIndicator', 'UserActivity', 'CausalLink',
        ]
        
        for model_name in expected_models:
            assert hasattr(models, model_name), f"Missing model: {model_name}"


class TestModelAttributes:
    """Tests that models have expected attributes."""
    
    def test_user_model_attributes(self):
        """Test User model has expected attributes."""
        from backend.models import User
        
        # Check essential attributes
        attrs = ['id', 'email', 'full_name', 'hashed_password', 'created_at', 'updated_at']
        for attr in attrs:
            assert hasattr(User, attr), f"User missing attribute: {attr}"
    
    def test_signal_model_attributes(self):
        """Test Signal model has expected attributes."""
        from backend.models import Signal
        
        attrs = ['id', 'name', 'description', 'type', 'category', 'intensity', 'confidence']
        for attr in attrs:
            assert hasattr(Signal, attr), f"Signal missing attribute: {attr}"
    
    def test_opportunity_model_attributes(self):
        """Test Opportunity model has expected attributes."""
        from backend.models import Opportunity
        
        attrs = ['id', 'title', 'description', 'category', 'industry', 'score_overall']
        for attr in attrs:
            assert hasattr(Opportunity, attr), f"Opportunity missing attribute: {attr}"
    
    def test_evidence_model_attributes(self):
        """Test Evidence model has expected attributes."""
        from backend.models import Evidence
        
        attrs = ['id', 'content', 'summary', 'source_name', 'reliability', 'relevance']
        for attr in attrs:
            assert hasattr(Evidence, attr), f"Evidence missing attribute: {attr}"
    
    def test_source_model_attributes(self):
        """Test Source model has expected attributes."""
        from backend.models import Source
        
        attrs = ['id', 'name', 'slug', 'type', 'reliability_score']
        for attr in attrs:
            assert hasattr(Source, attr), f"Source missing attribute: {attr}"
    
    def test_report_model_attributes(self):
        """Test Report model has expected attributes."""
        from backend.models import Report
        
        attrs = ['id', 'title', 'description', 'type', 'status']
        for attr in attrs:
            assert hasattr(Report, attr), f"Report missing attribute: {attr}"
    
    def test_notification_model_attributes(self):
        """Test Notification model has expected attributes."""
        from backend.models import Notification
        
        attrs = ['id', 'title', 'message', 'type', 'priority']
        for attr in attrs:
            assert hasattr(Notification, attr), f"Notification missing attribute: {attr}"
    
    def test_subscription_model_attributes(self):
        """Test Subscription model has expected attributes."""
        from backend.models import Subscription
        
        attrs = ['id', 'user_id', 'plan_id', 'plan_name', 'status']
        for attr in attrs:
            assert hasattr(Subscription, attr), f"Subscription missing attribute: {attr}"
    
    def test_knowledge_entity_model_attributes(self):
        """Test KnowledgeEntity model has expected attributes."""
        from backend.models import KnowledgeEntity
        
        attrs = ['id', 'name', 'type', 'description']
        for attr in attrs:
            assert hasattr(KnowledgeEntity, attr), f"KnowledgeEntity missing attribute: {attr}"


class TestModelTableNames:
    """Tests that models have correct table names."""
    
    def test_user_table_name(self):
        """Test User model has correct table name."""
        from backend.models import User
        assert User.__tablename__ == "users"
    
    def test_signal_table_name(self):
        """Test Signal model has correct table name."""
        from backend.models import Signal
        assert Signal.__tablename__ == "signals"
    
    def test_evidence_table_name(self):
        """Test Evidence model has correct table name."""
        from backend.models import Evidence
        assert Evidence.__tablename__ == "evidence"
    
    def test_source_table_name(self):
        """Test Source model has correct table name."""
        from backend.models import Source
        assert Source.__tablename__ == "sources"
    
    def test_report_table_name(self):
        """Test Report model has correct table name."""
        from backend.models import Report
        assert Report.__tablename__ == "reports"
    
    def test_notification_table_name(self):
        """Test Notification model has correct table name."""
        from backend.models import Notification
        assert Notification.__tablename__ == "notifications"


class TestBaseModelMixin:
    """Tests for base model mixins."""
    
    def test_base_has_uuid_mixin(self):
        """Test Base model includes UUIDMixin."""
        from backend.models import User
        from backend.models.common.base import UUIDMixin
        
        assert issubclass(User, UUIDMixin)
    
    def test_base_has_timestamp_mixin(self):
        """Test Base model includes TimestampMixin."""
        from backend.models import User
        from backend.models.common.base import TimestampMixin
        
        assert issubclass(User, TimestampMixin)
    
    def test_base_has_soft_delete_mixin(self):
        """Test Base model includes SoftDeleteMixin."""
        from backend.models import User
        from backend.models.common.base import SoftDeleteMixin
        
        assert issubclass(User, SoftDeleteMixin)
    
    def test_base_has_active_mixin(self):
        """Test Base model includes ActiveMixin."""
        from backend.models import User
        from backend.models.common.base import ActiveMixin
        
        assert issubclass(User, ActiveMixin)
