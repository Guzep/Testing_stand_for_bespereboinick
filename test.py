import tkinter as tk
from tkinter import ttk

def save_data():
    print("Данные сохранены")

def connect_com1():
    print("COM1 подключен")

def connect_com2():
    print("COM2 подключен")

def open_log():
    print("Открыт лог файл")

def save_config():
    print("Конфигурация сохранена")

# Создаем основное окно
root = tk.Tk()
root.title("Terminal Tester")
root.geometry("400x300")

# Добавляем элементы интерфейса

# Заголовок
label_title = tk.Label(root, text="Terminal Tester", font=("Arial", 14))
label_title.grid(row=0, column=0, columnspan=3, pady=10)

# Подключение COM портов
label_com1 = tk.Label(root, text="COM1:")
label_com1.grid(row=1, column=0, padx=5, pady=5, sticky="w")

btn_com1 = tk.Button(root, text="Подключить", command=connect_com1)
btn_com1.grid(row=1, column=1, padx=5, pady=5)

label_com2 = tk.Label(root, text="COM2:")
label_com2.grid(row=2, column=0, padx=5, pady=5, sticky="w")

btn_com2 = tk.Button(root, text="Подключить", command=connect_com2)
btn_com2.grid(row=2, column=1, padx=5, pady=5)

# Поле для сигнала/данных
text_data = tk.Text(root, height=5, width=40)
text_data.grid(row=3, column=0, columnspan=3, padx=10, pady=10)

# Кнопки
btn_save = tk.Button(root, text="Сохранить", command=save_data)
btn_save.grid(row=4, column=0, padx=5, pady=5)

btn_log = tk.Button(root, text="Открыть лог", command=open_log)
btn_log.grid(row=4, column=1, padx=5, pady=5)

btn_save_config = tk.Button(root, text="Сохранить конфигурацию", command=save_config)
btn_save_config.grid(row=5, column=0, columnspan=2, padx=5, pady=5)

# Запуск основного цикла приложения
root.mainloop()