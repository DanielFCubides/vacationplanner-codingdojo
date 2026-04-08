from hashlib import sha256

from domain.models import SearchParams


def create_search_params_hash(search_params: SearchParams) -> str:
    params_string = (f"{search_params.origin}|{search_params.destination}|"
                     f"{search_params.departure}|{search_params.return_date}|"
                     f"{search_params.passengers}|")
    params_hash = sha256(params_string.encode()).hexdigest()
    return params_hash
