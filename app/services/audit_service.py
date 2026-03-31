"""
Audit service: records processing steps for each candidate.
"""
import uuid
from datetime import datetime
from typing import Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.audit import AuditEntry


class AuditService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def log(
        self,
        candidate_id: uuid.UUID,
        step: str,
        status: str,
        message: Optional[str] = None,
        detail: Optional[Dict[str, Any]] = None,
    ) -> AuditEntry:
        entry = AuditEntry(
            candidate_id=candidate_id,
            step=step,
            status=status,
            message=message,
            detail=detail or {},
        )
        self.db.add(entry)
        await self.db.flush()
        return entry

    async def log_ok(self, candidate_id: uuid.UUID, step: str, message: str = "", detail: Optional[Dict] = None):
        return await self.log(candidate_id, step, "ok", message, detail)

    async def log_warn(self, candidate_id: uuid.UUID, step: str, message: str = "", detail: Optional[Dict] = None):
        return await self.log(candidate_id, step, "warn", message, detail)

    async def log_error(self, candidate_id: uuid.UUID, step: str, message: str = "", detail: Optional[Dict] = None):
        return await self.log(candidate_id, step, "error", message, detail)
