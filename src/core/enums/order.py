from enum import Enum


class OrderStatusEnum(str, Enum):
    booked = "BOOKED"
    sales_booked = "SALES_BOOKED"
    pending_for_payment = "PENDING_FOR_PAYMENT"
    completed = "COMPLETED"
    failed = "FAILED"
    refund = "REFUND"
    cancelled = "CANCELLED"
    invitation = "INVITATION"


ORDER_REJECT_REASONS = {
    OrderStatusEnum.cancelled: "Заказ отменен",
    OrderStatusEnum.refund: "Заказ возвращен",
    OrderStatusEnum.failed: "Ошибка оплаты",
}


class PaymentMethodEnum(str, Enum):
    cash = "CASH"
    card = "CARD"
    bank_transfer = "BANK_TRANSFER"
    invitation = "INVITATION"
    terminal = "TERMINAL"
