from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional, TYPE_CHECKING

from src.core.enums.scan import ScanTypeEnum

if TYPE_CHECKING:
    from src.infrastructure.database.models.scan_log import ScanLog


class AbstractScanLogRepository(ABC):

    @abstractmethod
    async def create_log(
        self,
        user_id: int,
        order_item_id: int,
        date_scan: datetime,
        type_scan: ScanTypeEnum,
    ) -> "ScanLog":
        raise NotImplementedError

    @abstractmethod
    async def get_first_log_for_ticket(
        self,
        order_item_id: int,
        type_scan: ScanTypeEnum = ScanTypeEnum.in_,
    ) -> Optional["ScanLog"]:
        raise NotImplementedError
