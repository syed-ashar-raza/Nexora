from app.providers.base import Provider


class Router:
    def __init__(self, providers: list[Provider]) -> None:
        self.providers = providers

    def choose(self, requested_model: str, healthy: set[str]) -> Provider:
        for provider in self.providers:
            if requested_model in provider.models and provider.name in healthy:
                return provider
        for provider in self.providers:
            if provider.name in healthy:
                return provider
        raise RuntimeError("no healthy provider available")
