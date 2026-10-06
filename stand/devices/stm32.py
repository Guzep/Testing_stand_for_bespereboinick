"""Драйвер STM32: коммутация контактов на электросхеме стенда."""

from __future__ import annotations

from .base import SerialDevice


class STM32Switcher(SerialDevice):
    """
    Микроконтроллер управляет реле/контактами специальной схемы.

    Команда — строка состояния пинов (например '00000', '11111', '2').
    Конкретная кодировка задаётся прошивкой на STM32.
    """

    def set_pins(self, command: str) -> str:
        """Отправить команду коммутации контактов."""
        if self.serial_ is None or not self.serial_.is_open:
            raise RuntimeError(f"Порт {self.com_port} не открыт")
        self.serial_.write(command.encode())
        return self.serial_.readline().decode(errors="replace").strip()

    def idle(self) -> str:
        """Разомкнуть / сбросить контакты."""
        return self.set_pins("00000")

    def reset_all(self) -> str:
        """Установить все контакты в активное состояние (по прошивке)."""
        return self.set_pins("11111")

    def probe(self) -> bool:
        self.idle()
        return True
