import logging
import sys

from aiogram import Bot, Dispatcher, html, Router
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.types import Message

logging.basicConfig(level=logging.INFO, stream=sys.stdout)
log = logging.getLogger(__name__)


class AiPizzaBot(Bot):
    def __init__(self, token, controller):
        super().__init__(token=token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
        self.controller = controller
        self.__token = token
        self.__chat_ids = []
        with open('chat_ids.txt', 'r') as file:
            self.__chat_ids = [int(line.rstrip()) for line in file]
        self.router = Router(name=__name__)
        self.dp = Dispatcher()
        self.dp.include_router(self.router)
        self.reg_cmds()

    def reg_cmds(self):
        self.router.message.register(self.message_handler, lambda message: message.text == "hello")
        self.router.message.register(self.command_start_handler, CommandStart())
        self.router.message.register(self.delay_setter, Command("delay"))
        self.router.message.register(self.name_setter, Command("name"))

    async def message_handler(self, message: Message) -> None:
        await message.answer(f"Hello!")

    async def delay_setter(self, message: Message) -> None:
        new_delay = int(message.text.split(" ")[-1])
        log.info(f"new delay:{new_delay}")
        self.controller.set_scheduler_delay(new_delay)

    async def name_setter(self, message: Message) -> None:
        cmd, id_, name_ = message.text.rstrip().split(" ")
        log.info(f"new name:{name_} for id:{id_}")
        self.controller.set_id_name(id_, name_)

    def run(self, loop):
        loop.create_task(self.polling())
        log.info("can driver started")

    async def polling(self):
        await self.dp.start_polling(self)

    async def can_msg_dispatch(self, msg_list) -> None:
        for chat in self.__chat_ids:
            for msg in msg_list:
                await self.send_message(chat_id=chat, text=msg)

    async def command_start_handler(self, message: Message) -> None:
        user = message.from_user.full_name
        chat_id = message.chat.id
        if chat_id in self.__chat_ids:
            await message.answer(f"Привет, {html.bold(user)}, ты уже в деле!")
            return
        self.__chat_ids.append(message.chat.id)
        with open('chat_ids.txt', 'a') as file:
            file.write(f'{message.chat.id}\n')
        await message.answer(f"Привет, {html.bold(user)}, это Дом Пицы!"
                             "Тут будет обновляться информация по датчикам"
                             "что бы открыть настройки комнда /set")
