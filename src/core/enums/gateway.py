from enum import Enum


class GatewayTypeEnum(str, Enum):
    payme = "PAYME"
    click = "CLICK"
    uzum = "UZUM"
