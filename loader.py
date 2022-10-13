from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from data import config
from data.config import DATABASE
from utils.db.storage import MongoHandler

bot = Bot(token=config.BOT_TOKEN, parse_mode=types.ParseMode.HTML)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
DB_CONF = DATABASE['mongodb']
db = MongoHandler(DB_CONF['db'])
add_to_cart_status = {}
status_buyout_complete = {}
images_buyout = {}