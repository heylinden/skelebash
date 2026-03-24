from __future__ import annotations
class Keyset:
    ZXCVBN: str = "zxcvbn"
    DIGITS: str = "123456"
    QWERTY: str = "qwerty"
    QUERTZ: str = "qwertz"
    AZERTY: str = "azerty"
    WASDFG: str = "wasdfg"
    DIGIT0: str = "012345"
    ZXCVGH: str = "zxcvgh"
class KeysetError(Exception):
    pass