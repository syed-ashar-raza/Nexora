from app.providers.base import Provider, ProviderUnavailable


class Router:
    def __init__(
        self,
        providers: list[Provider],
        policy: str = "health_aware",
    ) -> None:
        self.providers = providers
        self.policy = policy
        self._round_robin_index = 0

    def choose(self, requested_model: str, healthy: set[str]) -> Provider:
        matching = [
            provider
            for provider in self.providers
            if requested_model in provider.models
        ]

        if matching:
            available = [
                provider
                for provider in matching
                if provider.name in healthy
            ]

            if not available:
                raise ProviderUnavailable(
                    f"Requested model '{requested_model}' is unavailable"
                )

            return self._select(available)

        available = [
            provider
            for provider in self.providers
            if provider.name in healthy
        ]

        if not available:
            raise ProviderUnavailable("No healthy provider available")

        return self._select(available)

    def _select(self, providers: list[Provider]) -> Provider:
        if self.policy == "round_robin":
            provider = providers[self._round_robin_index % len(providers)]
            self._round_robin_index += 1
            return provider

        if self.policy == "cost":
            return min(providers, key=lambda provider: getattr(provider, "cost", 0.0))

        return providers[0]
