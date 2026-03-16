from datetime import datetime
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from src.application.repositories.scan_log import AbstractScanLogRepository
from src.core.enums.scan import ScanTypeEnum
from src.infrastructure.database.models.scan_log import ScanLog


class ScanLogRepository(AbstractScanLogRepository):

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_log(
        self,
        user_id: int,
        order_item_id: int,
        date_scan: datetime,
        type_scan: ScanTypeEnum,
    ) -> ScanLog:
        log = ScanLog(
            user_id=user_id,
            order_item_id=order_item_id,
            date_scan=date_scan,
            type_scan=type_scan,
        )
        self.session.add(log)
        await self.session.flush()
        return log

    async def get_first_log_for_ticket(
        self,
        order_item_id: int,
        type_scan: ScanTypeEnum = ScanTypeEnum.in_,
    ) -> Optional[ScanLog]:
        result = await self.session.execute(
            select(ScanLog)
            .options(joinedload(ScanLog.user))
            .where(
                ScanLog.order_item_id == order_item_id,
                ScanLog.type_scan == type_scan,
            )
            .order_by(ScanLog.date_scan.asc())
            .limit(1)
        )
        return result.scalars().first()
