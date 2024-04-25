import tkinter as tk
from tkinter import filedialog
from tkinter.scrolledtext import ScrolledText
import sys
from datetime import datetime
from serial.tools import list_ports
import serial

import test_PowerUnit
from test_PowerUnit import PowerUnit
import time
from Connection_STM import STM_manage
from Connection_MU import Mu_manage

test_data = [(7, '2', 7), (10, '2', 10), (15, '2', 15), (20, '2', 20), (30, '2', 30)]


# класс создания окна
class TestStandControlApp:
    def __init__(self, master):
        self.master = master
        self.master.title("TXC TESTER")
        self.master.geometry("900x350")
        self.create_widgets()

        # sys.stdout = self.CustomStdout(self.log_text)
        # sys.stderr = self.CustomStdout(self.log_text)

    # класс для кнопок в интерфейсе
    def create_widgets(self):
        # Разделение окна на две зоны
        self.left_frame = tk.Frame(self.master, width=300, bg="black")
        self.left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Терминал
        self.log_text = ScrolledText(self.left_frame, bg="black", fg="white")
        self.log_text.pack(fill=tk.BOTH, expand=True)

        self.right_frame = tk.Frame(self.master, width=400, bg="lightgray")
        self.right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Правая зона: текстовое окно другого цвета
        # Создаем список устройств
        self.devices = ["Мультиметр TH1951", "Блок Питания ODP3032", "Микроконтроллер STM32"]
        self.device_vars = []
        self.lamps = []

        available_ports = [port.device for port in serial.tools.list_ports.comports()]

        # if self.devices:
        #     for i, device in enumerate(self.devices):
        #         label = tk.Label(self.right_frame, text=device)
        #         label.grid(row=i, column=0, padx=10, pady=5)
        #
        #         com_var = tk.StringVar(self.right_frame)
        #         if available_ports:
        #             com_var.set(available_ports[i])
        #         else:
        #             com_var.set("")  # Set a default value if no ports are available
        #         option_menu = tk.OptionMenu(self.right_frame, com_var, *available_ports)
        #         option_menu.grid(row=i, column=1, padx=10, pady=5)
        #         self.device_vars.append(com_var)  # Add com_var to the list of device_vars
        #
        #         lamp = tk.Canvas(self.right_frame, width=20, height=20, bg="white", highlightthickness=0)
        #         lamp.grid(row=i, column=2, padx=10, pady=5)
        #         self.lamps.append(lamp)

        if self.devices:
            for i, device in enumerate(self.devices):
                label = tk.Label(self.right_frame, text=device)
                label.grid(row=i, column=0, padx=10, pady=5)

                com_var = tk.StringVar(self.right_frame)
                com_var.set(available_ports[i] if available_ports else "")
                option_menu = tk.OptionMenu(self.right_frame, com_var, *available_ports)
                # Устанавливаем COM порт по умолчанию, если доступны порты
                option_menu.grid(row=i, column=1, padx=10, pady=5)
                self.device_vars.append(com_var)  # Добавляем com_var в список device_vars

                lamp = tk.Canvas(self.right_frame, width=20, height=20, bg="white", highlightthickness=0)
                lamp.grid(row=i, column=2, padx=10, pady=5)
                self.lamps.append(lamp)

        # Добавляем кнопку для запуска теста
        self.start_button = tk.Button(self.right_frame, text="Подключение",
                                      command=self.start_test)
        self.start_button.grid(row=len(self.devices), column=0, columnspan=2, padx=10, pady=5)

        tests = ["Test1", "Test2", "Test3", "Test4"]
        test = tk.StringVar(self.right_frame)

        self.option_test = tk.OptionMenu(self.right_frame, test, *tests)
        test.set(tests[0])
        self.option_test.grid(row=len(self.devices) + 1, column=0, padx=5, pady=5)

        self.btn_stop = tk.Button(self.right_frame, text="СТОП", width=10, height=4,
                                  command="", bg="red")
        self.btn_stop.grid(row=8, column=0, padx=30, pady=30)
        self.btn_start = tk.Button(self.right_frame, text="СТАРТ", width=8, height=2,
                                   command=lambda: self.start(test_data), bg="green")
        self.btn_start.grid(row=4, column=1, padx=30, pady=30)
        self.btn_pause = tk.Button(self.right_frame, text="ПАУЗА", width=9, height=2,
                                   command="", bg="lightblue")
        self.btn_pause.grid(row=8, column=1, padx=30, pady=30)
        print(self.device_vars)

    # Кнопка проверка подключения устройств
    def start_test(self):
        for i, com_var in enumerate(self.device_vars):
            self.log_text.insert(tk.END, f"Проверка подключения")
            port = com_var.get()
            print(port)
            device = self.devices[i]
            color = "red"

            if i == 0:
                try:
                    self.mu_manage = Mu_manage(self.device_vars[1].get(), 9600)
                    print('подключились к Му')
                    print(self.mu_manage.parametr(), "СЮДА")
                    self.mu_manage.__del__()
                    color = "green"
                except serial.SerialException as e:
                    self.log_text.insert(tk.END, f"Ошибка при открытии порта {port}: {e}\n")
                self.lamps[i].config(bg=color)
                self.log_text.insert(tk.END, f"Статус подключения {device} к порту {port}: {color}\n")
                self.log_text.see(tk.END)
            elif i == 1:
                try:
                    self.power_unit = PowerUnit(self.device_vars[0].get(),
                                                115200)  # Создаем экземпляр PowerUnit с выбранным портом
                    print('подключились к БП')
                    self.power_unit.status_poll()
                    self.power_unit.__del__()
                    color = "green"
                except serial.SerialException as e:
                    self.log_text.insert(tk.END, f"Ошибка при открытии порта {port}: {e}\n")
                self.lamps[i].config(bg=color)
                self.log_text.insert(tk.END, f"Статус подключения {device} к порту {port}: {color}\n")
                self.log_text.see(tk.END)
            else:
                try:
                    self.stm_manage = STM_manage(self.device_vars[2].get(), 9600)
                    print('подключились к СТМ')
                    self.stm_manage.send_pin('00000')
                    self.stm_manage.__del__()
                    color = "green"
                except serial.SerialException as e:
                    self.log_text.insert(tk.END, f"Ошибка при открытии порта {port}: {e}\n")
                self.lamps[i].config(bg=color)
                self.log_text.insert(tk.END, f"Статус подключения {device} к порту {port}: {color}\n")
                self.log_text.see(tk.END)

    def start(self, test_data):
        self.mu_manage = Mu_manage(self.device_vars[1].get(), 9600)
        self.stm_manage = STM_manage(self.device_vars[2].get(), 9600)
        self.power_unit = PowerUnit(self.device_vars[0].get(),
                                    115200)  # Создаем экземпляр PowerUnit с выбранным портом
        for i, (voltage, pins, expected_voltage) in enumerate(test_data):
            self.stm_manage.send_pin(pins)
            self.power_unit.voltage_change(voltage, True)
            time.sleep(1)  # Подождать, чтобы обеспечить устойчивое измерение
            measured_voltage = self.power_unit.decode_response(self.power_unit.status_poll())["real_voltage"]
            print(f"Измеренное напряжение: {measured_voltage} В")
            if abs(float(measured_voltage) - expected_voltage) > 0.5:
                print("Ошибка: Измеренное напряжение не соответствует ожидаемому")
                return

            if i == len(test_data) - 1:
                print("Тест успешно завершен")
                return

            self.stm_manage.send_pin('11111')

        self.stm_manage.__del__()
        self.power_unit.__del__()
        self.mu_manage.__del__()
        pass

    def send_down_command(self):
        # self.serial_port.write(b'DOWN\n')
        pass

    def start_automatic_control(self):
        # for i = 3:
        #     check_mu = check_mu

        pass

    # класс для вывода в терминал в интерфейсе
    class CustomStdout:
        def __init__(self, text_widget):
            self.text_widget = text_widget

        # def write(self, string):
        #     current_time = datetime.now().strftime("[%H:%M:%S]")
        #     self.text_widget.insert(tk.END, current_time + string)
        #     self.text_widget.see(tk.END)


# Создаем основное окно
root = tk.Tk()
# Запускаем приложение
app = TestStandControlApp(root)
# Запускаем цикл обработки событий
root.mainloop()

