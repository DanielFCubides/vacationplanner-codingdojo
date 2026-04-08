from typing import Any
from urllib.parse import urlencode, urlparse, parse_qs

from typing_extensions import Self

DEFAULT_URL_SCHEMA = 'https'


class DynamicURL(str):

    def __new__(cls, scheme, netloc, path, **query_params):
        query_string = f"?{urlencode(query_params)}" if query_params else ""
        url = f"{scheme}://{netloc}{path}{query_string}"
        obj = str.__new__(cls, url)
        obj.scheme = scheme
        obj.netloc = netloc
        obj.path = path
        obj.query_params = query_params
        return obj

    def __str__(self):
        query_string = urlencode(self.query_params)
        return f"{self.scheme}://{self.netloc}{self.path}?{query_string}"

    def __repr__(self):
        query_string = urlencode(self.query_params)
        return f"{self.scheme}://{self.netloc}{self.path}?{query_string}"

    @classmethod
    def from_url(cls, url) -> Self:
        from urllib.parse import urlparse, parse_qs

        parsed_url = urlparse(url)
        query_params = {k: v[0] for k, v in parse_qs(parsed_url.query).items()}
        return cls(parsed_url.scheme, parsed_url.netloc, parsed_url.path, **query_params)

    def set_query_param(self, key, value):
        self.query_params[key] = value

    def set_query_params(self, params: dict[str, Any]):
        self.query_params.update(params)

    @property
    def get_query_params(self):
        parsed_url = urlparse(str(self))
        query_params = {
            k: v[0]
            if len(v) == 1 else v
            for k, v in parse_qs(parsed_url.query).items()
        }
        return query_params

    def get_query_param(self, key):
        return self.query_params.get(key)
