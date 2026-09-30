import enum

class UserRole(enum.Enum):
    ADIM = "admin"
    USER = "user"

class RevokeReason(enum.Enum):
    ROTATED = "ROTATED"
    USER_LOGOUT = "USER_LOGOUT"
    FORCE_LOGOUT = "FORCE_LOGOUT"