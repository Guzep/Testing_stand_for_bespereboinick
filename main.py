from datetime import datetime
import tkinter as tk
from tkinter.scrolledtext import ScrolledText
import time
import threading
import serial
from serial.tools import list_ports
from anbai import anbai
from test_PowerUnit import PowerUnit

# Основной класс для приложения контроля тестового стенда
class TestStandControlApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Termal_tester v1.0")
        self.master.geometry("1000x500")
        self.create_widgets()
        self.test_counter = 1  # Счетчик тестов

    # Создание интерфейса приложения
    def create_widgets(self):
        self.left_frame = tk.Frame(self.master, width=300, bg="black")
        self.left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.log_text = ScrolledText(self.left_frame, bg="black", fg="white")
        self.log_text.pack(fill=tk.BOTH, expand=True)

        self.right_frame = tk.Frame(self.master, width=400, bg="lightgray")
        self.right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.devices = ["AT4508", "Блок Питания ODP3032"]
        self.device_vars = []  # Переменные для выбора COM-портов
        self.lamps = []  # Индикаторы состояния устройств

        available_ports = [port.device for port in serial.tools.list_ports.comports()]

        for i, device in enumerate(self.devices):
            label = tk.Label(self.right_frame, text=device)
            label.grid(row=i, column=0, padx=10, pady=5)

            com_var = tk.StringVar(self.right_frame)
            com_var.set(available_ports[i] if available_ports else "")
            option_menu = tk.OptionMenu(self.right_frame, com_var, *available_ports)
            option_menu.grid(row=i, column=1, padx=10, pady=5)
            self.device_vars.append(com_var)

            lamp = tk.Canvas(self.right_frame, width=20, height=20, bg="white", highlightthickness=0)
            lamp.grid(row=i, column=2, padx=10, pady=5)
            self.lamps.append(lamp)

        self.start_button = tk.Button(self.right_frame, text="Подключение", command=self.start_test)
        self.start_button.grid(row=len(self.devices), column=0, columnspan=2, padx=10, pady=5)

        self.start_button = tk.Button(self.right_frame, text="Снять сейчас", command=self.form_list_now)
        self.start_button.grid(row=len(self.devices) + 1, column=0, padx=10, pady=5)

        self.start_button = tk.Button(self.right_frame, text="Выбрать время", command=self.open_input_window)
        self.start_button.grid(row=len(self.devices) + 2, column=0, padx=10, pady=5)

    # Проверка подключения устройств
    def start_test(self):
        for i, com_var in enumerate(self.device_vars):
            self.log_text.insert(tk.END, f"Проверка подключения\n")
            port = com_var.get()
            device = self.devices[i]
            color = "red"

            if i == 0:
                try:
                    self.anbai = anbai(self.device_vars[0].get(), 9600)
                    print('Подключились к AT4508')
                    self.anbai.__del__()
                    color = "green"
                except serial.SerialException as e:
                    self.log_text.insert(tk.END, f"Ошибка при подключении к {port}: {e}\n")
                self.lamps[i].config(bg=color)

            elif i == 1:
                try:
                    self.power_unit = PowerUnit(self.device_vars[1].get(), 115200)
                    print('Подключились к БП')
                    self.power_unit.status_poll()
                    self.power_unit.__del__()
                    color = "green"
                except serial.SerialException as e:
                    self.log_text.insert(tk.END, f"Ошибка при подключении к {port}: {e}\n")
                self.lamps[i].config(bg=color)

            self.log_text.insert(tk.END, f"Статус подключения {device} к порту {port}: {color}\n")
            self.log_text.see(tk.END)

    # Запуск функции в течение заданного времени с паузами и запись данных в новый файл
    def run_for_duration(self, duration_minutes, pause_time):
        total_time = (duration_minutes * 60) +1  # Преобразование минут в секунды
        start_time = time.time()

        # Генерация имени файла с учетом времени начала теста
        start_time_str = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"test_results_{start_time_str}.txt"

        with open(filename, 'w') as file:
            file.write("№\tT\tU\tI\tt1\tt2\tU5, В\tU15, В\n")
            minute_counter = 1  # Счетчик минут для поля T (время проведения теста)

            while (time.time() - start_time) < total_time:
                test_data = self.form_list(minute_counter)  # Сбор данных
                data_with_empty = test_data + ["", ""]  # Добавляем пустые столбцы для U5, В и U15, В
                file.write("\t".join(str(x) for x in data_with_empty) + "\n")  # Запись данных в файл
                minute_counter += pause_time
                self.test_counter += 1
                time.sleep(pause_time * 60)  # Пауза

        self.test_counter = 1
        self.log_text.insert(tk.END, f"Файл с результатами теста сформирован: {filename}\n")
        self.log_text.insert(tk.END, "Вы можете открыть файл и просмотреть результаты.\n")
        self.log_text.see(tk.END)

    def open_input_window(self):
        def on_submit():
            try:
                duration = int(duration_entry.get())
                pause_time = int(pause_entry.get())
                threading.Thread(target=self.run_for_duration, args=(duration, pause_time)).start()
                input_window.destroy()
            except ValueError:
                self.log_text.insert(tk.END, "Ошибка: введите корректные значения.\n")

        input_window = tk.Toplevel(self.master)
        input_window.title("Введите время")

        duration_label = tk.Label(input_window, text="Введите время работы в минутах:")
        duration_label.pack(padx=10, pady=5)

        duration_entry = tk.Entry(input_window)
        duration_entry.pack(padx=10, pady=5)

        pause_label = tk.Label(input_window, text="Введите паузу в минутах:")
        pause_label.pack(padx=10, pady=5)

        pause_entry = tk.Entry(input_window)
        pause_entry.pack(padx=10, pady=5)

        submit_button = tk.Button(input_window, text="Запустить", command=on_submit)
        submit_button.pack(padx=10, pady=10)

    # Сбор данных с устройств и возврат списка данных
    def form_list(self, minute_counter):
        test_data = [self.test_counter, minute_counter, 0, 0, 0, 0]  # Добавление счетчика тестов и минут
        self.power_unit = PowerUnit(self.device_vars[1].get(), 115200)
        power_data = self.power_unit.status_poll()
        power_data = self.power_unit.decode_response(power_data, channel=1)
        test_data[2], test_data[3] = float(power_data['real_voltage']), float(power_data['real_current'])

        self.anbai = anbai(self.device_vars[0].get(), 9600)
        temp_list = self.anbai.temperature()
        test_data[4], test_data[5] = temp_list[0], temp_list[1]

        self.power_unit.__del__()
        self.anbai.__del__()
        iteration_time = 'Итерация №' + str(test_data[0]) + ' Время ' + str(test_data[1]) + 'мин.\n'
        results_for_log = ('U = ' + str(test_data[2]) + ' I = ' + str(test_data[3]) + ' t1 = ' + str(test_data[4]) +
                           ' t2 = ' + str(test_data[5]) + '\n')
        self.log_text.insert(tk.END, iteration_time)
        self.log_text.insert(tk.END, results_for_log)
        return test_data

        # Сбор данных с устройств и возврат списка данных
    def form_list_now(self):
            test_data = [0, 0, 0, 0, 0, 0]
            self.power_unit = PowerUnit(self.device_vars[1].get(), 115200)
            power_data = self.power_unit.status_poll()
            power_data = self.power_unit.decode_response(power_data, channel=1)
            test_data[2], test_data[3] = float(power_data['real_voltage']), float(power_data['real_current'])

            self.anbai = anbai(self.device_vars[0].get(), 9600)
            temp_list = self.anbai.temperature()
            test_data[4], test_data[5] = temp_list[0], temp_list[1]

            self.power_unit.__del__()
            self.anbai.__del__()
            iteration_time = 'Итерация №' + str(test_data[0]) + ' Время ' + str(test_data[1]) + 'мин.\n'
            results_for_log = ('U = ' + str(test_data[2]) + ' I = ' + str(test_data[3]) + ' t1 = ' + str(test_data[4]) +
                               ' t2 = ' + str(test_data[5]) + '\n')
            self.log_text.insert(tk.END, iteration_time)
            self.log_text.insert(tk.END, results_for_log)
            return test_data

# Создание основного окна приложения
root = tk.Tk()
app = TestStandControlApp(root)
root.mainloop()
