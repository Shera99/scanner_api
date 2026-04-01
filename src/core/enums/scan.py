from enum import Enum


class ScanTypeEnum(str, Enum):
    in_ = "IN"
    out = "OUT"
    in_error = "IN_ERROR"
    out_error = "OUT_ERROR"


SCAN_LOG_TYPE = {1: ScanTypeEnum.in_, 0: ScanTypeEnum.out}

# Повторный вход при уже отмеченном входе / повторный выход при уже отмеченном выходе
ERROR_SCAN_LOG_TYPE = {1: ScanTypeEnum.in_error, 0: ScanTypeEnum.out_error}
