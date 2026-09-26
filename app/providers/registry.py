from app.providers.base import Provider
from app.providers.mock import MockProvider


class ProviderRegistry:
    def __init__(self) -> None:
        self._providers: dict[str, Provider] = {
            "nexora-mock": MockProvider("nexora-mock", cost=1.0),
            "mock-429": MockProvider("mock-429", cost=0.5),
            "mock-500": MockProvider("mock-500", cost=0.8),
            "mock-slow": MockProvider("mock-slow", cost=1.5),
        }

    def get(self, model: str) -> Provider:
        return self._providers.get(model, self._providers["nexora-mock"])

    def all(self) -> list[Provider]:
        return list(self._providers.values())
