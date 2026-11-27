from enum import Enum

from src.core.enums.order import OrderStatusEnum, ORDER_REJECT_REASONS


class ScanTypeEnum(str, Enum):
    in_ = "IN"
    out = "OUT"
    in_error = "IN_ERROR"
    out_error = "OUT_ERROR"


SCAN_LOG_TYPE = {1: ScanTypeEnum.in_, 0: ScanTypeEnum.out}

# Любая попытка, которая не закончилась проходом: повторный вход или выход,
# чужое мероприятие, возврат, отменённый заказ, другая зона. Причина отказа
# лежит в scan_logs.payload["result"].
ERROR_SCAN_LOG_TYPE = {1: ScanTypeEnum.in_error, 0: ScanTypeEnum.out_error}


class ScanResultEnum(str, Enum):
    """Исход скана, пишется в scan_logs.payload["result"]."""
    allowed = "allowed"
    already_used = "already_used"
    wrong_zone = "wrong_zone"
    wrong_event = "wrong_event"
    ticket_refund = "ticket_refund"
    order_cancelled = "order_cancelled"
    order_refund = "order_refund"
    order_failed = "order_failed"


ORDER_REJECT_RESULTS = {
    OrderStatusEnum.cancelled: ScanResultEnum.order_cancelled,
    OrderStatusEnum.refund: ScanResultEnum.order_refund,
    OrderStatusEnum.failed: ScanResultEnum.order_failed,
}

# Подписи записей журнала для экрана сканера.
_TYPE_MESSAGES = {
    ScanTypeEnum.in_: "Вход",
    ScanTypeEnum.out: "Выход",
    ScanTypeEnum.in_error: "Повторный вход",
    ScanTypeEnum.out_error: "Повторный выход",
}

_REJECT_MESSAGES = {
    ScanResultEnum.wrong_zone.value: "Другая зона",
    ScanResultEnum.wrong_event.value: "Другое мероприятие",
    ScanResultEnum.ticket_refund.value: "Билет отменен (возврат)",
    **{ORDER_REJECT_RESULTS[status].value: reason for status, reason in ORDER_REJECT_REASONS.items()},
}


def scan_log_result(type_scan: ScanTypeEnum, payload: dict | None) -> str:
    """Исход записи журнала. У записей без payload (старые или сделанные до
    появления колонки) он однозначно следует из типа."""
    if payload and payload.get("result"):
        return str(payload["result"])
    if type_scan in (ScanTypeEnum.in_, ScanTypeEnum.out):
        return ScanResultEnum.allowed.value
    return ScanResultEnum.already_used.value


def scan_log_message(type_scan: ScanTypeEnum, result: str) -> str:
    if result in (ScanResultEnum.allowed.value, ScanResultEnum.already_used.value):
        return _TYPE_MESSAGES[type_scan]
    return _REJECT_MESSAGES.get(result, result)
