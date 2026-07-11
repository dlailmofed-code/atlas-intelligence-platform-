"""
ATLAS Platform - Roles and Permissions Seed

This module seeds the default roles and permissions.
Idempotent: Running multiple times will not duplicate records.
"""

import uuid
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.logging import get_logger
from backend.models.users import Permission, Role

logger = get_logger(__name__)


# Default roles
DEFAULT_ROLES: list[dict[str, Any]] = [
    {
        "id": uuid.UUID("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"),
        "name": "guest",
        "description": "Unauthenticated user with minimal access",
        "is_active": True,
        "is_system": True,
    },
    {
        "id": uuid.UUID("bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb"),
        "name": "free_user",
        "description": "Authenticated user with free tier access",
        "is_active": True,
        "is_system": True,
    },
    {
        "id": uuid.UUID("cccccccc-cccc-cccc-cccc-cccccccccccc"),
        "name": "paid_user",
        "description": "User with paid subscription",
        "is_active": True,
        "is_system": True,
    },
    {
        "id": uuid.UUID("dddddddd-dddd-dddd-dddd-dddddddddddd"),
        "name": "enterprise_user",
        "description": "User with enterprise subscription",
        "is_active": True,
        "is_system": True,
    },
    {
        "id": uuid.UUID("eeeeeeee-eeee-eeee-eeee-eeeeeeeeeeee"),
        "name": "admin",
        "description": "Organization administrator",
        "is_active": True,
        "is_system": True,
    },
    {
        "id": uuid.UUID("ffffffff-ffff-ffff-ffff-ffffffffffff"),
        "name": "super_admin",
        "description": "System-wide administrator",
        "is_active": True,
        "is_system": True,
    },
]


