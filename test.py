import serial.tools.list_ports


# def list_serial_ports():
#     target_devices = [("067B", "23A3"), ("067B", "2303"), ("10C4", "EA60")]
#     ports = serial.tools.list_ports.comports()
#     filtered_ports = []
#
#     for port, desc, hwid in sorted(ports):
#         for vid, pid in target_devices:
#             if f"VID_{vid}&PID_{pid}" in hwid.upper():
#                 filtered_ports.append((port, desc, hwid))
#                 break
#
#     if filtered_ports:
#         print("Список доступных COM-портов:")
#         for index, (port, desc, hwid) in enumerate(filtered_ports, start=1):
#             print(f"{index}. COM порт: {port}")
#             if desc:
#                 print(f"   Описание: {desc}")
#             if hwid:
#                 print(f"   ID устройства: {hwid}")
#             print()
#     else:
#         print("COM-порты с заданными VID и PID не найдены.")



# if __name__ == "__main__":
#     list_serial_ports()

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

test_data = [(7, '2', 7), (10, '2', 7), (15, '2', 3.686), (20, '2', 3.686), (30, '2', 3.686)]
available_ports = [port.device for port in serial.tools.list_ports.comports()]
print(available_ports)

