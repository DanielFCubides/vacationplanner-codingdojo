from abc import ABC, abstractmethod
from typing import Tuple, Union


class FlightsRepository(ABC):
    
    @abstractmethod
    def get(
        self, 
        *, 
        id_fly: int, 
        **kwargs
    ) -> Tuple[dict | list, int]:
        """
        Obtain a flight with all information
        """
        pass

