import json
from typing import Literal


class EventMessage:
    def __init__(self, event_type: Literal["volume"], message: str) -> None:
        self.event_type = event_type
        self.message = message

    @property
    def json(self) -> str:
        return json.dumps(self.__dict__)
