"""
ATLAS Platform - Opportunity Service

This service handles opportunity-related business logic.
"""

from collections.abc import Sequence

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.logging import get_logger
from backend.models import Opportunity, Project
from backend.schemas import OpportunityCreate, OpportunityUpdate

logger = get_logger(__name__)


class OpportunityService:
    """Service for opportunity-related operations."""

    def __init__(self, session: AsyncSession):
        """
        Initialize opportunity service.

        Args:
            session: Database session
        """
        self.session = session

    async def get_by_id(self, opportunity_id: str) -> Opportunity | None:
        """
        Get opportunity by ID.

        Args:
            opportunity_id: Opportunity ID

        Returns:
            Opportunity if found, None otherwise
        """
        result = await self.session.execute(
            select(Opportunity).where(Opportunity.id == opportunity_id)
        )
        return result.scalar_one_or_none()

    async def get_by_project(
        self,
        project_id: str,
        skip: int = 0,
        limit: int = 20,
    ) -> tuple[Sequence[Opportunity], int]:
        """
        Get opportunities for a project.

        Args:
            project_id: Project ID
            skip: Number of records to skip
            limit: Maximum number of records

        Returns:
            Tuple of (opportunities, total count)
        """
        query = select(Opportunity).where(Opportunity.project_id == project_id)

        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total = await self.session.scalar(count_query)

        # Get paginated results
        query = query.offset(skip).limit(limit)
        result = await self.session.execute(query)
        opportunities = result.scalars().all()

        return opportunities, total or 0

    async def get_user_opportunities(
        self,
        user_id: str,
        skip: int = 0,
        limit: int = 20,
    ) -> tuple[Sequence[Opportunity], int]:
        """
        Get opportunities for a user (through their projects).

        Args:
            user_id: User ID
            skip: Number of records to skip
            limit: Maximum number of records

        Returns:
            Tuple of (opportunities, total count)
        """
        # Get user's project IDs
        project_query = select(Project.id).where(Project.user_id == user_id)

        # Query opportunities from those projects
        query = select(Opportunity).where(Opportunity.project_id.in_(project_query))

        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total = await self.session.scalar(count_query)

        # Get paginated results
        query = query.offset(skip).limit(limit)
        result = await self.session.execute(query)
        opportunities = result.scalars().all()

        return opportunities, total or 0

    async def search_opportunities(
        self,
        query: str,
        category: str | None = None,
        industry: str | None = None,
        region: str | None = None,
        min_score: float | None = None,
        skip: int = 0,
        limit: int = 20,
    ) -> tuple[Sequence[Opportunity], int]:
        """
        Search opportunities.

        Args:
            query: Search query
            category: Category filter
            industry: Industry filter
            region: Region filter
            min_score: Minimum score filter
            skip: Number of records to skip
            limit: Maximum number of records

        Returns:
            Tuple of (opportunities, total count)
        """
        stmt = select(Opportunity)

        # Apply filters
        if query:
            search_pattern = f"%{query}%"
            stmt = stmt.where(
                Opportunity.title.ilike(search_pattern) |
                Opportunity.description.ilike(search_pattern)
            )

        if category:
            stmt = stmt.where(Opportunity.category == category)

        if industry:
            stmt = stmt.where(Opportunity.industry == industry)

        if region:
            stmt = stmt.where(Opportunity.region == region)

        if min_score is not None:
            stmt = stmt.where(Opportunity.score_overall >= min_score)

        # Get total count
        count_query = select(func.count()).select_from(stmt.subquery())
        total = await self.session.scalar(count_query)

        # Get paginated results
        stmt = stmt.order_by(Opportunity.score_overall.desc())
        stmt = stmt.offset(skip).limit(limit)

        result = await self.session.execute(stmt)
        opportunities = result.scalars().all()

        return opportunities, total or 0

    async def create(
        self,
        user_id: str,
        opportunity_data: OpportunityCreate,
    ) -> Opportunity:
        """
        Create a new opportunity.

        Args:
            user_id: User ID (for authorization)
            opportunity_data: Opportunity creation data

        Returns:
            Created opportunity
        """
        opportunity = Opportunity(
            title=opportunity_data.title,
            description=opportunity_data.description,
            category=opportunity_data.category,
            industry=opportunity_data.industry,
            project_id=opportunity_data.project_id,
            region=opportunity_data.region,
            country=opportunity_data.country,
            city=opportunity_data.city,
            score_overall=opportunity_data.score_overall,
            score_demand=opportunity_data.score_demand,
            score_growth=opportunity_data.score_growth,
            score_competition=opportunity_data.score_competition,
            score_risk=opportunity_data.score_risk,
            confidence=opportunity_data.confidence,
        )

        self.session.add(opportunity)
        await self.session.flush()

        logger.info(
            "Opportunity created",
            opportunity_id=opportunity.id,
            user_id=user_id,
        )

        return opportunity

    async def update(
        self,
        opportunity: Opportunity,
        opportunity_data: OpportunityUpdate,
    ) -> Opportunity:
        """
        Update opportunity.

        Args:
            opportunity: Opportunity to update
            opportunity_data: Update data

        Returns:
            Updated opportunity
        """
        update_data = opportunity_data.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(opportunity, field, value)

        await self.session.flush()

        logger.info("Opportunity updated", opportunity_id=opportunity.id)

        return opportunity

    async def delete(self, opportunity: Opportunity) -> None:
        """
        Delete opportunity.

        Args:
            opportunity: Opportunity to delete
        """
        await self.session.delete(opportunity)
        await self.session.flush()

        logger.info("Opportunity deleted", opportunity_id=opportunity.id)

    async def toggle_bookmark(self, opportunity: Opportunity) -> Opportunity:
        """
        Toggle opportunity bookmark status.

        Args:
            opportunity: Opportunity to bookmark

        Returns:
            Updated opportunity
        """
        opportunity.is_bookmarked = not opportunity.is_bookmarked
        await self.session.flush()

        logger.info(
            "Opportunity bookmark toggled",
            opportunity_id=opportunity.id,
            is_bookmarked=opportunity.is_bookmarked,
        )

        return opportunity
