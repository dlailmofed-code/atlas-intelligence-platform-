"""ATLAS Platform - Initial Schema Migration

Revision ID: 001
Revises:
Create Date: 2026-07-10

This migration creates all tables for the ATLAS Platform including:
- Users, Roles, Permissions
- Subscriptions, Plans, Invoices, Payments
- Feature Flags, Usage Records
- Organizations, Projects, Reports
- Signals, Evidence, Knowledge
- Sources, Notifications
- All association tables
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # =========================================================================
    # ENUM TYPES
    # =========================================================================
    op.execute("CREATE TYPE subscriptionstatus AS ENUM ('active', 'inactive', 'cancelled', 'past_due', 'trialing')")
    op.execute("CREATE TYPE billingcycle AS ENUM ('monthly', 'yearly')")
    op.execute("CREATE TYPE invoicestatus AS ENUM ('draft', 'pending', 'paid', 'failed', 'refunded')")
    op.execute("CREATE TYPE paymentstatus AS ENUM ('pending', 'completed', 'failed', 'refunded')")
    op.execute("CREATE TYPE sourcetype AS ENUM ('webhook', 'api', 'rss', 'manual', 'scrape')")
    op.execute("CREATE TYPE sourcestatus AS ENUM ('active', 'inactive', 'error', 'paused')")
    op.execute("CREATE TYPE notificationtype AS ENUM ('info', 'warning', 'error', 'success')")
    op.execute("CREATE TYPE notificationchannel AS ENUM ('email', 'sms', 'push', 'in_app')")
    op.execute("CREATE TYPE signalconfidence AS ENUM ('low', 'medium', 'high', 'very_high')")
    op.execute("CREATE TYPE signalstatus AS ENUM ('active', 'triggered', 'resolved', 'dismissed')")
    op.execute("CREATE TYPE reportstatus AS ENUM ('draft', 'processing', 'completed', 'failed')")
    op.execute("CREATE TYPE reporttype AS ENUM ('opportunity', 'risk', 'performance', 'custom')")
    op.execute("CREATE TYPE projectstatus AS ENUM ('active', 'completed', 'archived', 'on_hold')")

    # =========================================================================
    # USERS, ROLES, PERMISSIONS
    # =========================================================================
    op.create_table(
        "roles",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(50), nullable=False, unique=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("is_system", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_roles_name", "roles", ["name"], unique=True)

    op.create_table(
        "permissions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(100), nullable=False, unique=True),
        sa.Column("resource", sa.String(50), nullable=False),
        sa.Column("action", sa.String(50), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_permissions_name", "permissions", ["name"], unique=True)
    op.create_index("ix_permissions_resource_action", "permissions", ["resource", "action"])

    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("email", sa.String(255), nullable=False, unique=True),
        sa.Column("username", sa.String(100), nullable=True, unique=True),
        sa.Column("hashed_password", sa.String(255), nullable=False),
        sa.Column("first_name", sa.String(100), nullable=True),
        sa.Column("last_name", sa.String(100), nullable=True),
        sa.Column("full_name", sa.String(200), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("is_verified", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("is_superuser", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("avatar_url", sa.String(500), nullable=True),
        sa.Column("bio", sa.Text(), nullable=True),
        sa.Column("phone", sa.String(50), nullable=True),
        sa.Column("timezone", sa.String(50), nullable=True),
        sa.Column("locale", sa.String(10), nullable=True),
        sa.Column("preferences", postgresql.JSON(), nullable=False, server_default="{}"),
        sa.Column("last_login_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_activity_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("email_verified_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)
    op.create_index("ix_users_username", "users", ["username"], unique=True)
    op.create_index("ix_users_is_active", "users", ["is_active"])

    # User-Role association
    op.create_table(
        "user_roles",
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("role_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True),
    )

    # Role-Permission association
    op.create_table(
        "role_permissions",
        sa.Column("role_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("permission_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("permissions.id", ondelete="CASCADE"), primary_key=True),
    )

    # =========================================================================
    # ORGANIZATIONS
    # =========================================================================
    op.create_table(
        "organizations",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("slug", sa.String(100), nullable=False, unique=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("logo_url", sa.String(500), nullable=True),
        sa.Column("website", sa.String(255), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("settings", postgresql.JSON(), nullable=False, server_default="{}"),
        sa.Column("metadata", postgresql.JSON(), nullable=False, server_default="{}"),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_organizations_slug", "organizations", ["slug"], unique=True)
    op.create_index("ix_organizations_is_active", "organizations", ["is_active"])

    # Organization-Member association
    op.create_table(
        "organization_members",
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("organizations.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("is_owner", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("role", sa.String(50), nullable=False, server_default="member"),
    )

    # =========================================================================
    # SUBSCRIPTIONS & PLANS
    # =========================================================================
    op.create_table(
        "plans",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("slug", sa.String(50), nullable=False, unique=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("price_monthly", sa.Numeric(10, 2), nullable=False),
        sa.Column("price_yearly", sa.Numeric(10, 2), nullable=False),
        sa.Column("currency", sa.String(3), nullable=False, server_default="USD"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("is_featured", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("features", postgresql.JSON(), nullable=False, server_default="[]"),
        sa.Column("limits", postgresql.JSON(), nullable=False, server_default="{}"),
        sa.Column("display_order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_plans_slug", "plans", ["slug"], unique=True)
    op.create_index("ix_plans_is_active", "plans", ["is_active"])

    op.create_table(
        "subscriptions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("plan_id", sa.String(50), nullable=False),
        sa.Column("plan_name", sa.String(100), nullable=False),
        sa.Column("status", postgresql.ENUM("active", "inactive", "cancelled", "past_due", "trialing", name="subscriptionstatus"), nullable=False),
        sa.Column("billing_cycle", postgresql.ENUM("monthly", "yearly", name="billingcycle"), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("current_period_start", sa.DateTime(timezone=True), nullable=True),
        sa.Column("current_period_end", sa.DateTime(timezone=True), nullable=True),
        sa.Column("trial_end", sa.DateTime(timezone=True), nullable=True),
        sa.Column("cancelled_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("external_subscription_id", sa.String(255), nullable=True),
        sa.Column("metadata", postgresql.JSON(), nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_subscriptions_user_id", "subscriptions", ["user_id"])
    op.create_index("ix_subscriptions_status", "subscriptions", ["status"])

    op.create_table(
        "invoices",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("subscription_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("subscriptions.id", ondelete="SET NULL"), nullable=True, index=True),
        sa.Column("invoice_number", sa.String(50), nullable=False, unique=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("subtotal", sa.Numeric(10, 2), nullable=False),
        sa.Column("tax", sa.Numeric(10, 2), nullable=False, server_default="0"),
        sa.Column("total", sa.Numeric(10, 2), nullable=False),
        sa.Column("currency", sa.String(3), nullable=False, server_default="USD"),
        sa.Column("status", postgresql.ENUM("draft", "pending", "paid", "failed", "refunded", name="invoicestatus"), nullable=False),
        sa.Column("issue_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("due_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("paid_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("external_invoice_id", sa.String(255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_invoices_invoice_number", "invoices", ["invoice_number"], unique=True)
    op.create_index("ix_invoices_status", "invoices", ["status"])

    op.create_table(
        "payments",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("subscription_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("subscriptions.id", ondelete="SET NULL"), nullable=True, index=True),
        sa.Column("invoice_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("invoices.id", ondelete="SET NULL"), nullable=True, index=True),
        sa.Column("amount", sa.Numeric(10, 2), nullable=False),
        sa.Column("currency", sa.String(3), nullable=False, server_default="USD"),
        sa.Column("status", postgresql.ENUM("pending", "completed", "failed", "refunded", name="paymentstatus"), nullable=False),
        sa.Column("payment_method", sa.String(50), nullable=True),
        sa.Column("external_payment_id", sa.String(255), nullable=True),
        sa.Column("external_receipt_url", sa.String(500), nullable=True),
        sa.Column("failure_reason", sa.Text(), nullable=True),
        sa.Column("paid_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_payments_status", "payments", ["status"])

    # =========================================================================
    # FEATURE FLAGS & USAGE
    # =========================================================================
    op.create_table(
        "feature_flags",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("key", sa.String(100), nullable=False, unique=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("is_rollout", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("rollout_percentage", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("enabled_plans", postgresql.JSON(), nullable=False, server_default="[]"),
        sa.Column("enabled_roles", postgresql.JSON(), nullable=False, server_default="[]"),
        sa.Column("enabled_regions", postgresql.JSON(), nullable=False, server_default="[]"),
        sa.Column("experiment_group", sa.String(100), nullable=True),
        sa.Column("is_beta", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("documentation_url", sa.String(500), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_feature_flags_key", "feature_flags", ["key"], unique=True)
    op.create_index("ix_feature_flags_is_active", "feature_flags", ["is_active"])

    op.create_table(
        "feature_flag_overrides",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("feature_flag_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("feature_flags.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("is_enabled", sa.Boolean(), nullable=False),
        sa.Column("reason", sa.Text(), nullable=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_by_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_feature_flag_overrides_user_flag", "feature_flag_overrides", ["user_id", "feature_flag_id"], unique=True)

    op.create_table(
        "usage_records",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("subscription_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("subscriptions.id", ondelete="SET NULL"), nullable=True, index=True),
        sa.Column("usage_type", sa.String(100), nullable=False, index=True),
        sa.Column("amount", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("resource_id", sa.String(255), nullable=True),
        sa.Column("reset_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("extra_data", postgresql.JSON(), nullable=False, server_default="{}"),
        sa.Column("is_processed", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_usage_records_user_type_date", "usage_records", ["user_id", "usage_type", "created_at"])
    op.create_index("ix_usage_records_reset_at", "usage_records", ["reset_at"])

    op.create_table(
        "usage_summaries",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("usage_type", sa.String(100), nullable=False, index=True),
        sa.Column("period_type", sa.String(20), nullable=False),
        sa.Column("period_start", sa.DateTime(timezone=True), nullable=False),
        sa.Column("period_end", sa.DateTime(timezone=True), nullable=False),
        sa.Column("total_usage", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("last_reset", sa.DateTime(timezone=True), nullable=False),
        sa.Column("concurrent_usage", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_usage_summaries_user_type_period", "usage_summaries", ["user_id", "usage_type", "period_start"])
    op.create_index("ix_usage_summaries_period_start", "usage_summaries", ["period_start"])

    # =========================================================================
    # BILLING & SEATS
    # =========================================================================
    op.create_table(
        "billing_organizations",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), nullable=False, index=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("slug", sa.String(100), nullable=False, unique=True),
        sa.Column("billing_email", sa.String(255), nullable=True),
        sa.Column("billing_name", sa.String(255), nullable=True),
        sa.Column("billing_phone", sa.String(50), nullable=True),
        sa.Column("billing_address_line1", sa.String(255), nullable=True),
        sa.Column("billing_address_line2", sa.String(255), nullable=True),
        sa.Column("billing_city", sa.String(100), nullable=True),
        sa.Column("billing_state", sa.String(100), nullable=True),
        sa.Column("billing_postal_code", sa.String(20), nullable=True),
        sa.Column("billing_country", sa.String(2), nullable=False, server_default="US"),
        sa.Column("subscription_tier", sa.String(50), nullable=False, server_default="free"),
        sa.Column("tax_id", sa.String(100), nullable=True),
        sa.Column("tax_exempt", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("default_payment_method", sa.String(255), nullable=True),
        sa.Column("preferred_currency", sa.String(3), nullable=False, server_default="USD"),
        sa.Column("settings", postgresql.JSON(), nullable=False, server_default="{}"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_billing_orgs_slug", "billing_organizations", ["slug"], unique=True)
    op.create_index("ix_billing_orgs_subscription_tier", "billing_organizations", ["subscription_tier"])

    op.create_table(
        "organization_seats",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), nullable=False, index=True),
        sa.Column("seat_type", sa.String(50), nullable=False),
        sa.Column("total_seats", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("used_seats", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("pending_seats", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("period_start", sa.DateTime(timezone=True), nullable=False),
        sa.Column("period_end", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_organization_seats_org_type", "organization_seats", ["organization_id", "seat_type"])

    # =========================================================================
    # PROJECTS
    # =========================================================================
    op.create_table(
        "projects",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("slug", sa.String(100), nullable=False, unique=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("status", postgresql.ENUM("active", "completed", "archived", "on_hold", name="projectstatus"), nullable=False, server_default="active"),
        sa.Column("owner_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=True, index=True),
        sa.Column("settings", postgresql.JSON(), nullable=False, server_default="{}"),
        sa.Column("metadata", postgresql.JSON(), nullable=False, server_default="{}"),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_projects_slug", "projects", ["slug"], unique=True)
    op.create_index("ix_projects_status", "projects", ["status"])

    op.create_table(
        "project_members",
        sa.Column("project_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("projects.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("role", sa.String(50), nullable=False, server_default="member"),
        sa.Column("can_edit", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("can_delete", sa.Boolean(), nullable=False, server_default="false"),
    )

    # =========================================================================
    # SOURCES
    # =========================================================================
    op.create_table(
        "sources",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("type", postgresql.ENUM("webhook", "api", "rss", "manual", "scrape", name="sourcetype"), nullable=False),
        sa.Column("url", sa.String(500), nullable=True),
        sa.Column("status", postgresql.ENUM("active", "inactive", "error", "paused", name="sourcestatus"), nullable=False, server_default="active"),
        sa.Column("owner_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=True, index=True),
        sa.Column("schedule", sa.String(100), nullable=True),
        sa.Column("last_fetch_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_error", sa.Text(), nullable=True),
        sa.Column("metadata", postgresql.JSON(), nullable=False, server_default="{}"),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_sources_status", "sources", ["status"])

    op.create_table(
        "source_configs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("source_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("sources.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("key", sa.String(100), nullable=False),
        sa.Column("value", postgresql.JSON(), nullable=False),
        sa.Column("is_secret", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_source_configs_source_key", "source_configs", ["source_id", "key"], unique=True)

    # =========================================================================
    # SIGNALS
    # =========================================================================
    op.create_table(
        "signal_types",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(100), nullable=False, unique=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("category", sa.String(50), nullable=True),
        sa.Column("default_confidence", postgresql.ENUM("low", "medium", "high", "very_high", name="signalconfidence"), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_signal_types_name", "signal_types", ["name"], unique=True)

    op.create_table(
        "signals",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("type_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("signal_types.id", ondelete="SET NULL"), nullable=True, index=True),
        sa.Column("signal_type", sa.String(100), nullable=True),
        sa.Column("confidence", postgresql.ENUM("low", "medium", "high", "very_high", name="signalconfidence"), nullable=False),
        sa.Column("status", postgresql.ENUM("active", "triggered", "resolved", "dismissed", name="signalstatus"), nullable=False, server_default="active"),
        sa.Column("severity", sa.Integer(), nullable=True),
        sa.Column("metadata", postgresql.JSON(), nullable=False, server_default="{}"),
        sa.Column("triggered_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("resolved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("owner_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=True, index=True),
        sa.Column("source_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("sources.id", ondelete="SET NULL"), nullable=True, index=True),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_signals_status", "signals", ["status"])
    op.create_index("ix_signals_confidence", "signals", ["confidence"])
    op.create_index("ix_signals_created_at", "signals", ["created_at"])

    op.create_table(
        "signal_tag_values",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(100), nullable=False, unique=True),
        sa.Column("color", sa.String(7), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_signal_tag_values_name", "signal_tag_values", ["name"], unique=True)

    op.create_table(
        "signal_tags",
        sa.Column("signal_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("signals.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("tag_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("signal_tag_values.id", ondelete="CASCADE"), primary_key=True),
    )

    # User favorite opportunities
    op.create_table(
        "user_favorite_opportunities",
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("opportunity_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("signals.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    # =========================================================================
    # REPORTS
    # =========================================================================
    op.create_table(
        "reports",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("slug", sa.String(100), nullable=False, unique=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("report_type", postgresql.ENUM("opportunity", "risk", "performance", "custom", name="reporttype"), nullable=False),
        sa.Column("status", postgresql.ENUM("draft", "processing", "completed", "failed", name="reportstatus"), nullable=False, server_default="draft"),
        sa.Column("content", postgresql.JSON(), nullable=True),
        sa.Column("filters", postgresql.JSON(), nullable=False, server_default="{}"),
        sa.Column("metadata", postgresql.JSON(), nullable=False, server_default="{}"),
        sa.Column("file_url", sa.String(500), nullable=True),
        sa.Column("file_format", sa.String(20), nullable=True),
        sa.Column("file_size", sa.BigInteger(), nullable=True),
        sa.Column("owner_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=True, index=True),
        sa.Column("project_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("projects.id", ondelete="SET NULL"), nullable=True, index=True),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_reports_slug", "reports", ["slug"], unique=True)
    op.create_index("ix_reports_status", "reports", ["status"])
    op.create_index("ix_reports_report_type", "reports", ["report_type"])

    op.create_table(
        "report_tag_values",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(100), nullable=False, unique=True),
        sa.Column("color", sa.String(7), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_report_tag_values_name", "report_tag_values", ["name"], unique=True)

    op.create_table(
        "report_tags",
        sa.Column("report_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("reports.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("tag_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("report_tag_values.id", ondelete="CASCADE"), primary_key=True),
    )

    # =========================================================================
    # EVIDENCE
    # =========================================================================
    op.create_table(
        "evidence",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("source_name", sa.String(255), nullable=True),
        sa.Column("source_url", sa.String(500), nullable=True),
        sa.Column("source_type", sa.String(50), nullable=True),
        sa.Column("relevance_score", sa.Float(), nullable=True),
        sa.Column("metadata", postgresql.JSON(), nullable=False, server_default="{}"),
        sa.Column("signal_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("signals.id", ondelete="CASCADE"), nullable=True, index=True),
        sa.Column("owner_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=True, index=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_evidence_signal_id", "evidence", ["signal_id"])

    op.create_table(
        "evidence_sources",
        sa.Column("evidence_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("evidence.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("source_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("sources.id", ondelete="CASCADE"), primary_key=True),
    )

    # =========================================================================
    # KNOWLEDGE
    # =========================================================================
    op.create_table(
        "knowledge_items",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("content", sa.Text(), nullable=True),
        sa.Column("category", sa.String(100), nullable=True),
        sa.Column("tags", postgresql.JSON(), nullable=False, server_default="[]"),
        sa.Column("metadata", postgresql.JSON(), nullable=False, server_default="{}"),
        sa.Column("embedding", postgresql.BYTEA(), nullable=True),
        sa.Column("owner_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=True, index=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_knowledge_items_category", "knowledge_items", ["category"])

    # =========================================================================
    # NOTIFICATIONS
    # =========================================================================
    op.create_table(
        "notification_templates",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(100), nullable=False, unique=True),
        sa.Column("type", postgresql.ENUM("info", "warning", "error", "success", name="notificationtype"), nullable=False),
        sa.Column("channel", postgresql.ENUM("email", "sms", "push", "in_app", name="notificationchannel"), nullable=False),
        sa.Column("subject", sa.String(255), nullable=True),
        sa.Column("template", sa.Text(), nullable=False),
        sa.Column("variables", postgresql.JSON(), nullable=False, server_default="[]"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_notification_templates_name", "notification_templates", ["name"], unique=True)

    op.create_table(
        "notifications",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("type", postgresql.ENUM("info", "warning", "error", "success", name="notificationtype"), nullable=False),
        sa.Column("channel", postgresql.ENUM("email", "sms", "push", "in_app", name="notificationchannel"), nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("data", postgresql.JSON(), nullable=False, server_default="{}"),
        sa.Column("read_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("sent_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("template_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("notification_templates.id", ondelete="SET NULL"), nullable=True),
        sa.Column("owner_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=True, index=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_notifications_owner_id", "notifications", ["owner_id"])
    op.create_index("ix_notifications_read_at", "notifications", ["read_at"])

    op.create_table(
        "notification_recipients",
        sa.Column("notification_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("notifications.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("read_at", sa.Boolean(), nullable=True, server_default="false"),
        sa.Column("read_at_timestamp", sa.DateTime(timezone=True), nullable=True),
    )


def downgrade() -> None:
    # Drop notification tables
    op.drop_table("notification_recipients")
    op.drop_table("notifications")
    op.drop_table("notification_templates")

    # Drop knowledge tables
    op.drop_table("knowledge_items")

    # Drop evidence tables
    op.drop_table("evidence_sources")
    op.drop_table("evidence")

    # Drop report tables
    op.drop_table("report_tags")
    op.drop_table("report_tag_values")
    op.drop_table("reports")

    # Drop signal tables
    op.drop_table("user_favorite_opportunities")
    op.drop_table("signal_tags")
    op.drop_table("signal_tag_values")
    op.drop_table("signals")
    op.drop_table("signal_types")

    # Drop source tables
    op.drop_table("source_configs")
    op.drop_table("sources")

    # Drop project tables
    op.drop_table("project_members")
    op.drop_table("projects")

    # Drop billing tables
    op.drop_table("organization_seats")
    op.drop_table("billing_organizations")

    # Drop usage tables
    op.drop_table("usage_summaries")
    op.drop_table("usage_records")
    op.drop_table("feature_flag_overrides")
    op.drop_table("feature_flags")

    # Drop payment tables
    op.drop_table("payments")
    op.drop_table("invoices")
    op.drop_table("subscriptions")
    op.drop_table("plans")

    # Drop organization tables
    op.drop_table("organization_members")
    op.drop_table("organizations")

    # Drop user tables
    op.drop_table("role_permissions")
    op.drop_table("user_roles")
    op.drop_table("users")
    op.drop_table("permissions")
    op.drop_table("roles")

    # Drop enum types
    op.execute("DROP TYPE projectstatus")
    op.execute("DROP TYPE reporttype")
    op.execute("DROP TYPE reportstatus")
    op.execute("DROP TYPE signalstatus")
    op.execute("DROP TYPE signalconfidence")
    op.execute("DROP TYPE notificationchannel")
    op.execute("DROP TYPE notificationtype")
    op.execute("DROP TYPE sourcestatus")
    op.execute("DROP TYPE sourcetype")
    op.execute("DROP TYPE paymentstatus")
    op.execute("DROP TYPE invoicestatus")
    op.execute("DROP TYPE billingcycle")
    op.execute("DROP TYPE subscriptionstatus")
