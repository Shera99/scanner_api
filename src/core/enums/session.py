from enum import Enum


class SessionStatusEnum(str, Enum):
    active = "ACTIVE"
    active_web = "ACTIVE_WEB"
    active_cabinet = "ACTIVE_CABINET"
    active_url = "ACTIVE_URL"
    inactive = "INACTIVE"
    cancelled = "CANCELLED"


class SvgTypeEnum(str, Enum):
    our_system = "OUR_SYSTEM"
    esbo = "ESBO"
