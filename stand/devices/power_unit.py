"""Драйвер блока питания ODP3032."""

from __future__ import annotations

from .base import SerialDevice


class PowerUnit(SerialDevice):
    """Программируемый БП ODP3032: напряжение, ток, режимы, вкл/выкл."""

    VOLTAGE_OFFSET_MAP = {
        range(0, 10): 706,
        range(10, 20): 755,
        range(20, 30): 756,
        range(30, 40): 757,
        range(40, 50): 758,
        range(50, 60): 759,
        range(60, 62): 760,
    }
    CURRENT_OFFSET_MAP = {
        range(0, 1): 687,
        range(1, 3): 688,
        range(2, 4): 689,
    }
    MODE_COMMANDS = {
        0: "&COMMON,PARALLEL,1134",
        1: "&COMMON,SERIES,1004",
        2: "&COMMON,DOUBLE,988",
    }
    SWITCH_COMMANDS = {
        True: "&SW1,0,355",
        False: "&SW1,1,356",
    }

    def _calculate_offset(self, value: int, offset_map: dict) -> int:
        for range_, offset_base in offset_map.items():
            if value in range_:
                return offset_base + value - range_.start
        raise ValueError(f"Нет offset для значения {value}")

    def voltage_change(self, voltage: int, enable: bool = True) -> bool:
        """Установить напряжение 0–60 В. При enable=True включает выход."""
        if not 0 <= voltage <= 60:
            raise ValueError("Напряжение должно быть от 0 до 60 В")
        offset = self._calculate_offset(voltage, self.VOLTAGE_OFFSET_MAP)

        if enable:
            self.switching_on_off(True)
            self.send_command(f"&SSERIV,{voltage}.0,{offset}")
            for _ in range(15):
                status = self.decode_response(self.status_poll())
                if int(float(status["real_voltage"])) == voltage:
                    return True
            return False

        self.switching_on_off(False)
        self.send_command(f"&SSERIV,{voltage}.0,{offset}")
        return True

    def current_change(self, current: int) -> dict:
        """Установить ток 0–3 А."""
        if not 0 <= current <= 3:
            raise ValueError("Ток должен быть от 0 до 3 А")
        offset = self._calculate_offset(current, self.CURRENT_OFFSET_MAP)
        return self.decode_response(self.send_command(f"&SSERIC,{current}.0,{offset}"))

    def mode_change(self, mode: int) -> str:
        """mode: 0 — PARALLEL, 1 — SERIES, 2 — DOUBLE."""
        if mode not in self.MODE_COMMANDS:
            raise ValueError("Неизвестный режим")
        return self.send_command(self.MODE_COMMANDS[mode])

    def switching_on_off(self, switch: bool = True) -> str:
        return self.send_command(self.SWITCH_COMMANDS[switch])

    def decode_response(self, data: str, channel: int = 1) -> dict:
        parts = data.split(",")
        if len(parts) < 9:
            raise ValueError(f"Некорректный ответ БП: {data!r}")
        return {
            "set_voltage": parts[5],
            "set_current": parts[6],
            "real_voltage": parts[7],
            "real_current": parts[8],
            "channel": channel,
        }

    def status_poll(self) -> str:
        return self.send_command("&SYNCHRO,0,686")

    def probe(self) -> bool:
        self.status_poll()
        return True

    def read_channel(self, channel: int = 1) -> dict:
        return self.decode_response(self.status_poll(), channel=channel)