# Default permissions
DEFAULT_PERMISSIONS: list[dict[str, Any]] = [
    # Site permissions
    {"id": uuid.UUID("01000001-0000-0000-0000-000000000001"), "name": "site:read", "resource": "site", "action": "read", "description": "View site content"},

    # Content permissions
    {"id": uuid.UUID("01000002-0000-0000-0000-000000000002"), "name": "content:read", "resource": "content", "action": "read", "description": "Read content"},
    {"id": uuid.UUID("01000003-0000-0000-0000-000000000003"), "name": "content:write", "resource": "content", "action": "write", "description": "Create/edit content"},
    {"id": uuid.UUID("01000004-0000-0000-0000-000000000004"), "name": "content:delete", "resource": "content", "action": "delete", "description": "Delete content"},

    # Analysis permissions
    {"id": uuid.UUID("01000005-0000-0000-0000-000000000005"), "name": "analysis:create", "resource": "analysis", "action": "create", "description": "Create analyses"},
    {"id": uuid.UUID("01000006-0000-0000-0000-000000000006"), "name": "analysis:create_limited", "resource": "analysis", "action": "create_limited", "description": "Create limited analyses"},
    {"id": uuid.UUID("01000007-0000-0000-0000-000000000007"), "name": "analysis:create_concurrent", "resource": "analysis", "action": "create_concurrent", "description": "Run concurrent analyses"},
    {"id": uuid.UUID("01000008-0000-0000-0000-000000000008"), "name": "analysis:read", "resource": "analysis", "action": "read", "description": "View analyses"},
    {"id": uuid.UUID("01000009-0000-0000-0000-000000000009"), "name": "analysis:delete", "resource": "analysis", "action": "delete", "description": "Delete analyses"},

    # Report permissions
    {"id": uuid.UUID("01000010-0000-0000-0000-000000000010"), "name": "report:read_basic", "resource": "report", "action": "read_basic", "description": "View basic reports"},
    {"id": uuid.UUID("01000011-0000-0000-0000-000000000011"), "name": "report:read_detailed", "resource": "report", "action": "read_detailed", "description": "View detailed reports"},
    {"id": uuid.UUID("01000012-0000-0000-0000-000000000012"), "name": "report:read_advanced", "resource": "report", "action": "read_advanced", "description": "View advanced reports"},
    {"id": uuid.UUID("01000013-0000-0000-0000-000000000013"), "name": "report:create", "resource": "report", "action": "create", "description": "Create reports"},
    {"id": uuid.UUID("01000014-0000-0000-0000-000000000014"), "name": "report:share", "resource": "report", "action": "share", "description": "Share reports"},
    {"id": uuid.UUID("01000015-0000-0000-0000-000000000015"), "name": "report:delete", "resource": "report", "action": "delete", "description": "Delete reports"},

    # Export permissions
    {"id": uuid.UUID("01000016-0000-0000-0000-000000000016"), "name": "export:pdf", "resource": "export", "action": "pdf", "description": "Export to PDF"},
    {"id": uuid.UUID("01000017-0000-0000-0000-000000000017"), "name": "export:csv", "resource": "export", "action": "csv", "description": "Export to CSV"},
    {"id": uuid.UUID("01000018-0000-0000-0000-000000000018"), "name": "export:excel", "resource": "export", "action": "excel", "description": "Export to Excel"},
    {"id": uuid.UUID("01000019-0000-0000-0000-000000000019"), "name": "export:api", "resource": "export", "action": "api", "description": "Export via API"},

    # API permissions
    {"id": uuid.UUID("01000020-0000-0000-0000-000000000020"), "name": "api:access", "resource": "api", "action": "access", "description": "Basic API access"},
    {"id": uuid.UUID("01000021-0000-0000-0000-000000000021"), "name": "api:full", "resource": "api", "action": "full", "description": "Full API access"},

    # Organization permissions
    {"id": uuid.UUID("01000022-0000-0000-0000-000000000022"), "name": "org:dashboard", "resource": "org", "action": "dashboard", "description": "View organization dashboard"},
    {"id": uuid.UUID("01000023-0000-0000-0000-000000000023"), "name": "org:users:read", "resource": "org", "action": "users:read", "description": "View organization users"},
    {"id": uuid.UUID("01000024-0000-0000-0000-000000000024"), "name": "org:users:manage", "resource": "org", "action": "users:manage", "description": "Manage organization users"},
    {"id": uuid.UUID("01000025-0000-0000-0000-000000000025"), "name": "org:billing:read", "resource": "org", "action": "billing:read", "description": "View billing information"},
    {"id": uuid.UUID("01000026-0000-0000-0000-000000000026"), "name": "org:billing:manage", "resource": "org", "action": "billing:manage", "description": "Manage billing"},
    {"id": uuid.UUID("01000027-0000-0000-0000-000000000027"), "name": "org:settings:read", "resource": "org", "action": "settings:read", "description": "View organization settings"},
    {"id": uuid.UUID("01000028-0000-0000-0000-000000000028"), "name": "org:settings:manage", "resource": "org", "action": "settings:manage", "description": "Manage organization settings"},

    # Settings permissions
    {"id": uuid.UUID("01000029-0000-0000-0000-000000000029"), "name": "settings:read", "resource": "settings", "action": "read", "description": "View user settings"},
    {"id": uuid.UUID("01000030-0000-0000-0000-000000000030"), "name": "settings:manage", "resource": "settings", "action": "manage", "description": "Manage user settings"},

    # Admin permissions
    {"id": uuid.UUID("01000031-0000-0000-0000-000000000031"), "name": "admin:users:manage", "resource": "admin", "action": "users:manage", "description": "Manage all users"},
    {"id": uuid.UUID("01000032-0000-0000-0000-000000000032"), "name": "admin:plans:manage", "resource": "admin", "action": "plans:manage", "description": "Manage subscription plans"},
    {"id": uuid.UUID("01000033-0000-0000-0000-000000000033"), "name": "admin:features:manage", "resource": "admin", "action": "features:manage", "description": "Manage feature flags"},
    {"id": uuid.UUID("01000034-0000-0000-0000-000000000034"), "name": "admin:system:manage", "resource": "admin", "action": "system:manage", "description": "Manage system settings"},
]

