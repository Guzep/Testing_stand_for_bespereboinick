"""Конфигурация стенда и профили тестов."""

from dataclasses import dataclass, field
from typing import List, Tuple


@dataclass(frozen=True)
class DeviceSpec:
    """Описание устройства на стенде."""

    key: str
    title: str
    baud_rate: int
    required: bool = True


# Три основных устройства для теста ИБП с переключением контактов.
# AT4508 (термометр) — опционально, для длительного термомониторинга.
DEVICES: List[DeviceSpec] = [
    DeviceSpec("multimeter", "Мультиметр TH1951", 9600),
    DeviceSpec("power_unit", "Блок питания ODP3032", 115200),
    DeviceSpec("stm32", "Микроконтроллер STM32 (коммутация)", 9600),
    DeviceSpec("thermometer", "Термометр AT4508", 9600, required=False),
]

# Профиль теста ИБП: (напряжение БП, команда пинов STM32, ожидаемое напряжение).
# Команда пинов — строка для схемы коммутации контактов.
DEFAULT_UPS_PROFILE: List[Tuple[int, str, float]] = [
    (7, "2", 7.0),
    (10, "2", 10.0),
    (15, "2", 15.0),
    (20, "2", 20.0),
    (30, "2", 30.0),
]

# Команда «все контакты разомкнуты / сброс» для STM32.
STM_IDLE_PINS = "00000"
STM_RESET_PINS = "11111"

# Допуск при сравнении измеренного и ожидаемого напряжения (В).
VOLTAGE_TOLERANCE_V = 0.5

# Пауза после коммутации / смены напряжения (с).
SETTLE_TIME_S = 1.0

# Каталог для файлов результатов.
RESULTS_DIR = "results"
