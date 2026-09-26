import pytest

from app.providers.base import ProviderUnavailable
from app.providers.mock import MockProvider
from app.routing.policy import Router


def test_health_aware_selects_first_healthy_provider():
    providers = [
        MockProvider("provider-a", cost=2.0),
        MockProvider("provider-b", cost=1.0),
    ]

    router = Router(providers, "health_aware")

    assert router.choose("unknown", {"provider-a", "provider-b"}).name == "provider-a"


def test_cost_selects_lowest_cost_provider():
    providers = [
        MockProvider("provider-a", cost=2.0),
        MockProvider("provider-b", cost=1.0),
    ]

    router = Router(providers, "cost")

    assert router.choose("unknown", {"provider-a", "provider-b"}).name == "provider-b"


def test_round_robin_rotates_providers():
    providers = [
        MockProvider("provider-a"),
        MockProvider("provider-b"),
    ]

    router = Router(providers, "round_robin")

    healthy = {"provider-a", "provider-b"}

    assert router.choose("unknown", healthy).name == "provider-a"
    assert router.choose("unknown", healthy).name == "provider-b"
    assert router.choose("unknown", healthy).name == "provider-a"


def test_requested_model_takes_precedence():
    providers = [
        MockProvider("provider-a"),
        MockProvider("provider-b"),
    ]

    router = Router(providers, "cost")

    assert router.choose("provider-b", {"provider-a", "provider-b"}).name == "provider-b"


def test_unavailable_requested_model_does_not_fallback():
    providers = [
        MockProvider("provider-a"),
        MockProvider("provider-b"),
    ]

    router = Router(providers, "health_aware")

    with pytest.raises(ProviderUnavailable):
        router.choose("provider-a", {"provider-b"})
