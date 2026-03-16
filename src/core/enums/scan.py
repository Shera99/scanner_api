from enum import Enum


class ScanTypeEnum(str, Enum):
    in_ = "IN"
    out = "OUT"


SCAN_LOG_TYPE = {1: ScanTypeEnum.in_, 0: ScanTypeEnum.out}
