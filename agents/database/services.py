"""
TwisterLab Database Services
Service layer for database operations
"""

from typing import List, Optional
from sqlalchemy import select, update, delete, and_, or_, func
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timezone
import uuid

from .models import SOP
from ..api.models_sops import SOPCreate, SOPUpdate, SOPResponse


class SOPService:
    """Service class for SOP database operations."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_sop(self, sop_data: SOPCreate, created_by: str = "system") -> SOPResponse:
        """
        Create a new SOP.

        Args:
            sop_data: SOP creation data
            created_by: User who created the SOP

        Returns:
            Created SOP response model

        Raises:
            IntegrityError: If SOP creation fails due to database constraints
        """
        sop_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc)

        sop = SOP(
            id=sop_id,
            title=sop_data.title,
            description=sop_data.description,
            category=sop_data.category,
            priority=sop_data.priority,
            steps=sop_data.steps,
            applicable_issues=sop_data.applicable_issues,
            is_active=True,
            version=1,
            created_at=now,
            updated_at=now,
            created_by=created_by
        )

        self.session.add(sop)
        await self.session.commit()
        await self.session.refresh(sop)

        return self._sop_to_response(sop)

    async def get_sop_by_id(self, sop_id: str) -> Optional[SOPResponse]:
        """
        Get SOP by ID.

        Args:
            sop_id: SOP identifier

        Returns:
            SOP response model or None if not found
        """
        stmt = select(SOP).where(SOP.id == sop_id)
        result = await self.session.execute(stmt)
        sop = result.scalar_one_or_none()
        return self._sop_to_response(sop) if sop else None

    async def list_sops(
        self,
        category: Optional[str] = None,
        is_active: Optional[bool] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[SOPResponse]:
        """
        List SOPs with optional filtering and pagination.

        Args:
            category: Filter by category
            is_active: Filter by active status
            limit: Maximum number of results
            offset: Number of results to skip

        Returns:
            List of SOP response models
        """
        stmt = select(SOP)

        # Apply filters
        conditions = []
        if category:
            conditions.append(SOP.category == category)
        if is_active is not None:
            conditions.append(SOP.is_active == is_active)

        if conditions:
            stmt = stmt.where(and_(*conditions))

        # Apply ordering and pagination
        stmt = stmt.order_by(SOP.created_at.desc()).limit(limit).offset(offset)

        result = await self.session.execute(stmt)
        sops = list(result.scalars().all())
        return [self._sop_to_response(sop) for sop in sops]

    async def update_sop(self, sop_id: str, update_data: SOPUpdate) -> Optional[SOPResponse]:
        """
        Update an existing SOP.

        Args:
            sop_id: SOP identifier
            update_data: Data to update

        Returns:
            Updated SOP response model or None if not found

        Raises:
            NoResultFound: If SOP doesn't exist
        """
        # Get current SOP
        sop = await self.get_sop_by_id(sop_id)
        if not sop:
            return None

        # Get the database instance for updating
        stmt = select(SOP).where(SOP.id == sop_id)
        result = await self.session.execute(stmt)
        db_sop = result.scalar_one()

        # Prepare update data
        update_dict = update_data.model_dump(exclude_unset=True)
        if update_dict:
            update_dict["updated_at"] = datetime.now(timezone.utc)
            update_dict["version"] = db_sop.version + 1

            # Update the SOP
            stmt = (
                update(SOP)
                .where(SOP.id == sop_id)
                .values(**update_dict)
            )
            await self.session.execute(stmt)
            await self.session.commit()

            # Refresh the instance
            await self.session.refresh(db_sop)

        return self._sop_to_response(db_sop)

    async def delete_sop(self, sop_id: str) -> bool:
        """
        Delete an SOP.

        Args:
            sop_id: SOP identifier

        Returns:
            True if deleted, False if not found
        """
        stmt = delete(SOP).where(SOP.id == sop_id)
        result = await self.session.execute(stmt)
        await self.session.commit()

        return result.rowcount > 0

    async def get_sops_by_category(self, category: str, limit: int = 50) -> List[SOP]:
        """
        Get SOPs by category.

        Args:
            category: SOP category
            limit: Maximum number of results

        Returns:
            List of SOPs in the specified category
        """
        return await self.list_sops(category=category, limit=limit)

    async def count_sops(
        self,
        category: Optional[str] = None,
        is_active: Optional[bool] = None
    ) -> int:
        """
        Count SOPs with optional filtering.

        Args:
            category: Filter by category
            is_active: Filter by active status

        Returns:
            Number of SOPs matching criteria
        """
        stmt = select(func.count(SOP.id))

        # Apply filters
        conditions = []
        if category:
            conditions.append(SOP.category == category)
        if is_active is not None:
            conditions.append(SOP.is_active == is_active)

        if conditions:
            stmt = stmt.where(and_(*conditions))

        result = await self.session.execute(stmt)
        return result.scalar() or 0

    async def search_sops(self, query: str, limit: int = 20) -> List[SOP]:
        """
        Search SOPs by title or description.

        Args:
            query: Search query
            limit: Maximum number of results

        Returns:
            List of matching SOPs
        """
        search_term = f"%{query}%"
        stmt = select(SOP).where(
            or_(
                SOP.title.ilike(search_term),
                SOP.description.ilike(search_term)
            )
        ).order_by(SOP.created_at.desc()).limit(limit)

        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    def _sop_to_response(self, sop: SOP) -> SOPResponse:
        """Convert SOP database model to SOPResponse."""
        return SOPResponse(
            id=sop.id,
            title=sop.title,
            description=sop.description,
            category=sop.category,
            priority=sop.priority,
            steps=sop.steps,
            applicable_issues=sop.applicable_issues,
            is_active=sop.is_active,
            version=sop.version,
            created_by=sop.created_by,
            created_at=sop.created_at.isoformat(),
            updated_at=sop.updated_at.isoformat()
        )