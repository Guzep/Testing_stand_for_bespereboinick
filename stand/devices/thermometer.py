"""Драйвер термометра AT4508 (Applent / Anbai)."""

from __future__ import annotations

from .base import SerialDevice


class Thermometer(SerialDevice):
    """Многоканальный термометр AT4508."""

    EXPECTED_IDN_PREFIX = "AT4508"

    def identify(self) -> str:
        return self.send_command("IDN?")

    def check(self) -> bool:
        response = self.identify()
        return response.startswith(self.EXPECTED_IDN_PREFIX)

    def temperature(self) -> list[float]:
        """Список температур по каналам (°C), округление до 0.01."""
        response = self.send_command("fetch?")
        numbers = [float(x) for x in response.split(",") if x]
        return [round(num, 2) for num in numbers]

    def probe(self) -> bool:
        return self.check()
