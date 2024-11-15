import asyncio
import logging

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
log = logging.getLogger(__name__)


class Scheduler:
    def __init__(self, delay_s, action_coro, loop):
        self.__delay = delay_s
        self.__enable = True
        self.__action_coro = action_coro
        self.loop = loop
        self.__task: asyncio.Task = None

    async def task(self):
        while self.enable:
            await asyncio.sleep(self.__delay)
            await self.__action_coro()

    def run(self):
        self.__task = self.loop.create_task(self.task())
        log.info(f"scheduled task started delay:{self.delay}")

    @property
    def delay(self):
        return self.__enable

    @delay.setter
    def delay(self, seconds: int):
        self.__delay = seconds
        log.info(f"new delay set :{self.delay}")
        if self.__task is not None:
            self.__task.cancel()
            self.__task = self.loop.create_task(self.task())

    @property
    def enable(self):
        return self.__enable

    @enable.setter
    def enable(self, en: bool):
        self.__enable = en
