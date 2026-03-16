from enum import Enum


class OrganizationTypeEnum(str, Enum):
    individual = "INDIVIDUAL"
    legal = "LEGAL"


class ServiceFeeTypeEnum(str, Enum):
    fixed = "FIXED"
    percent = "PERCENT"
