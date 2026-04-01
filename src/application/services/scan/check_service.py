from datetime import datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession

from src.application.repositories.scan_log import AbstractScanLogRepository
from src.application.repositories.ticket import AbstractTicketRepository
from src.application.schemas.response import CheckResultResponse, ScanCountsResponse, ScanLogResponse
from src.application.services.crypto import TicketCryptographyService
from src.core.config import settings
from src.core.entities import ScanType, SCAN_TYPE_VALUES, SCAN_ALLOWED_MESSAGES, SCAN_ALREADY_USED_MESSAGES
from src.core.enums.order import ORDER_REJECT_REASONS
from src.core.enums.scan import ScanTypeEnum, SCAN_LOG_TYPE
from src.core.exceptions import BadRequestException


class ScanCheckService:

    def __init__(
        self,
        ticket_repo: AbstractTicketRepository,
        scan_log_repo: AbstractScanLogRepository,
        db_session: AsyncSession,
    ):
        self.ticket_repo = ticket_repo
        self.scan_log_repo = scan_log_repo
        self.db_session = db_session
        self.crypto_service = TicketCryptographyService()

    async def check_ticket(
        self,
        session_id: int,
        scan_type: ScanType,
        user_id: int,
        code: str | None = None,
        no_code: str | None = None,
        time_zone_difference: int | None = None,
    ) -> CheckResultResponse:
        ticket_number = self._resolve_ticket_number(code, no_code)

        ticket = await self.ticket_repo.get_ticket_by_session_and_serial(
            session_id=session_id,
            serial_number=ticket_number,
        )

        if ticket is None:
            return await self._handle_ticket_not_in_session(
                serial_number=ticket_number,
                time_zone_difference=time_zone_difference,
            )

        scan_logs = await self._scan_logs_for_ticket(ticket.id)

        if ticket.is_refund:
            return CheckResultResponse(
                status="error_invalid",
                message="ОШИБКА / НЕДЕЙСТВИТЕЛЕН",
                reason="Билет отменен (возврат)",
                place=ticket.title,
                scan_logs=scan_logs,
            )

        if ticket.order and ticket.order.status in ORDER_REJECT_REASONS:
            return CheckResultResponse(
                status="error_invalid",
                message="ОШИБКА / НЕДЕЙСТВИТЕЛЕН",
                reason=ORDER_REJECT_REASONS[ticket.order.status],
                place=ticket.title,
                scan_logs=scan_logs,
            )

        scan_value = SCAN_TYPE_VALUES[scan_type]
        tz_diff = time_zone_difference or settings.time_zone_difference
        event_name, event_date = self._extract_event_info(ticket, tz_diff)

        if ticket.checked and scan_value == ticket.in_out:
            first_check_in, scanned_by = await self._get_first_scan_info(
                ticket.id, tz_diff, SCAN_LOG_TYPE[scan_value],
            )
            return CheckResultResponse(
                status="already_used",
                message=SCAN_ALREADY_USED_MESSAGES[scan_value],
                place=ticket.title,
                first_check_in=first_check_in,
                scanned_by=scanned_by,
                event_name=event_name,
                event_date=event_date,
                scan_logs=scan_logs,
            )

        current_time = datetime.utcnow()
        await self.ticket_repo.update_ticket_scan(
            ticket=ticket,
            checked=True,
            in_out=scan_value,
            updated_at=current_time,
        )

        await self.scan_log_repo.create_log(
            user_id=user_id,
            order_item_id=ticket.id,
            date_scan=current_time,
            type_scan=SCAN_LOG_TYPE[scan_value],
        )

        await self.db_session.commit()

        ticket_counts = await self.ticket_repo.get_ticket_counts(session_id)
        counts = ScanCountsResponse(
            all_count=ticket_counts["all_count"],
            scan_count=ticket_counts["scan_count"],
            in_count=ticket_counts["in_count"],
            out_count=ticket_counts["out_count"],
        )

        return CheckResultResponse(
            status="allowed",
            message=SCAN_ALLOWED_MESSAGES[scan_value],
            place=ticket.title,
            counts=counts,
            event_name=event_name,
            event_date=event_date,
            scan_logs=scan_logs,
        )

    def _resolve_ticket_number(self, code: str | None, no_code: str | None) -> str:
        if code:
            ticket_number = self.crypto_service.decrypt(code)
            if ticket_number is None:
                raise BadRequestException("Невалидный QR-код")
            return ticket_number

        if not no_code:
            raise BadRequestException("Не указан номер билета!")
        return no_code

    @staticmethod
    def _extract_event_info(ticket, tz_diff: int) -> tuple[str | None, str | None]:
        if ticket.session and ticket.session.event:
            event_name = ticket.session.event.title_ru
            adjusted = ticket.session.date_time + timedelta(hours=tz_diff)
            event_date = adjusted.strftime("%d.%m.%Y")
            return event_name, event_date
        return None, None

    async def _handle_ticket_not_in_session(
        self,
        serial_number: str,
        time_zone_difference: int | None,
    ) -> CheckResultResponse:
        ticket = await self.ticket_repo.get_ticket_by_serial(serial_number)

        if ticket is None:
            return CheckResultResponse(
                status="error_invalid",
                message="ОШИБКА / НЕДЕЙСТВИТЕЛЕН",
                reason="Билет не найден",
            )

        tz_diff = time_zone_difference or settings.time_zone_difference
        event_name, event_date = self._extract_event_info(ticket, tz_diff)

        scan_logs = await self._scan_logs_for_ticket(ticket.id)

        return CheckResultResponse(
            status="wrong_event",
            message="НЕ ДЛЯ ЭТОГО МЕРОПРИЯТИЯ",
            event_name=event_name,
            event_date=event_date,
            place=ticket.title,
            scan_logs=scan_logs,
        )

    async def _get_first_scan_info(
        self,
        order_item_id: int,
        time_zone_difference: int,
        type_scan: ScanTypeEnum = ScanTypeEnum.in_,
    ) -> tuple[str | None, str | None]:
        log = await self.scan_log_repo.get_first_log_for_ticket(order_item_id, type_scan)
        if not log:
            return None, None

        adjusted = log.date_scan + timedelta(hours=time_zone_difference)
        first_check_in = adjusted.strftime("%H:%M:%S")
        scanned_by = log.user.full_name if log.user else None
        return first_check_in, scanned_by

    async def _scan_logs_for_ticket(self, order_item_id: int) -> list[ScanLogResponse]:
        logs = await self.scan_log_repo.get_logs_for_ticket(order_item_id)
        return [ScanLogResponse.model_validate(log) for log in logs]
