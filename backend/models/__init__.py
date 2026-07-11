"""
ATLAS Platform - Models Package

This package contains all database models organized by domain.
"""

# Common models
from backend.models.common.associations import (
    evidence_sources,
    notification_recipients,
    organization_members,
    project_members,
    report_tags,
    role_permissions,
    signal_tags,
    user_favorite_opportunities,
    user_roles,
)
from backend.models.common.base import (
    ActiveMixin,
    Base,
    SoftDeleteMixin,
    TenantMixin,
    TimestampMixin,
    UUIDMixin,
)

# Evidence models
from backend.models.evidence import Evidence, EvidenceVersion

# Knowledge models
from backend.models.knowledge import (
    CausalLink,
    IntelligenceIndicator,
    KnowledgeEntity,
    KnowledgeRelation,
    UserActivity,
)

# Monetization models
from backend.models.monetization import (
    BillingOrganization,
    FeatureFlag,
    FeatureFlagOverride,
    Seat,
    UsageRecord,
    UsageSummary,
)

# Notification models
from backend.models.notifications import (
    Notification,
    NotificationLog,
    UserNotificationPreference,
)

# Project models
from backend.models.projects import Organization, Project, ProjectInvite

# Report models
from backend.models.reports import (
    Report,
    ReportGenerationJob,
    ReportTag,
    ReportTemplate,
)

# Signal models
from backend.models.signals import Opportunity, SavedFilter, Signal, Tag

# Source models
from backend.models.sources import Connector, CrawlJob, Source

# Subscription models
from backend.models.subscriptions import (
    Invoice,
    Payment,
    Plan,
    Subscription,
    SubscriptionFeature,
)

# User models
from backend.models.users import Permission, Role, User

__all__ = [
    "ActiveMixin",
    # Common
    "Base",
    "BillingOrganization",
    "CausalLink",
    "Connector",
    "CrawlJob",
    # Evidence
    "Evidence",
    "EvidenceVersion",
    # Monetization
    "FeatureFlag",
    "FeatureFlagOverride",
    "IntelligenceIndicator",
    "Invoice",
    # Knowledge
    "KnowledgeEntity",
    "KnowledgeRelation",
    # Notifications
    "Notification",
    "NotificationLog",
    "Opportunity",
    # Projects
    "Organization",
    "Payment",
    "Permission",
    "Plan",
    "Project",
    "ProjectInvite",
    # Reports
    "Report",
    "ReportGenerationJob",
    "ReportTag",
    "ReportTemplate",
    "Role",
    "SavedFilter",
    "Seat",
    # Signals
    "Signal",
    "SoftDeleteMixin",
    # Sources
    "Source",
    # Subscriptions
    "Subscription",
    "SubscriptionFeature",
    "Tag",
    "TenantMixin",
    "TimestampMixin",
    "UUIDMixin",
    "UsageRecord",
    "UsageSummary",
    # Users
    "User",
    "UserActivity",
    "UserNotificationPreference",
    "evidence_sources",
    "notification_recipients",
    # Associations
    "organization_members",
    "project_members",
    "report_tags",
    "role_permissions",
    "signal_tags",
    "user_favorite_opportunities",
    "user_roles",
]
