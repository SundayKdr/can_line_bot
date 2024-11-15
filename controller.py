import asyncio
import json
import logging
import signal
import sys

import ai_pizza_bot
import can_driver
import sensors_data
import scheduler


logging.basicConfig(level=logging.INFO, stream=sys.stdout)
log = logging.getLogger(__name__)


class Controller:
    def __init__(self, interface, channel, token):
        self.bot = ai_pizza_bot.AiPizzaBot(token, self)
        self.loop = asyncio.get_event_loop()
        self.can_bus = can_driver.CanDriver(interface=interface, channel=channel, loop=self.loop)
        self.sensors = sensors_data.SensorsData()
        self.scheduler = scheduler.Scheduler(delay_s=60, action_coro=self.info_broker, loop=self.loop)
        self.saved_data: dict = {}
        self.set_callbacks()
        self.load_saved_data()

    def start_app(self):
        self.loop.add_signal_handler(signal.SIGINT, lambda: (print("bot close"), self.bot.close()))
        self.loop.add_signal_handler(signal.SIGTERM, lambda: (print("bot close"), self.bot.close()))
        self.bot.run(self.loop)
        self.can_bus.run()
        self.scheduler.run()
        self.loop.create_task(self.bot.on_start_msg())
        self.loop.run_forever()

    async def info_broker(self) -> None:
        info = self.sensors.get_info()
        await self.bot.can_msg_dispatch(info)

    async def update_info_on_req(self) -> None:
        info = self.sensors.get_info(reset=False)
        await self.bot.can_msg_dispatch(info)

    def set_scheduler_delay(self, delay: int):
        if 0 < delay < 172800:
            self.scheduler.delay = delay
            self.saved_data["delay"] = delay
            self.save_data()

    def add_chat(self, chat_id):
        self.saved_data["chats"].append(chat_id)
        self.save_data()

    def remove_chat(self, chat_id):
        try:
            self.saved_data["chats"].remove(chat_id)
            self.save_data()
        except:
            log.info(f"trying to remove non existing chat {chat_id}")

    def set_callbacks(self):
        self.can_bus.add_callback(self.sensors.line_update)

    def save_data(self):
        json.dump(self.saved_data, open("saved.json", "w"), indent=4)

    def set_id_name(self, id_: str, name: str):
        self.sensors.add_name(id_, name)
        self.saved_data["names"][id_] = name
        self.save_data()

    def load_saved_data(self):
        self.saved_data = json.load(open('saved.json', 'r'))
        self.sensors.set_names(self.saved_data["names"])
        self.scheduler.delay = self.saved_data["delay"]
        self.bot.set_chats(self.saved_data["chats"])
