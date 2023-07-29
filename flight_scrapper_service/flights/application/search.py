from abc import ABC, abstractmethod
from typing import Union


class FlightsRepository(ABC):
    
    @abstractmethod
    def get(
        self, 
        *, 
        id_fly: int, 
        **kwargs
    ) -> Union[(dict, list), int]:
        """
        Obtain a flight with all information
        """
        pass

