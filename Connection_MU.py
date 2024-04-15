import serial
import time

COM_PORT = 'COM12'
BAUD_RATE = 9600

# Создание объекта serial для общения с мультиметром
class Mu_manage:

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

    # Функция для отправки команд и получения ответов от мультиметра
    def send_command(self, command):
        self.serial_.write((command + '\n').encode('ascii'))  # Отправка команды
        time.sleep(0.02)  # небольшая задержка для обработки команды мультиметром
        response = self.serial_.readline().strip()  # Чтение ответа
        return response

    def parametr(self):
        measurement_command = ":FETC?"
        response = self.send_command(measurement_command)
        print(f"Ответ мультиметра: {response}")
        return response

    def mode_resistance(self):
        measurement_command = ":FUNC CURR:AC"
        response = self.send_command(measurement_command)
        print(f"Ответ мультиметра: {response}")
        return response

    def mode_voltage(self):
        measurement_command = ":trig:sour bus;*trg"
        response = self.send_command(measurement_command)
        print(f"Ответ мультиметра: {response}")
        return response

    def __del__(self):
        if self.serial_ and self.serial_.isOpen():
            self.serial_.close()
        return print("Порт закрыт")

#if __name__ == "__main__":
    #connection_MU = Mu_manage("COM12")

# print(send_command(":trig:sour bus;*trg"))
#
# # print(send_command(":volt:dc:rang 1.0"))
# for i in range(100):
#     # # измерение начать
#     # print(send_command(":func volt:ac")) #вкл измерение ас
#     # time.sleep(1)
#     # print(f"ABORT {send_command(':ABORT')}") #сбросили последнее значение
#     # time.sleep(1)
#     # print(f"READ {send_command(':READ?')}") #прочитали значение здесь и сейчас
#     # time.sleep(1)
#     # print(f"CONF {send_command(':CONF?')}") #узнали какой режим сейчас включен
#     # print(f"FUNC {send_command('FUNC?')}") #показывает какой режим сейчас включен
#     # print(f"data {send_command('DATA?')}") #показывает какой режим сейчас включен
#
#
#
#     # print(send_command(':DISP:ENAB 0')) #Выключили дисплей
#     # print(send_command(':DISP:ENAB?')) #Проверили режим
#     # print(send_command(':DISP:ENAB 1')) #Включили дисплей
#     # print(send_command(':DISP:ENAB?')) #проверили режим
#
#
#
#     time.sleep(2)
#     # print(send_command(":func curr:ac"))
#     # time.sleep(0.2)
#     # print(parametr())
#     # print(f"data {send_command('CONF?')}")  # показывает какой режим сейчас включен
#     # print(send_command(":func curr:dc"))
#     # time.sleep(0.2)
#     # print(parametr())
#     print(f"data {send_command('CONF?')}")  # показывает какой режим сейчас включен
#     print(send_command(":func RES"))
#     time.sleep(0.2)
#     print(parametr())
#     print(f"data {send_command('CONF?')}")  # показывает какой режим сейчас включен
#     print(send_command(":func FRES"))
#     time.sleep(0.2)
#     print(parametr())
#     # print(f"data {send_command('CONF?')}")  # показывает какой режим сейчас включен
#     # print(send_command(":func FREQ"))
#     # time.sleep(0.2)
#     # print(parametr())
#     # print(f"data {send_command('CONF?')}")  # показывает какой режим сейчас включен
#     # print(send_command(":func PER"))
#     # time.sleep(0.2)
#     # print(parametr())
#     # print(f"data {send_command('CONF?')}")  # показывает какой режим сейчас включен
#     # print(send_command(":func DIOD"))
#     # time.sleep(0.2)
#     # print(parametr())
#     # print(f"data {send_command('CONF?')}")  # показывает какой режим сейчас включен
#     # print(send_command(":func CONT"))
#     # time.sleep(0.2)
#     # print(parametr())
#     # print(f"data {send_command('CONF?')}")  # показывает какой режим сейчас включен
#     # print(send_command(":DISP:ENAB 0"))
#     # time.sleep(0.2)
#     # print(parametr())
#     # print(f"data {send_command('CONF?')}")  # показывает какой режим сейчас включен
#     # print(send_command(":DISP:ENAB 1"))
#     # print(parametr())
#     # print(f"data {send_command('CONF?')}")  # показывает какой режим сейчас включен
#     #
#
# # Закрытие соединения

