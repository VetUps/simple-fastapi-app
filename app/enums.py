import enum

class UserRole(enum.Enum):
    ADIM = "admin"
    USER = "user"

class RevokeReason(enum.Enum):
    ROTATED = "rotated"
    USER_LOGOUT = "user_logout"
    FORCE_LOGOUT = "force_logout"