"""Базовый класс последовательного устройства."""

from __future__ import annotations

import serial


class SerialDevice:
    """Обёртка над pyserial с context manager и единым API закрытия."""

    def __init__(self, com_port: str, baud_rate: int, timeout: float = 0.5):
        self.com_port = com_port
        self.baud_rate = baud_rate
        self.timeout = timeout
        self.serial_: serial.Serial | None = None
        self.connect()

    def connect(self) -> None:
        try:
            self.serial_ = serial.Serial(
                self.com_port,
                self.baud_rate,
                timeout=self.timeout,
            )
        except serial.SerialException as exc:
            raise serial.SerialException(
                f"Ошибка подключения к {self.com_port}: {exc}"
            ) from exc

    def send_command(self, command: str, append_newline: bool = True) -> str:
        if self.serial_ is None or not self.serial_.is_open:
            raise serial.SerialException(f"Порт {self.com_port} не открыт")
        payload = (command + "\n") if append_newline else command
        self.serial_.write(payload.encode())
        return self.serial_.readline().decode(errors="replace").strip()

    def close(self) -> None:
        if self.serial_ is not None and self.serial_.is_open:
            self.serial_.close()
        self.serial_ = None

    def __enter__(self) -> SerialDevice:
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()

    def __del__(self) -> None:
        try:
            self.close()
        except Exception:
            pass
