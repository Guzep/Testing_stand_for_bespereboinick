"""Логика тестов стенда: ИБП с коммутацией и термомониторинг."""

from __future__ import annotations

import csv
import os
import time
from datetime import datetime
from typing import Callable, List, Optional, Tuple

from stand.config import (
    DEFAULT_UPS_PROFILE,
    RESULTS_DIR,
    SETTLE_TIME_S,
    STM_RESET_PINS,
    VOLTAGE_TOLERANCE_V,
)
from stand.devices import Multimeter, PowerUnit, STM32Switcher, Thermometer

LogFn = Callable[[str], None]


def _ensure_results_dir() -> str:
    os.makedirs(RESULTS_DIR, exist_ok=True)
    return RESULTS_DIR


def run_ups_contact_test(
    multimeter_port: str,
    power_port: str,
    stm_port: str,
    profile: Optional[List[Tuple[int, str, float]]] = None,
    log: Optional[LogFn] = None,
) -> bool:
    """
    Тест ИБП: STM32 коммутирует контакты, БП задаёт напряжение,
    мультиметр (или опрос БП) проверяет результат.

    profile: список (напряжение, команда_пинов, ожидаемое_напряжение).
    """
    profile = profile or DEFAULT_UPS_PROFILE
    log = log or print

    with (
        Multimeter(multimeter_port, 9600) as mu,
        PowerUnit(power_port, 115200) as psu,
        STM32Switcher(stm_port, 9600) as stm,
    ):
        log("Устройства подключены. Старт теста коммутации…")
        for i, (voltage, pins, expected) in enumerate(profile):
            log(f"Шаг {i + 1}/{len(profile)}: U={voltage} В, пины={pins!r}")
            stm.set_pins(pins)
            ok = psu.voltage_change(voltage, enable=True)
            if not ok:
                log(f"БП не вышел на {voltage} В")
                return False

            time.sleep(SETTLE_TIME_S)

            # Основная проверка — по реальному напряжению БП;
            # мультиметр держим открытым для расширенной схемы.
            status = psu.read_channel()
            measured = float(status["real_voltage"])
            try:
                mu_raw = mu.fetch()
                log(f"  Мультиметр: {mu_raw}")
            except Exception as exc:  # noqa: BLE001
                log(f"  Мультиметр: не удалось снять ({exc})")

            log(f"  БП real U={measured} В (ожидалось {expected} ± {VOLTAGE_TOLERANCE_V})")
            if abs(measured - expected) > VOLTAGE_TOLERANCE_V:
                log("Ошибка: напряжение вне допуска")
                stm.set_pins(STM_RESET_PINS)
                return False

            if i < len(profile) - 1:
                stm.set_pins(STM_RESET_PINS)

        log("Тест ИБП успешно завершён")
        return True


def run_thermal_logging(
    thermometer_port: str,
    power_port: str,
    duration_minutes: int,
    pause_minutes: int,
    log: Optional[LogFn] = None,
) -> str:
    """
    Длительный термомониторинг: периодически пишет U, I, t1, t2 в CSV.
    Возвращает путь к файлу результатов.
    """
    log = log or print
    _ensure_results_dir()
    stamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filepath = os.path.join(RESULTS_DIR, f"test_results_{stamp}.csv")

    total_seconds = duration_minutes * 60
    start = time.time()
    minute_counter = 0
    row_n = 1

    with open(filepath, "w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh, delimiter="\t")
        writer.writerow(["№", "T_мин", "U", "I", "t1", "t2", "U5_В", "U15_В"])

        while (time.time() - start) < total_seconds:
            with (
                PowerUnit(power_port, 115200) as psu,
                Thermometer(thermometer_port, 9600) as thermo,
            ):
                power = psu.read_channel()
                temps = thermo.temperature()
                t1 = temps[0] if len(temps) > 0 else ""
                t2 = temps[1] if len(temps) > 1 else ""
                u = float(power["real_voltage"])
                i = float(power["real_current"])

            writer.writerow([row_n, minute_counter, u, i, t1, t2, "", ""])
            fh.flush()
            log(f"Итерация №{row_n}  T={minute_counter} мин  U={u}  I={i}  t1={t1}  t2={t2}")

            row_n += 1
            minute_counter += pause_minutes
            time.sleep(pause_minutes * 60)

    log(f"Результаты сохранены: {filepath}")
    return filepath


def snapshot_thermal(
    thermometer_port: str,
    power_port: str,
    log: Optional[LogFn] = None,
) -> dict:
    """Однократный съём U/I/t1/t2."""
    log = log or print
    with (
        PowerUnit(power_port, 115200) as psu,
        Thermometer(thermometer_port, 9600) as thermo,
    ):
        power = psu.read_channel()
        temps = thermo.temperature()
    data = {
        "U": float(power["real_voltage"]),
        "I": float(power["real_current"]),
        "t1": temps[0] if temps else None,
        "t2": temps[1] if len(temps) > 1 else None,
    }
    log(f"Снимок: U={data['U']} I={data['I']} t1={data['t1']} t2={data['t2']}")
    return data
