from enum import Enum
import os

SEARCH_RETRIES = int(os.getenv("SEARCH_RETRIES", "3"))

class StrEnum(str, Enum):
    DEFAULT = ""

    @classmethod
    def _missing_(cls, value):
        return cls.DEFAULT


class QueryParamInitializer(StrEnum):
    DEFAULT = "?"
    OPTION_1 = "search?_query="


# https://www.rfc-editor.org/rfc/rfc3986#section-2.2
class QueryParamDelimiter(StrEnum):
    DEFAULT = "+"
    OPTION_1 = "&"

