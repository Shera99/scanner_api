import logging
from datetime import datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession

from src.application.repositories.scan_log import AbstractScanLogRepository
from src.application.repositories.ticket import AbstractTicketRepository
from src.application.schemas.response import (
    CheckResultResponse,
    ScanAttemptsResponse,
    ScanCountsResponse,
    ScanLogResponse,
)
from src.application.services.crypto import TicketCryptographyService
from src.application.services.scan.counts_cache import counts_cache
from src.core.config import settings
from src.core.entities import ScanType, SCAN_TYPE_VALUES, SCAN_ALLOWED_MESSAGES, SCAN_ALREADY_USED_MESSAGES
from src.core.entities.zone import ScanZone, zone_for_session
from src.core.enums.order import ORDER_REJECT_REASONS
from src.core.enums.scan import (
    ScanResultEnum,
    ScanTypeEnum,
    SCAN_LOG_TYPE,
    ERROR_SCAN_LOG_TYPE,
    ORDER_REJECT_RESULTS,
    scan_log_message,
    scan_log_result,
)
from src.core.exceptions import BadRequestException

logger = logging.getLogger(__name__)


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
        account_zone: ScanZone | None = None,
        requested_zone: ScanZone | None = None,
    ) -> CheckResultResponse:
        ticket_number = self._resolve_ticket_number(code, no_code)

        ticket = await self.ticket_repo.get_ticket_for_check(ticket_number)

        if ticket is None:
            return CheckResultResponse(
                status="error_invalid",
                message="ОШИБКА / НЕДЕЙСТВИТЕЛЕН",
                reason="Билет не найден",
            )

        scan_value = SCAN_TYPE_VALUES[scan_type]
        tz_diff = time_zone_difference or settings.time_zone_difference
        event_name, event_date = self._extract_event_info(ticket, tz_diff)
        zone, zone_locked = zone_for_session(session_id, account_zone, requested_zone)

        # Всё нужное от билета берём до записи в базу: после сбоя записи
        # объект билета читать уже нельзя.
        ticket_id = ticket.id
        place = ticket.title
        order_status = ticket.order.status if ticket.order else None
        is_option = ticket.session_option_id is not None

        scan_logs = await self._scan_logs_for_ticket(ticket_id)
        attempts = self._attempts(scan_logs)

        async def log_rejection(result: ScanResultEnum) -> None:
            await self._log_rejection(
                user_id=user_id,
                ticket_id=ticket_id,
                scan_value=scan_value,
                result=result,
                payload=self._log_payload(result, session_id, zone, zone_locked),
            )

        # Проверка session_id: разрешаем если совпадает или если билет из сессии
        if ticket.session_id != session_id:
            if ticket.session_id != 37 and ticket.session_id != 35:
                await log_rejection(ScanResultEnum.wrong_event)
                return CheckResultResponse(
                    status="wrong_event",
                    message="НЕ ДЛЯ ЭТОГО МЕРОПРИЯТИЯ",
                    event_name=event_name,
                    event_date=event_date,
                    place=place,
                    scan_logs=scan_logs,
                    attempts=attempts,
                )

        if ticket.is_refund:
            await log_rejection(ScanResultEnum.ticket_refund)
            return CheckResultResponse(
                status="error_invalid",
                message="ОШИБКА / НЕДЕЙСТВИТЕЛЕН",
                reason="Билет отменен (возврат)",
                place=place,
                scan_logs=scan_logs,
                attempts=attempts,
            )

        if order_status in ORDER_REJECT_REASONS:
            await log_rejection(ORDER_REJECT_RESULTS[order_status])
            return CheckResultResponse(
                status="error_invalid",
                message="ОШИБКА / НЕДЕЙСТВИТЕЛЕН",
                reason=ORDER_REJECT_REASONS[order_status],
                place=place,
                scan_logs=scan_logs,
                attempts=attempts,
            )

        if zone is not None and not self._ticket_in_zone(ticket, zone):
            await log_rejection(ScanResultEnum.wrong_zone)
            return CheckResultResponse(
                status="error_invalid",
                message="ДРУГАЯ ЗОНА",
                reason=f"Билет не для зоны «{zone.title}»" if zone.title else "Билет не для этой зоны",
                error_code="wrong_zone",
                place=place,
                event_name=event_name,
                event_date=event_date,
                scan_logs=scan_logs,
                attempts=attempts,
            )

        current_time = datetime.utcnow()
        was_checked = bool(ticket.checked)
        was_in_out = ticket.in_out

        already_used = was_checked and scan_value == was_in_out
        if not already_used:
            already_used = not await self.ticket_repo.mark_ticket_scanned(
                ticket_id=ticket_id,
                in_out=scan_value,
                updated_at=current_time,
            )

        if already_used:
            first_check_in, scanned_by = await self._get_first_scan_info(
                ticket_id, tz_diff, SCAN_LOG_TYPE[scan_value],
            )
            await log_rejection(ScanResultEnum.already_used)

            return CheckResultResponse(
                status="already_used",
                message=SCAN_ALREADY_USED_MESSAGES[scan_value],
                place=place,
                first_check_in=first_check_in,
                scanned_by=scanned_by,
                event_name=event_name,
                event_date=event_date,
                scan_logs=scan_logs,
                attempts=attempts,
            )

        await self.scan_log_repo.create_log(
            user_id=user_id,
            order_item_id=ticket_id,
            date_scan=current_time,
            type_scan=SCAN_LOG_TYPE[scan_value],
            payload=self._log_payload(ScanResultEnum.allowed, session_id, zone, zone_locked),
        )

        await self.db_session.commit()

        delta = self._scan_delta(was_checked, was_in_out, scan_value)
        if is_option and zone is None:
            # доп. опция — не билет: счётчики билетов сеанса её скан не меняет
            delta = dict.fromkeys(delta, 0)
        counts = await self._counts_after_scan(session_id, zone, delta)

        return CheckResultResponse(
            status="allowed",
            message=SCAN_ALLOWED_MESSAGES[scan_value],
            place=place,
            counts=counts,
            event_name=event_name,
            event_date=event_date,
            scan_logs=scan_logs,
            attempts=attempts,
        )

    async def _log_rejection(
        self,
        user_id: int,
        ticket_id: int,
        scan_value: int,
        result: ScanResultEnum,
        payload: dict,
    ) -> None:
        # Причина отказа хранится в payload. Пока этой колонки нет, запись о чужом
        # мероприятии или возврате выглядела бы как повторный вход, поэтому без
        # колонки в журнал идут только повторы — как и раньше.
        if result is not ScanResultEnum.already_used and not settings.scan_zone_columns:
            return

        # Отказ контролёр увидит в любом случае: сбой записи в журнал его не отменяет.
        try:
            await self.scan_log_repo.create_log(
                user_id=user_id,
                order_item_id=ticket_id,
                date_scan=datetime.utcnow(),
                type_scan=ERROR_SCAN_LOG_TYPE[scan_value],
                payload=payload,
            )
            await self.db_session.commit()
        except Exception:
            logger.exception("Отказ %s по билету %s не записан в журнал", result.value, ticket_id)

    @staticmethod
    def _attempts(scan_logs: list[ScanLogResponse]) -> ScanAttemptsResponse:
        passed = sum(1 for log in scan_logs if log.type_scan in (ScanTypeEnum.in_, ScanTypeEnum.out))
        return ScanAttemptsResponse(total=len(scan_logs), passed=passed, rejected=len(scan_logs) - passed)

    @staticmethod
    def _ticket_in_zone(ticket, zone: ScanZone) -> bool:
        sector = ticket.ticket_seat.sector if ticket.ticket_seat else None
        return zone.allows(
            ticket_seat_id=ticket.ticket_seat_id,
            sector=sector,
            ticket_type_id=ticket.ticket_type_id,
            ticket_area_id=ticket.ticket_area_id,
            session_option_id=ticket.session_option_id,
        )

    @staticmethod
    def _log_payload(
        result: ScanResultEnum,
        session_id: int,
        zone: ScanZone | None,
        zone_locked: bool,
    ) -> dict:
        payload: dict = {"result": result.value, "session_id": session_id}
        if zone is not None:
            payload["zone"] = zone.model_dump(exclude_defaults=True)
            payload["zone_source"] = "account" if zone_locked else "app"
        return payload

    @staticmethod
    def _scan_delta(was_checked: bool, was_in_out: int | None, scan_value: int) -> dict:
        """Как один успешный скан меняет счётчики сеанса."""
        was_in = was_checked and was_in_out == 1
        was_out = was_checked and was_in_out == 0
        return {
            "all_count": 0,
            "scan_count": 0 if was_checked else 1,
            "in_count": int(scan_value == 1) - int(was_in),
            "out_count": int(scan_value == 0) - int(was_out),
        }

    async def _counts_after_scan(
        self,
        session_id: int,
        zone: ScanZone | None,
        delta: dict,
    ) -> ScanCountsResponse | None:
        key = (session_id, zone.cache_key() if zone is not None else "")

        counts = counts_cache.get(key)
        if counts is not None:
            for name, change in delta.items():
                counts[name] = max(counts[name] + change, 0)
            return ScanCountsResponse(**counts)

        try:
            counts = await self.ticket_repo.get_ticket_counts(session_id, zone)
        except Exception:
            # Билет уже погашен и сохранён: сбой счётчиков не должен превращать
            # разрешённый проход в ошибку. Отдаём последние известные числа.
            logger.exception("Счётчики сеанса %s не посчитаны", session_id)
            counts = counts_cache.get(key, stale=True)
            return ScanCountsResponse(**counts) if counts is not None else None

        counts_cache.put(key, counts)
        return ScanCountsResponse(**counts)

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
        ticket = await self.ticket_repo.get_ticket_for_check(serial_number)

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

        history = []
        for log in logs:
            result = scan_log_result(log.type_scan, log.payload)
            history.append(ScanLogResponse(
                date_scan=log.date_scan,
                type_scan=log.type_scan,
                full_name=log.full_name,
                result=result,
                message=scan_log_message(log.type_scan, result),
                payload=log.payload,
            ))
        return history