# Role-Permission mappings
ROLE_PERMISSIONS: dict[str, list[str]] = {
    "guest": ["site:read", "content:read"],
    "free_user": ["site:read", "content:read", "analysis:create_limited", "report:read_basic"],
    "paid_user": [
        "site:read", "content:read", "content:write",
        "analysis:create", "analysis:create_concurrent",
        "report:read_basic", "report:read_detailed", "report:create",
        "export:pdf", "export:csv",
        "api:access",
        "settings:read", "settings:manage",
    ],
    "enterprise_user": [
        "site:read", "content:read", "content:write",
        "analysis:create", "analysis:create_concurrent", "analysis:read", "analysis:delete",
        "report:read_basic", "report:read_detailed", "report:read_advanced", "report:create", "report:share",
        "export:pdf", "export:csv", "export:excel", "export:api",
        "api:access", "api:full",
        "org:dashboard",
        "settings:read", "settings:manage",
    ],
    "admin": [
        "site:read", "content:read", "content:write", "content:delete",
        "analysis:create", "analysis:create_concurrent", "analysis:read", "analysis:delete",
        "report:read_basic", "report:read_detailed", "report:read_advanced", "report:create", "report:share", "report:delete",
        "export:pdf", "export:csv", "export:excel", "export:api",
        "api:access", "api:full",
        "org:dashboard", "org:users:read", "org:users:manage", "org:billing:read", "org:settings:read", "org:settings:manage",
        "settings:read", "settings:manage",
        "admin:users:manage", "admin:plans:manage", "admin:features:manage",
    ],
    "super_admin": [  # All permissions
        "*"
    ],
}


async def seed_roles_permissions(db: AsyncSession) -> tuple[list[Role], list[Permission]]:
    """
    Seed roles and permissions.

    Idempotent: Will update existing records instead of creating duplicates.

    Args:
        db: Database session

    Returns:
        Tuple of (roles, permissions)
    """
    # Seed permissions first
    seeded_permissions = {}
    for perm_data in DEFAULT_PERMISSIONS:
        result = await db.execute(
            select(Permission).where(Permission.id == perm_data["id"])
        )
        existing = result.scalar_one_or_none()

        if existing:
            for key, value in perm_data.items():
                if key != "id":
                    setattr(existing, key, value)
            seeded_permissions[perm_data["name"]] = existing
            logger.info(f"Updated permission: {perm_data['name']}")
        else:
            perm = Permission(**perm_data)
            db.add(perm)
            seeded_permissions[perm_data["name"]] = perm
            logger.info(f"Created permission: {perm_data['name']}")

    await db.commit()

    # Refresh permissions
    for perm in seeded_permissions.values():
        await db.refresh(perm)

    # Seed roles
    seeded_roles = {}
    for role_data in DEFAULT_ROLES:
        result = await db.execute(
            select(Role).where(Role.id == role_data["id"])
        )
        existing = result.scalar_one_or_none()

        if existing:
            for key, value in role_data.items():
                if key != "id":
                    setattr(existing, key, value)
            seeded_roles[role_data["name"]] = existing
            logger.info(f"Updated role: {role_data['name']}")
        else:
            role = Role(**role_data)
            db.add(role)
            seeded_roles[role_data["name"]] = role
            logger.info(f"Created role: {role_data['name']}")

    await db.commit()

    # Refresh roles
    for role in seeded_roles.values():
        await db.refresh(role)

    # Assign permissions to roles via the association table
    for role_name, perm_names in ROLE_PERMISSIONS.items():
        if role_name not in seeded_roles:
            continue

        role = seeded_roles[role_name]

        if "*" in perm_names:
            # Super admin gets all permissions
            perm_list = list(seeded_permissions.values())
        else:
            perm_list = [seeded_permissions[name] for name in perm_names if name in seeded_permissions]

        # Assign permissions using the relationship
        role.permissions = perm_list
        logger.info(f"Assigned {len(perm_list)} permissions to role: {role_name}")

    await db.commit()

    logger.info(f"Seeded {len(seeded_roles)} roles and {len(seeded_permissions)} permissions")
    return list(seeded_roles.values()), list(seeded_permissions.values())


async def rollback_roles_permissions(db: AsyncSession) -> None:
    """
    Rollback roles and permissions seeds.

    Args:
        db: Database session
    """
    # Delete permissions by known IDs
    for perm_data in DEFAULT_PERMISSIONS:
        result = await db.execute(
            select(Permission).where(Permission.id == perm_data["id"])
        )
        perm = result.scalar_one_or_none()
        if perm:
            await db.delete(perm)
            logger.info(f"Deleted permission: {perm_data['name']}")

    # Delete roles by known IDs
    for role_data in DEFAULT_ROLES:
        result = await db.execute(
            select(Role).where(Role.id == role_data["id"])
        )
        role = result.scalar_one_or_none()
        if role:
            await db.delete(role)
            logger.info(f"Deleted role: {role_data['name']}")

    await db.commit()
    logger.info("Rolled back roles and permissions")
