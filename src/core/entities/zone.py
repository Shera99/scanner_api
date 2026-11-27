"""Зона сканирования: какие билеты пропускает сканер."""
import json
import logging
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator

logger = logging.getLogger(__name__)


class ScanZone(BaseModel):
    """Фильтр билетов. Один и тот же формат хранится у учётки контролёра
    (user_permissions.scan_zone) и приходит от приложения в /check.

    Билет подходит, если сработало хотя бы одно правило. Зона без правил
    ничего не ограничивает.
    """
    model_config = ConfigDict(extra="ignore")

    title: str | None = Field(None, description="Название зоны для экрана сканера")
    session_ids: list[int] = Field(
        default_factory=list,
        description="Сеансы, на которых зона действует. Пусто — на всех",
    )
    all_seats: bool = Field(False, description="Все билеты с местом")
    sectors: list[str] = Field(
        default_factory=list,
        description="Билеты с местом в этих секторах. Пустая строка — места без сектора",
    )
    all_entry: bool = Field(False, description="Все входные билеты (без места)")
    type_ids: list[int] = Field(default_factory=list, description="Входные билеты этих типов (ticket_types.id)")
    area_ids: list[int] = Field(default_factory=list, description="Входные билеты этих областей схемы (ticket_areas.id)")
    option_ids: list[int] = Field(
        default_factory=list,
        description="Доп. опции сеанса, например Fast Track (session_options.id)",
    )

    @field_validator("session_ids", "sectors", "type_ids", "area_ids", "option_ids", mode="before")
    @classmethod
    def _none_as_empty(cls, value: Any) -> Any:
        return [] if value is None else value

    @field_validator("sectors", mode="before")
    @classmethod
    def _sectors_as_str(cls, value: Any) -> Any:
        # Сектор в базе — строка, а из админки и приложения он может прийти числом.
        if isinstance(value, (list, tuple)):
            return [str(item).strip() for item in value if item is not None]
        return value

    @property
    def has_rules(self) -> bool:
        return bool(
            self.all_seats or self.sectors or self.all_entry
            or self.type_ids or self.area_ids or self.option_ids
        )

    def applies_to(self, session_id: int) -> bool:
        return not self.session_ids or session_id in self.session_ids

    def allows(
        self,
        ticket_seat_id: int | None,
        sector: str | None,
        ticket_type_id: int | None,
        ticket_area_id: int | None,
        session_option_id: int | None = None,
    ) -> bool:
        if session_option_id is not None:
            # доп. опция — не билет: правила для билетов её не касаются
            return session_option_id in self.option_ids
        if ticket_seat_id is not None:
            # место без сектора считается сектором с пустым названием
            if self.all_seats or (sector or "").strip() in self.sectors:
                return True
        elif self.all_entry:
            return True
        if ticket_type_id is not None and ticket_type_id in self.type_ids:
            return True
        if ticket_area_id is not None and ticket_area_id in self.area_ids:
            return True
        return False

    def cache_key(self) -> str:
        return json.dumps([
            self.all_seats,
            sorted(self.sectors),
            self.all_entry,
            sorted(self.type_ids),
            sorted(self.area_ids),
            sorted(self.option_ids),
        ], ensure_ascii=False)

    @classmethod
    def parse(cls, raw: Any) -> "ScanZone | None":
        """Зона из JSON учётки. Битое значение не должно останавливать вход:
        такая учётка сканирует без ограничения, а в лог уходит предупреждение."""
        if not raw:
            return None
        try:
            zone = cls.model_validate(raw)
        except Exception as e:
            logger.warning("scan_zone не разобран, зона не применяется: %s | %r", e, raw)
            return None
        return zone if zone.has_rules else None


def zone_for_session(
    session_id: int,
    account_zone: ScanZone | None,
    requested_zone: ScanZone | None = None,
) -> tuple[ScanZone | None, bool]:
    """Какая зона действует на сеансе и закреплена ли она за учёткой.

    Зона из админки важнее выбора в приложении: пока она действует на сеансе,
    присланная приложением зона не учитывается.
    """
    if account_zone is not None and account_zone.has_rules and account_zone.applies_to(session_id):
        return account_zone, True
    if requested_zone is not None and requested_zone.has_rules:
        return requested_zone, False
    return None, False
