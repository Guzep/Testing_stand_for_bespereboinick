import serial
import time

# COM_PORT = 'COM13'
# BAUD_RATE = 9600
cmd = '11111'
class STM_manage:

    def __init__(self, com_port: str, BAUD_RATE: int):
        self.com_port = com_port
        self.BAUD_RATE = BAUD_RATE
        self.serial_ = None
        self.connect()

    def connect(self):
        try:
            self.serial_ = serial.Serial(self.com_port, self.BAUD_RATE, timeout=0.5)
        except serial.SerialException as e:
            print(f"Ошибка при подключении к {self.com_port}: {e}")
            raise
    def send_pin(self, command):
        self.serial_.write((command).encode())
        response = self.serial_.readline().decode().strip()
        return response

    def __del__(self):
        if self.serial_ and self.serial_.isOpen():
            self.serial_.close()
        return print("Порт закрыт")

