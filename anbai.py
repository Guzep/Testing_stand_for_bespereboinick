import serial

# #idn?
# AT4508,REV S3.6,450801505367,01,Applent Instruments Inc.
# fetch?
# -1.000000e+05,-1.000000e+05,-1.000000e+05,-1.000000e+05,2.516196e+01,2.494082e+01,2.443367e+01,2.440600e+01,

class anbai:
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

    def send_command(self, command):
        self.serial_.write((command + "\n").encode())
        response = self.serial_.readline().decode().strip()
        return response

    def check(self):
        response = self.send_command('IDN?')
        if response == 'AT4508,REV S3.6,450801505367,01,Applent Instruments Inc.':
            return "Online"
        else:
            return "Offline"

    def temperature(self):
        response = self.send_command('fetch?')
        # Преобразуем строку в список чисел, исключая пустые элементы
        numbers = [float(x) for x in response.split(',') if x != '']
        # Округляем все числа с точностью до двух знаков после запятой
        rounded_numbers = [round(num, 2) for num in numbers]
        return rounded_numbers

    def __del__(self):
        if self.serial_ and self.serial_.isOpen():
            self.serial_.close()
        return print("Порт закрыт")


# if __name__ == "__main__":
#     anbai = anbai("COM15", 9600)