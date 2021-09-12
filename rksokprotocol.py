from enum import Enum
from typing import ClassVar

_PROTOCOL = "РКСОК/1.0"
_ENCODING = "UTF-8"
_SEPARATOR = "\r\n"
_ENDING = "\r\n\r\n"

class RequestVerb(Enum):
    """Verbs specified in RKSOK specs for requests"""
    GET = "ОТДОВАЙ"
    DELETE = "УДОЛИ"
    WRITE = "ЗОПИШИ"
    CAN = "АМОЖНА?"


class ResponseStatus(Enum):
    """Response statuses specified in RKSOK specs for responses"""
    OK = "НОРМАЛДЫКС"
    NOTFOUND = "НИНАШОЛ"
    NOT_APPROVED = "НИЛЬЗЯ"
    INCORRECT_REQUEST = "НИПОНЯЛ"
    APPROVED = "МОЖНА"


class RKSOKCommand:
    """
    This class describe RKSOK command.
    Also he allow to represent RKSOK command in string format and make RKSOK command from str.
    """

    _allow_commands = {
        **RequestVerb._value2member_map_,
        **ResponseStatus._value2member_map_
        }

    _allow_commands_with_value = (
        RequestVerb.WRITE.value,
        ResponseStatus.OK.value,
        RequestVerb.CAN.value,
        ResponseStatus.NOT_APPROVED.value
        )

    def __init__(self, command: str, key: str = None, value: str = None) -> None:
        """
        Init RKSOKCommand parameters.

        Parameters:
        command (str) - command for RKSOKcommand (for example: "ОТДОВАЙ", "УДОЛИ")
        key (str = None) - key for RKSOKcommand (for example: "Иван Хмурый")
        value (str = None) = value for RKSOKCommand (for Example: "89218881111\r\n8-800-555-35-35")
        """
        self._prop_key = None
        self._prop_command = None
        self._prop_value = None
        self._command = command
        self._key = key
        self._value = value

    @property
    def _key(self):
        return self._prop_key

    @_key.setter
    def _key(self, value: str):
        if value is not None and len(value) > 30:
            raise ValueError("Key to long.")
        self._prop_key = value

    @property
    def _command(self):
        return self._prop_command

    @_command.setter
    def _command(self, value: str):
        if value not in self._allow_commands:
            raise ValueError("Unacceptable command.")
        self._prop_command = value

    @property
    def _value(self):
        return self._prop_value

    @_value.setter
    def _value(self, value):
        if value is not None and self._command not in self._allow_commands_with_value:
            raise ValueError(f"Command {self._command} does not support values.")
        self._prop_value = value

    def __str__(self) -> str:
        if self._key and self._value:
            return f"{self._command} {self._key} {_PROTOCOL}{_SEPARATOR}{self._value}{_ENDING}"
        if not self._key and not self._value:
            return f"{self._command} {_PROTOCOL}{_ENDING}"
        if not self._key:
            return f"{self._command} {_PROTOCOL}{_SEPARATOR}{self._value}{_ENDING}"
        if not self._value:
            return f"{self._command} {self._key} {_PROTOCOL}{_ENDING}"

    def command(self):
        return self._command
    
    def key(self):
        return self._key
    
    def value(self):
        return self._value

    @classmethod
    def rksokcommand_from_str(cls, command: str) -> object:
        """
        Parse command and create RKSOKcommand object.
        If string command is wrong, this method returned Incorrect RKSOKcommand.

        Parameters:
        command (str) - rksok command in str format (for example: ЗОПИШИ Иван Хмурый РКСОК/1.0\r\n89012345678 — мобильный\r\n02 — рабочий\r\n\r\n)

        Returns:
        (RKSOKCommand)
        """
        try:
            command_line, *values = command.strip().split(_SEPARATOR)
            command, *key, protocol = command_line.strip().split()
            
            if protocol != _PROTOCOL:
                raise ValueError('Incorrect protocol')

            result_key = " ".join(key) if key else None
            result_value = _SEPARATOR.join(values) if values else None

            return cls(command, result_key, result_value)
        except ValueError:
            return cls(ResponseStatus.INCORRECT_REQUEST.value)


if __name__ == "__main__":
    pass