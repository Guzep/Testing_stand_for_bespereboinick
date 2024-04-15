import serial




"""
$COMMON,DUALCHANNEL  ,1,1,1,  12.000,0.500,0.000,0.000,  16.000,  1.100,  1,1,1,7.500,3.000,0.000,0.000,12.500,1.100,5237#
$COMMON,INDEPENDENT  ,1,1,1,  5.000,3.000,0.000,0.000,   1.000,   0.600,  1,1,1,1.000,0.300,0.000,0.000,5.000,0.600,5239#
$COMMON,PARALLEL     ,1,1,1,  5.000,1.000,0.000,0.000,   16.000,  1.200,  1,1,1,5.000,1.000,0.000,0.000,16.000,1.200,5160#
$COMMON,SERIES,       1,0,0,  15.000,2.000,0.000,0.000,  60.000,  3.000,  1,0,0,15.000,2.000,0.000,0.000,60.000,3.000,5124#
"""


import time
class PowerUnit:
    BAUD_RATE = 115200
    VOLTAGE_OFFSET_MAP = {
        range(0, 10): 706,
        range(10, 20): 755,
        range(20, 30): 756,
        range(30, 40): 757,
        range(40, 50): 758,
        range(50, 60): 759,
        range(60, 62): 760,

    }
    CURRENT_OFFSET_MAP = {
        range(0, 1): 687,
        range(1, 3): 688,
        range(2, 4): 689,


    }
    MODE_COMMANDS = {
        0: "&COMMON,PARALLEL,1134",
        1: "&COMMON,SERIES,1004",
        2: "&COMMON,DOUBLE,988",

    }
    SWITCH_COMMANDS = {
        True: "&SW1,0,355",
        False: "&SW1,1,356"
    }

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

    def _calculate_offset(self, value, offset_map):
        for range_, offset_base in offset_map.items():
            if value in range_:
                return offset_base + value - range_.start

    def voltage_change(self, voltage, flag=True): # сделать флаг включения
        """
        Метод для изменения напряжения с целыми значениями.
        Args:
            voltage (int): Значение напряжения 0-60В.
            Изначально voltage=0
        Returns:
            bool: результат применения команды
        """
        if not 0 <= voltage <= 60:
            raise ValueError("Напряжение должно быть от 0 до 60 В")
        offset = self._calculate_offset(voltage, self.VOLTAGE_OFFSET_MAP)

        if flag:
            self.switching_on_off(True)

            self.send_command(f"&SSERIV,{voltage}.0,{offset}")
            for _ in range(15):
                voltage_test = self.decode_response(self.status_poll())["real_voltage"]
                if int(float(voltage_test)) == voltage:
                    return True
            return False
        self.switching_on_off(False)
        return self.send_command(f"&SSERIV,{voltage}.0,{offset}")

    def current_change(self, current):
        """
        Метод для изменения тока с целыми значениями
        Args:
            current (int): Значение тока 0-3А.
            Изначально current=0
        Returns:
            str: Строка с командой для изменения тока.
        """
        if not 0 <= current <= 3:
            raise ValueError("Ток должен быть от 0 до 3 А")
        offset = self._calculate_offset(current, self.CURRENT_OFFSET_MAP)
        return self.decode_response(self.send_command(f"&SSERIC,{current}.0,{offset}"))

    def mode_change(self, mode):
        """
        Метод для изменения режима
        Args:
            mode (int): 0 - PARALLEL, 1 - SERIES, 2 - DOUBLE
            изначально mode=0
        Returns:
            str: Строка с командой для изменения режима.
        """
        if mode not in self.MODE_COMMANDS:
            raise ValueError("Такого режима нет")
        return self.send_command(self.MODE_COMMANDS[mode])

    def switching_on_off(self, switch=True):
        return self.send_command(self.SWITCH_COMMANDS[switch])

    def send_command(self, command):
        """
        Метод для отправки команды устройству и получения ответа
        Args:
            command (str): Команда для отправки
        Returns:
            str: Ответ от устройства.
        """
        self.serial_.write((command + "\n").encode())
        response = self.serial_.readline().decode().strip()
        return response

    def decode_response(self, data, channel=1):
        data = data.split(",")
        ch_data = {
            "set_voltage": data[5],
            "set_current": data[6],
            "real_voltage": data[7],
            "real_current": data[8]
        }
        return ch_data if channel == 1 else ch_data.copy()

    def status_poll(self):
        return self.send_command("&SYNCHRO,0,686")

    def christmas_tree_testing(self):
        # # Подключение

        #изменение режима
        command = self.mode_change(1)
        response = self.send_command(command)
        print(response)
        # изменение напряжения
        for voltage in range(0, 61):
            command = self.voltage_change(voltage)
            response = self.send_command(command)
            print(response)
        print("Тестирование напряжения : Успешно")
        print("___________________________________________________________________________")
        print("Тестирование Тока")
        # Изменение тока
        for current in range(3):
            command = self.current_change(current)
            response = self.send_command(command)
            print(response)
        print("___________________________________________________________________________")
        # Изменение режима
        for mode in range(4):
            command = self.mode_change(mode)
            response = self.send_command(command)
            print(response)
        print("___________________________________________________________________________")
        # Включение и выключение
        for switch in [True, False]:
            command = self.switching_on_off(switch)
            response = self.send_command(command)
            print(response)
        print("___________________________________________________________________________")
        # Изменение напряжения
        # Закрытие соединения
    # def __del__(self):
    #     if self.serial_ and self.serial_.isOpen():
    #         self.serial_.close()
    #     return print("Порт закрыт")


    def __del__(self):
        if self.serial_ and self.serial_.isOpen():
            self.serial_.close()
        return print("Порт закрыт")



if __name__ == "__main__":
    power_unit = PowerUnit("COM11", 125000)
    power_unit.christmas_tree_testing()