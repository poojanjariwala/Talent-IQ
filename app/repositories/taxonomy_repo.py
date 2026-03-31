import uuid
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.audit import SkillTaxonomy


class TaxonomyRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all(self) -> List[SkillTaxonomy]:
        result = await self.db.execute(select(SkillTaxonomy))
        return list(result.scalars().all())

    async def get_by_canonical(self, name: str) -> Optional[SkillTaxonomy]:
        result = await self.db.execute(
            select(SkillTaxonomy).where(SkillTaxonomy.canonical_name == name)
        )
        return result.scalar_one_or_none()

    async def upsert_bulk(self, entries: List[dict]) -> int:
        count = 0
        for entry in entries:
            existing = await self.get_by_canonical(entry["canonical_name"])
            if existing:
                for k, v in entry.items():
                    setattr(existing, k, v)
            else:
                skill = SkillTaxonomy(**entry)
                self.db.add(skill)
                count += 1
        await self.db.flush()
        return count
