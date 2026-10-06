"""Драйвер мультиметра TH1951 (SCPI через COM)."""

from __future__ import annotations

import time

from .base import SerialDevice


class Multimeter(SerialDevice):
    """Управление мультиметром TH1951."""

    def send_command(self, command: str, append_newline: bool = True) -> str:
        if self.serial_ is None or not self.serial_.is_open:
            raise RuntimeError(f"Порт {self.com_port} не открыт")
        payload = (command + "\n") if append_newline else command
        self.serial_.write(payload.encode("ascii"))
        time.sleep(0.02)
        return self.serial_.readline().strip().decode("ascii", errors="replace")

    def fetch(self) -> str:
        """Текущее измерение (:FETC?)."""
        return self.send_command(":FETC?")

    def mode_ac_current(self) -> str:
        return self.send_command(":FUNC CURR:AC")

    def mode_resistance(self) -> str:
        return self.send_command(":FUNC RES")

    def trigger_bus(self) -> str:
        return self.send_command(":trig:sour bus;*trg")

    def probe(self) -> bool:
        """Проверка связи: запрос измерения не должен ронять порт."""
        self.fetch()
        return True
