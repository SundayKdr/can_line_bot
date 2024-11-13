from datetime import datetime
import logging

import can
import struct

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
log = logging.getLogger(__name__)


class Data:
    def __init__(self, id_, value, name):
        self.id: int = id_
        self.__name: str = name
        self.__last_value: float = value
        self.__values_sum: float = value
        self.__values_cnt: int = 1
        self.__last_update: datetime = datetime.now()

    def add_value(self, v: float):
        self.__values_sum += v
        self.__values_cnt += 1
        self.__last_update = datetime.now()
        self.__last_value = v

    def get_average(self) -> float:
        if self.__values_cnt > 0:
            return self.__values_sum / self.__values_cnt
        else:
            return 0

    def reset(self):
        self.__values_sum = 0
        self.__values_cnt = 0

    @property
    def name(self):
        return self.__name

    @name.setter
    def name(self, name_: str):
        self.__name = name_
        log.info(f"new name set:{self.__name} id:{self.id}")

    def __str__(self):
        if self.__values_cnt == 0:
            return f'Имя:{self.__name} (id:{self.id}) не было обновлений'
        return f'Имя: {self.__name} (id: {self.id})' \
               f'\nпоследнее обновление: {self.__last_update.strftime("%H:%M:%S %d-%m-%Y")}' \
               f'\nпоследнее значение: {f"{self.__last_value:.2f}"}' \
               f'\nсреднее: {f"{self.get_average():.2f}"}' \
               f'\nколичество записей: {self.__values_cnt}'


class SensorsData:
    def __init__(self):
        self.sensors: dict[str, Data] = {}
        self.sensors_names: dict[str, str] = {}
        with open('sensors_names.txt', 'r') as file:
            for line in file:
                id_, name_ = line.rstrip().split("|")
                self.sensors_names[id_] = name_

    async def line_update(self, msg: can.Message):
        if len(msg.data) < 6:
            return
        value_id: str = str(msg.data[0])
        value_float: float = struct.unpack('f', msg.data[2:6])[0]
        if value_id in self.sensors:
            self.sensors[value_id].add_value(v=value_float)
        else:
            name: str = self.sensors_names[value_id] if value_id in self.sensors_names else "Нет имени"
            self.sensors[value_id] = Data(value_id, value_float, name)

    def get_info(self):
        ret_val = []
        for _, sensor in self.sensors.items():
            ret_val.append(str(sensor))
            sensor.reset()
        return ret_val

    def add_name(self, id_: str, name_: str):
        if id_ in self.sensors:
            self.sensors[id_].name = name_
        self.sensors_names[id_] = name_
        with open('sensors_names.txt', 'w') as file:
            for w_id, w_name in self.sensors_names.items():
                file.write(f'{w_id}|{w_name}\n')
