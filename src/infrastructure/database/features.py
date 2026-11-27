"""Необязательные части общей базы.

Схему ведёт showgo_api, и у разных стран она разная: где-то ещё нет колонок
зон, где-то нет доп. опций сеанса или времени смены пароля. Сервис при старте
один раз смотрит, что есть в базе, и к отсутствующему не обращается.
"""
import logging

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncConnection

from src.core.config import settings

logger = logging.getLogger(__name__)

_COLUMNS = {
    "scan_zone": ("user_permissions", "scan_zone"),
    "scan_log_payload": ("scan_logs", "payload"),
    "password_changed_at": ("users", "password_changed_at"),
    "session_options": ("order_items", "session_option_id"),
}


class DbFeatures:
    # users.password_changed_at: вход, выданный до смены пароля, не действует.
    password_changed_at: bool = False
    # Доп. опции сеанса (Fast Track): order_items.session_option_id, session_options.
    session_options: bool = False


db_features = DbFeatures()


async def detect_db_features(connection: AsyncConnection) -> None:
    result = await connection.execute(text(
        "SELECT table_name, column_name FROM information_schema.columns "
        "WHERE table_schema = current_schema() "
        "AND table_name IN ('user_permissions', 'scan_logs', 'users', 'order_items')"
    ))
    existing = {tuple(row) for row in result}
    present = {name: column in existing for name, column in _COLUMNS.items()}

    db_features.password_changed_at = present["password_changed_at"]
    db_features.session_options = present["session_options"]

    # Выключатель включили, а колонок нет: любой запрос сканера падал бы.
    # Работаем как без зон из админки и пишем об этом в лог.
    if settings.scan_zone_columns and not (present["scan_zone"] and present["scan_log_payload"]):
        logger.error(
            "SCAN_ZONE_COLUMNS=true, но в базе нет user_permissions.scan_zone или scan_logs.payload: "
            "зоны из админки и причины отказов в журнале выключены"
        )
        settings.scan_zone_columns = False

    logger.info(
        "База: зоны из админки — %s, выход после смены пароля — %s, доп. опции сеанса — %s",
        settings.scan_zone_columns, db_features.password_changed_at, db_features.session_options,
    )
