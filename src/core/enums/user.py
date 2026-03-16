from enum import Enum


class UserPermissionRoleEnum(str, Enum):
    super_admin = "SUPER_ADMIN"
    admin = "ADMIN"
    manager = "MANAGER"
    accountant = "ACCOUNTANT"
    organizer = "ORGANIZER"
    cashier = "CASHIER"
    controller = "CONTROLLER"
    partner = "PARTNER"
    super_cashier = "SUPER_CASHIER"
    artist = "ARTIST"


class GenderEnum(str, Enum):
    male = "MALE"
    female = "FEMALE"
