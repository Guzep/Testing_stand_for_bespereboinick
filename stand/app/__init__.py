"""GUI тестового стенда."""

from __future__ import annotations

import threading
import tkinter as tk
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText
from typing import Dict

from serial.tools import list_ports

from stand.config import DEVICES
from stand.devices import Multimeter, PowerUnit, STM32Switcher, Thermometer
from stand.tester import run_thermal_logging, run_ups_contact_test, snapshot_thermal


DEVICE_FACTORY = {
    "multimeter": lambda port, baud: Multimeter(port, baud),
    "power_unit": lambda port, baud: PowerUnit(port, baud),
    "stm32": lambda port, baud: STM32Switcher(port, baud),
    "thermometer": lambda port, baud: Thermometer(port, baud),
}


class TestStandApp:
    def __init__(self, master: tk.Tk):
        self.master = master
        self.master.title("Стенд теста ИБП v1.1")
        self.master.geometry("1100x560")
        self.master.minsize(900, 480)

        self.port_vars: Dict[str, tk.StringVar] = {}
        self.port_combos: Dict[str, ttk.Combobox] = {}
        self.lamps: Dict[str, tk.Canvas] = {}

        self._build_ui()
        self.refresh_ports()

    def _build_ui(self) -> None:
        self.master.columnconfigure(0, weight=3)
        self.master.columnconfigure(1, weight=2)
        self.master.rowconfigure(0, weight=1)

        left = ttk.Frame(self.master, padding=8)
        left.grid(row=0, column=0, sticky="nsew")
        left.rowconfigure(0, weight=1)
        left.columnconfigure(0, weight=1)

        self.log_text = ScrolledText(left, bg="#111", fg="#e8e8e8", insertbackground="white")
        self.log_text.grid(row=0, column=0, sticky="nsew")

        right = ttk.Frame(self.master, padding=12)
        right.grid(row=0, column=1, sticky="nsew")

        ttk.Label(right, text="Устройства и COM-порты", font=("", 11, "bold")).grid(
            row=0, column=0, columnspan=3, sticky="w", pady=(0, 8)
        )

        for row, spec in enumerate(DEVICES, start=1):
            ttk.Label(right, text=spec.title).grid(row=row, column=0, sticky="w", pady=4)
            var = tk.StringVar(value="")
            self.port_vars[spec.key] = var
            combo = ttk.Combobox(right, textvariable=var, width=18, state="readonly")
            combo.grid(row=row, column=1, sticky="ew", padx=6, pady=4)
            self.port_combos[spec.key] = combo
            lamp = tk.Canvas(right, width=18, height=18, highlightthickness=1, highlightbackground="#888")
            lamp.grid(row=row, column=2, padx=4)
            lamp.create_oval(2, 2, 16, 16, fill="#ccc", outline="")
            self.lamps[spec.key] = lamp

        btn_row = len(DEVICES) + 1
        ttk.Button(right, text="Обновить порты", command=self.refresh_ports).grid(
            row=btn_row, column=0, sticky="ew", pady=6
        )
        ttk.Button(right, text="Проверить связь", command=self.check_connections).grid(
            row=btn_row, column=1, columnspan=2, sticky="ew", pady=6
        )

        ttk.Separator(right).grid(row=btn_row + 1, column=0, columnspan=3, sticky="ew", pady=10)

        ttk.Label(right, text="Тест ИБП (коммутация контактов)", font=("", 10, "bold")).grid(
            row=btn_row + 2, column=0, columnspan=3, sticky="w"
        )
        ttk.Button(right, text="Старт теста ИБП", command=self.start_ups_test).grid(
            row=btn_row + 3, column=0, columnspan=3, sticky="ew", pady=6
        )

        ttk.Separator(right).grid(row=btn_row + 4, column=0, columnspan=3, sticky="ew", pady=10)

        ttk.Label(right, text="Термомониторинг (AT4508 + БП)", font=("", 10, "bold")).grid(
            row=btn_row + 5, column=0, columnspan=3, sticky="w"
        )
        ttk.Button(right, text="Снять сейчас", command=self.snapshot_now).grid(
            row=btn_row + 6, column=0, columnspan=3, sticky="ew", pady=4
        )
        ttk.Button(right, text="Запуск по времени…", command=self.open_duration_dialog).grid(
            row=btn_row + 7, column=0, columnspan=3, sticky="ew", pady=4
        )

        self.status_var = tk.StringVar(value="Готов")
        ttk.Label(right, textvariable=self.status_var).grid(
            row=btn_row + 8, column=0, columnspan=3, sticky="w", pady=(16, 0)
        )

    def log(self, message: str) -> None:
        def _append() -> None:
            self.log_text.insert(tk.END, message + "\n")
            self.log_text.see(tk.END)

        self.master.after(0, _append)

    def set_status(self, text: str) -> None:
        self.master.after(0, lambda: self.status_var.set(text))

    def set_lamp(self, key: str, ok: bool) -> None:
        color = "#2ecc71" if ok else "#e74c3c"

        def _paint() -> None:
            canvas = self.lamps[key]
            canvas.delete("all")
            canvas.create_oval(2, 2, 16, 16, fill=color, outline="")

        self.master.after(0, _paint)

    def refresh_ports(self) -> None:
        ports = [p.device for p in list_ports.comports()]
        values = ports or [""]
        for combo in self.port_combos.values():
            combo["values"] = values

        # Разным устройствам — разные порты; при нехватке не падаем.
        for i, spec in enumerate(DEVICES):
            if i < len(ports):
                self.port_vars[spec.key].set(ports[i])
            else:
                self.port_vars[spec.key].set("")
        self.log(
            f"Найдено COM-портов: {len(ports)}"
            + (f" → {', '.join(ports)}" if ports else "")
        )

    def _port(self, key: str) -> str:
        return self.port_vars[key].get().strip()

    def check_connections(self) -> None:
        def worker() -> None:
            self.set_status("Проверка…")
            for spec in DEVICES:
                port = self._port(spec.key)
                if not port:
                    if spec.required:
                        self.log(f"{spec.title}: порт не выбран")
                        self.set_lamp(spec.key, False)
                    else:
                        self.log(f"{spec.title}: пропуск (опционально, порт не выбран)")
                    continue
                try:
                    device = DEVICE_FACTORY[spec.key](port, spec.baud_rate)
                    try:
                        device.probe()
                        self.set_lamp(spec.key, True)
                        self.log(f"{spec.title} @ {port}: OK")
                    finally:
                        device.close()
                except Exception as exc:  # noqa: BLE001
                    self.set_lamp(spec.key, False)
                    self.log(f"{spec.title} @ {port}: ошибка — {exc}")
            self.set_status("Готов")

        threading.Thread(target=worker, daemon=True).start()

    def start_ups_test(self) -> None:
        mu = self._port("multimeter")
        psu = self._port("power_unit")
        stm = self._port("stm32")
        if not all([mu, psu, stm]):
            self.log("Для теста ИБП нужны порты: TH1951, ODP3032, STM32")
            return

        def worker() -> None:
            self.set_status("Тест ИБП…")
            try:
                ok = run_ups_contact_test(mu, psu, stm, log=self.log)
                self.set_status("Успех" if ok else "Ошибка теста")
            except Exception as exc:  # noqa: BLE001
                self.log(f"Сбой теста ИБП: {exc}")
                self.set_status("Ошибка")

        threading.Thread(target=worker, daemon=True).start()

    def snapshot_now(self) -> None:
        thermo = self._port("thermometer")
        psu = self._port("power_unit")
        if not thermo or not psu:
            self.log("Нужны порты AT4508 и ODP3032")
            return

        def worker() -> None:
            try:
                snapshot_thermal(thermo, psu, log=self.log)
            except Exception as exc:  # noqa: BLE001
                self.log(f"Ошибка снимка: {exc}")

        threading.Thread(target=worker, daemon=True).start()

    def open_duration_dialog(self) -> None:
        win = tk.Toplevel(self.master)
        win.title("Термомониторинг")
        win.resizable(False, False)

        ttk.Label(win, text="Длительность, мин:").grid(row=0, column=0, padx=8, pady=6, sticky="w")
        duration_var = tk.StringVar(value="60")
        ttk.Entry(win, textvariable=duration_var, width=10).grid(row=0, column=1, padx=8, pady=6)

        ttk.Label(win, text="Пауза между съёмами, мин:").grid(row=1, column=0, padx=8, pady=6, sticky="w")
        pause_var = tk.StringVar(value="1")
        ttk.Entry(win, textvariable=pause_var, width=10).grid(row=1, column=1, padx=8, pady=6)

        def on_start() -> None:
            thermo = self._port("thermometer")
            psu = self._port("power_unit")
            if not thermo or not psu:
                self.log("Нужны порты AT4508 и ODP3032")
                return
            try:
                duration = int(duration_var.get())
                pause = int(pause_var.get())
            except ValueError:
                self.log("Введите целые числа для времени")
                return
            win.destroy()

            def worker() -> None:
                self.set_status("Термомониторинг…")
                try:
                    run_thermal_logging(thermo, psu, duration, pause, log=self.log)
                    self.set_status("Готов")
                except Exception as exc:  # noqa: BLE001
                    self.log(f"Ошибка мониторинга: {exc}")
                    self.set_status("Ошибка")

            threading.Thread(target=worker, daemon=True).start()

        ttk.Button(win, text="Запустить", command=on_start).grid(
            row=2, column=0, columnspan=2, pady=10
        )


def run_app() -> None:
    root = tk.Tk()
    try:
        style = ttk.Style()
        if "clam" in style.theme_names():
            style.theme_use("clam")
    except tk.TclError:
        pass
    TestStandApp(root)
    root.mainloop()
