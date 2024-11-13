import asyncio
import signal

import can

import ai_pizza_bot
import can_driver
import sensors_data
import scheduler


class Controller:
    def __init__(self, interface, channel, token):
        self.bot = ai_pizza_bot.AiPizzaBot(token, self)
        self.loop = asyncio.get_event_loop()
        self.can_bus = can_driver.CanDriver(interface=interface, channel=channel, loop=self.loop)
        self.sensors = sensors_data.SensorsData()
        self.scheduler = scheduler.Scheduler(delay_s=5, action_coro=self.info_broker, loop=self.loop)
        self.set_callbacks()

    def start_app(self):
        self.loop.add_signal_handler(signal.SIGINT, lambda: (print("bot close"), self.bot.close()))
        self.loop.add_signal_handler(signal.SIGTERM, lambda: (print("bot close"), self.bot.close()))
        self.bot.run(self.loop)
        self.can_bus.run()
        self.scheduler.run()
        self.loop.run_forever()

    async def info_broker(self) -> None:
        info = self.sensors.get_info()
        await self.bot.can_msg_dispatch(info)

    def set_scheduler_delay(self, delay: int):
        if 0 < delay < 172800:
            self.scheduler.delay = delay

    def set_callbacks(self):
        self.can_bus.add_callback(self.sensors.line_update)

    def set_id_name(self, id_: str, name: str):
        self.sensors.add_name(id_, name)
