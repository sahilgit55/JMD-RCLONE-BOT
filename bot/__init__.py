from faulthandler import enable as faulthandler_enable
from socket import setdefaulttimeout
from uvloop import install

faulthandler_enable()
install()
setdefaulttimeout(600)



from pyrogram import Client, enums
from asyncio import get_event_loop
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from time import time
from tzlocal import get_localzone
from requests import get
from os.path import exists

from config import LOGGER, log_file, user_data, config_dict, list_drives_dict, shorteneres_list, extra_buttons, categories_dict, bot_id, GLOBAL_EXTENSION_FILTER, PORT, BASE_URL
from ml_config import download_dict_lock, status_reply_dict_lock, queue_dict_lock, status_reply_dict, download_dict, Interval, DRIVES_NAMES, DRIVES_IDS, INDEX_URLS, aria2_options, queued_dl, queued_up, non_queued_dl, non_queued_up, aria2, aria2c_global
from subprocess import Popen
from subprocess import run as srun

botloop = get_event_loop()
botStartTime = time()


LOGGER.info(f'Starting Bot')
bot = Client(
    "Nik66Bot",
    api_id=config_dict['TELEGRAM_API'],
    api_hash=config_dict['TELEGRAM_HASH'],
    bot_token=config_dict['BOT_TOKEN'],
    workers=1000,
    parse_mode=enums.ParseMode.HTML,
    max_concurrent_transmissions=1000).start()

bot_loop = bot.loop
bot_name = bot.me.username
scheduler = AsyncIOScheduler(timezone=str(
    get_localzone()), event_loop=bot_loop)


IS_PREMIUM_USER = False
user = ''
if len(config_dict['USER_SESSION_STRING']) != 0:
    LOGGER.info("Creating client from USER_SESSION_STRING")
    user = Client('user',
                        config_dict['TELEGRAM_API'],
                        config_dict['TELEGRAM_HASH'],
                        session_string=config_dict['USER_SESSION_STRING'],
                        parse_mode=enums.ParseMode.HTML,
                        no_updates=True,
                        max_concurrent_transmissions=1000).start()
    if user.me.is_bot:
        LOGGER.warning(
            "You added bot string for USER_SESSION_STRING this is not allowed! Exiting now")
        user.stop()
        exit(1)
    else:
        IS_PREMIUM_USER = user.me.is_premium

Popen(f"gunicorn webserver.wserver:app --bind 0.0.0.0:{PORT} --worker-class gevent", shell=True)


qbit_options = {}
rss_dict = {}
cached_dict = {}
OWNER_ID = config_dict['OWNER_ID']
DATABASE_URL = config_dict['DATABASE_URL']
CMD_SUFFIX = config_dict['CMD_SUFFIX']
DOWNLOAD_DIR = config_dict['DOWNLOAD_DIR']
MAX_SPLIT_SIZE = 4194304000 if IS_PREMIUM_USER else 2097152000

if len(config_dict['LEECH_SPLIT_SIZE']) == 0 or int(config_dict['LEECH_SPLIT_SIZE']) > MAX_SPLIT_SIZE:
    config_dict['LEECH_SPLIT_SIZE'] = MAX_SPLIT_SIZE
else:
    config_dict['LEECH_SPLIT_SIZE'] = int(config_dict['LEECH_SPLIT_SIZE'])

get_client = None