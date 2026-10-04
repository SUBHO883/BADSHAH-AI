from backend.ai.ollama_client import OllamaClient
from backend.scanners.wifi_scanner import (
    discover_wifi_networks,
)


def test_ollama_client_creation():

    client = OllamaClient()

    assert client.base_url
    assert client.model


def test_wifi_function_exists():

    assert callable(
        discover_wifi_networks
    )