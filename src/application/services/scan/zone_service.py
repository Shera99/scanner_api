import re

from src.application.repositories.ticket import AbstractTicketRepository
from src.application.repositories.user import AbstractUserRepository
from src.application.schemas.response import (
    ZoneCounts,
    ZoneNamedOption,
    ZoneSectorOption,
    ZoneStatisticResponse,
    ZoneTicketOption,
)
from src.application.services.scan.counts_cache import counts_cache
from src.core.entities.zone import ScanZone, zone_for_session

_COUNT_FIELDS = ("all_count", "scan_count", "in_count", "out_count")


def _natural_key(value: str) -> list:
    """«Сектор 10» после «Сектор 9»."""
    return [
        (0, int(part), "") if part.isdigit() else (1, 0, part.lower())
        for part in re.split(r"(\d+)", value) if part
    ]


def _add(target: ZoneCounts, row: dict) -> None:
    for field in _COUNT_FIELDS:
        setattr(target, field, getattr(target, field) + row[field])


class ZoneService:

    def __init__(self, ticket_repo: AbstractTicketRepository, user_repo: AbstractUserRepository):
        self.ticket_repo = ticket_repo
        self.user_repo = user_repo

    async def get_statistics(
        self,
        session_id: int,
        account_zone: ScanZone | None = None,
    ) -> ZoneStatisticResponse:
        zone, zone_locked = zone_for_session(session_id, account_zone)
        data = await self._session_data(session_id)

        total = ZoneCounts()
        seats = ZoneCounts()
        entry = ZoneCounts()
        sectors = {name: ZoneSectorOption(sector=name) for name in data["sectors"]}
        types = {row["id"]: ZoneTicketOption(id=row["id"], title=row["title_ru"]) for row in data["types"]}
        areas = {row["id"]: ZoneTicketOption(id=row["id"], title=row["title_ru"]) for row in data["areas"]}
        options = {row["id"]: ZoneTicketOption(id=row["id"], title=row["title_ru"]) for row in data["options"]}
        zones = self._named_zones(data["zones"], zone)

        # Строка sold — группа билетов с одинаковыми типом, областью и сектором.
        # Билеты с местом делятся только по секторам, билеты без места — по
        # типам и областям схемы, так что один билет не попадает в две строки.
        # Зоны контролёров считаются по ScanZone.allows, как при проверке билета.
        for row in data["sold"]:
            option_id = row.get("session_option_id")
            targets: list[ZoneCounts] = []
            if option_id is not None:
                # доп. опция (Fast Track) — не билет: считается отдельно от билетов
                if option_id in options:
                    targets.append(options[option_id])
            elif row["seated"]:
                targets.append(total)
                targets.append(seats)
                targets.append(sectors.setdefault(row["sector"], ZoneSectorOption(sector=row["sector"])))
            else:
                targets.append(total)
                targets.append(entry)
                if row["ticket_type_id"] in types:
                    targets.append(types[row["ticket_type_id"]])
                elif row["ticket_area_id"] in areas:
                    targets.append(areas[row["ticket_area_id"]])
            targets.extend(
                named for named in zones
                if named.zone.allows(
                    ticket_seat_id=1 if row["seated"] else None,
                    sector=row["sector"],
                    ticket_type_id=row["ticket_type_id"],
                    ticket_area_id=row["ticket_area_id"],
                    session_option_id=option_id,
                )
            )

            for target in targets:
                _add(target, row)

        return ZoneStatisticResponse(
            zone=zone,
            zone_locked=zone_locked,
            total=total,
            seats=seats,
            entry=entry,
            zones=zones,
            # места без сектора — последней строкой
            sectors=sorted(sectors.values(), key=lambda option: (not option.sector, _natural_key(option.sector))),
            types=list(types.values()),
            areas=list(areas.values()),
            options=list(options.values()),
        )

    async def _session_data(self, session_id: int) -> dict:
        # Экран статистики обновляют сразу много контролёров, а разбивка сеанса —
        # тяжёлый запрос: держим её в памяти столько же, сколько счётчики.
        key = (session_id, "#statistic")
        data = counts_cache.get(key)
        if data is None:
            data = await self.ticket_repo.get_zone_breakdown(session_id)
            data["zones"] = await self.user_repo.get_session_scan_zones(session_id)
            counts_cache.put(key, data)
        return data

    @staticmethod
    def _named_zones(raw_zones: list[dict], account_zone: ScanZone | None) -> list[ZoneNamedOption]:
        """Зоны контролёров этого сеанса без повторов; своя зона — всегда в списке."""
        parsed = [ScanZone.parse(raw) for raw in raw_zones]
        if account_zone is not None:
            parsed.append(account_zone)

        unique: dict[tuple, ZoneNamedOption] = {}
        for zone in parsed:
            if zone is None:
                continue
            unique.setdefault((zone.title, zone.cache_key()), ZoneNamedOption(title=zone.title, zone=zone))
        return list(unique.values())
