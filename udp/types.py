from enum import Enum

class DATA_TYPES(Enum):
    IMAGE   =  0
    BOOLEAN = -1
    INTEGER = -2
    FLOAT   = -3
    STRING  = -4


class BROADCAST_MODE(Enum):
    """Mod slanja podataka"""
    BROADCAST = "broadcast"  # Pošalji svima na mreži
    UNICAST = "unicast"      # Pošalji samo specifičnim IP adresama