class FlightsSearch:

    def __init__(
            self,
            repository
        ) -> None:
        self.repository = repository

    def search(self, *, id_fly: int) -> dict:
        fly = self.repository.get(
            id_fly=id_fly
        )

        # TODO: Add a validation that review if there is a fly
        return fly