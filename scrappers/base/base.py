import abc
import dataclasses
from typing import Optional, TypeVar, Generic
from bs4 import BeautifulSoup

_S = TypeVar("_S", bound=BeautifulSoup)

@dataclasses.dataclass
class SearchParams:
    ...


@dataclasses.dataclass
class Result:
    ...


class Scrapper(abc.ABC):

    @property
    @abc.abstractmethod
    def url(self):
        ...

    @property
    @abc.abstractmethod
    def param_initializer(self):
        ...

    @property
    @abc.abstractmethod
    def param_delimiter(self):
        ...

    def parse_url(self, search_params: SearchParams) -> str:
        data = dataclasses.asdict(search_params)
        params = ""
        for key, value in data.items():
            params += f"{key}={value}{self.param_delimiter}"
        search = f"{self.url}{self.param_initializer}{params}"
        return search

    @abc.abstractmethod
    def make_query(self, search_params: SearchParams) -> Optional[Generic[_S]]:
        ...

    @abc.abstractmethod
    def make_json_object(self, search_params: SearchParams) -> Optional[Generic[_S]]:
        ...

    @abc.abstractmethod
    def clean_result(self, scrapper_object: Generic[_S]) -> list[Result]:
        ...
