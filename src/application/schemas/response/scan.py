"""Scan response schemas."""
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, computed_field

from src.core.entities.zone import ScanZone
from src.core.enums.scan import ScanTypeEnum


class EventListItem(BaseModel):
    """Event item in list response."""
    id: int
    event_id: int
    event_name: str | None = None
    category_id: int | None = None
    category_name: str | None = None
    image: str | None = None
    date_time: datetime
    all_count: int = 0
    scan_count: int = 0
    theater_name: str | None = None
    address: str | None = None
    inCount: int = 0
    outCount: int = 0
    zone: ScanZone | None = Field(None, description="Зона, закреплённая за учёткой на этом сеансе")
    zone_locked: bool = Field(False, description="True — зона закреплена, выбор в приложении не показывать")


class EventListResponse(BaseModel):
    """Events list response."""
    events: list[EventListItem]


class ScanCountsResponse(BaseModel):
    """Scan counts response."""
    all_count: int
    scan_count: int
    in_count: int
    out_count: int


class ScanLogResponse(BaseModel):
    """Scan log line in check result (date, type, scanner name)."""
    date_scan: datetime
    type_scan: ScanTypeEnum
    full_name: str | None = None
    result: str | None = Field(None, description="Исход: allowed, already_used, wrong_event, wrong_zone, ticket_refund, order_cancelled, order_refund, order_failed")
    message: str | None = Field(None, description="Исход словами для экрана сканера")
    payload: dict | None = Field(None, description="Подробности скана: сеанс, зона, исход")


class ScanAttemptsResponse(BaseModel):
    """Сколько раз билет сканировали до текущего скана."""
    total: int = 0
    passed: int = Field(0, description="Проходы: входы и выходы")
    rejected: int = Field(0, description="Отказы: повторные сканы и ошибки")


class CheckResultResponse(BaseModel):
    """Unified scan check result matching frontend LastCheckResult type."""
    status: Literal["allowed", "already_used", "error_invalid", "wrong_event"]
    message: str
    place: str | None = None
    first_check_in: str | None = None
    scanned_by: str | None = None
    reason: str | None = None
    error_code: str | None = Field(None, description="Уточнение отказа: wrong_zone — билет из другой зоны")
    event_name: str | None = None
    event_date: str | None = None
    counts: ScanCountsResponse | None = None
    scan_logs: list[ScanLogResponse] = Field(default_factory=list, description="Прежние сканы этого билета")
    attempts: ScanAttemptsResponse | None = Field(None, description="Итог по прежним сканам билета")


class ZoneCounts(BaseModel):
    """Счётчики по действующим билетам."""
    all_count: int = Field(0, description="Всего билетов")
    scan_count: int = Field(0, description="Пришли: отсканированы хотя бы раз")
    in_count: int = Field(0, description="Сейчас внутри")
    out_count: int = Field(0, description="Вышли")

    @computed_field(description="Ещё не пришли")
    @property
    def left_count(self) -> int:
        return max(self.all_count - self.scan_count, 0)


class ZoneNamedOption(ZoneCounts):
    title: str | None = None
    zone: ScanZone


class ZoneSectorOption(ZoneCounts):
    sector: str = Field(description="Значение для поля sectors зоны. Пустая строка — места без сектора")

    @computed_field(description="Название для экрана")
    @property
    def title(self) -> str:
        return self.sector or "Без сектора"


class ZoneTicketOption(ZoneCounts):
    id: int
    title: str | None = None


class ZoneStatisticResponse(BaseModel):
    """Сеанс в разбивке по зонам: сколько пришло и сколько осталось.
    Из этих же строк контролёр собирает зону, если она не закреплена."""
    zone: ScanZone | None = Field(None, description="Зона, закреплённая за учёткой на этом сеансе")
    zone_locked: bool = Field(False, description="True — зона закреплена, выбор в приложении не показывать")
    total: ZoneCounts = Field(default_factory=ZoneCounts, description="Весь сеанс")
    seats: ZoneCounts = Field(default_factory=ZoneCounts, description="Все билеты с местом")
    entry: ZoneCounts = Field(default_factory=ZoneCounts, description="Все входные билеты (без места)")
    zones: list[ZoneNamedOption] = Field(default_factory=list, description="Зоны, назначенные контролёрам в админке")
    sectors: list[ZoneSectorOption] = Field(default_factory=list, description="Билеты с местом по секторам")
    types: list[ZoneTicketOption] = Field(default_factory=list, description="Билеты без места по типам")
    areas: list[ZoneTicketOption] = Field(default_factory=list, description="Билеты без места по областям схемы")
    options: list[ZoneTicketOption] = Field(
        default_factory=list,
        description="Доп. опции сеанса (Fast Track и т.п.): считаются отдельно, в счётчики билетов не входят",
    )


class TicketListItem(BaseModel):
    """Ticket item in list response."""
    id: int
    serial_number: str | None = None
    checked: bool = False
    order_status: str | None = None
    ticket_type: str | None = None
    place: str | None = None
    price: int
    qr_number: str | None = None
    user_name: str | None = None
    user_email: str | None = None
    user_phone: str | None = None
    order_date: datetime | None = None


class TicketListResponse(BaseModel):
    """Ticket list response."""
    result: int = 0
    status: str = "success"
    payload: list[TicketListItem] = []


class TicketResponse(BaseModel):
    """Single ticket response."""
    id: int
    serial_number: str | None = None
    price: int
    checked: bool = False
    session_id: int
    title: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None


class StatisticResponse(BaseModel):
    """Session statistics response."""
    salesAmount: float = 0
    numberOfTickets: int = 0
    numberOfRefundedTickets: int = 0
