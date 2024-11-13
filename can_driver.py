import asyncio
import signal

import can
import logging

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
log = logging.getLogger(__name__)


def make_can_msg_(id_, bytes_: tuple):
    return can.Message(
        arbitration_id=id_,
        data=bytes_,
        is_extended_id=True
    )


async def print_msg(msg) -> None:
    print(msg)


class CanDriver:
    def __init__(self, interface, channel, loop):
        self.loop = loop
        self.__can = can.Bus(interface=interface, channel=channel, receive_own_messages=True)
        self.reader = can.AsyncBufferedReader()
        self.notifier = can.Notifier(self.__can, [self.reader], loop=loop)
        self.logger = can.Logger("logfile.asc")
        self.listeners = [print_msg]

    async def service_buffer(self):
        while True:
            msg = await self.reader.get_message()
            [await cb(msg) for cb in self.listeners]

    def get_can(self):
        return self.__can

    def send(self, msg):
        try:
            self.__can.send(msg)
            return f"Message sent on {self.__can.channel_info}"
        except can.CanError:
            return "Message NOT sent"

    def add_callback(self, call_back):
        log.info(f'call_back added:{call_back}')
        self.listeners.append(call_back)

    def stop_reading(self):
        self.notifier.stop()

    def run(self):
        self.loop.create_task(self.service_buffer())
        log.info("can driver started")
