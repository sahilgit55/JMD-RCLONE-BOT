from bot import bot, botloop, LOGGER, log_file, botloop, Interval, scheduler
from os import execl as osexecl
from signal import SIGINT, signal
from sys import executable
from os import execl, remove
from os.path import isfile
from asyncio import create_subprocess_exec
from pyrogram.filters import command
from pyrogram.handlers import MessageHandler
from asyncio import gather
from aiofiles import open as aiopen

from .helper.other.commands import Commands
from .helper.other.other_utils import bot_uptime, get_logs_msg, get_host_stats
from bot.helper.pyrogram_helper.message_utils import sendMessage, sendFile
from bot.helper.pyrogram_helper.buttons import ButtonMaker
from bot.helper.jmd.utils.utils import sync_to_async, set_commands
from bot.helper.jmd.utils.files_utils import clean_all, start_cleanup, exit_clean_up
from bot.helper.jmd.aria2.aria2_engine import start_aria2_listener
from bot.helper.jmd import ml_handler, ml_status, t_select, h_alive, auth, cancel, rss, b_settings, u_settings, yt_handler, save_msg



async def restart(_, message):
    restart_message = await sendMessage(message, "Restarting...")
    if scheduler.running:
        scheduler.shutdown(wait=False)
    # for interval in [QbInterval, Interval]:
    for interval in [Interval]:
        if interval:
            interval[0].cancel()
    await sync_to_async(clean_all)
    # proc1 = await create_subprocess_exec('pkill', '-9', '-f', 'gunicorn|aria2c|qbittorrent-nox|ffmpeg|rclone')
    proc1 = await create_subprocess_exec('pkill', '-9', '-f', 'gunicorn|aria2c|ffmpeg|rclone')
    proc2 = await create_subprocess_exec('python3', 'update.py')
    await gather(proc1.wait(), proc2.wait())
    async with aiopen(".restartmsg", "w") as f:
        await f.write(f"{restart_message.chat.id}\n{restart_message.id}\n")
    osexecl(executable, executable, "-m", "bot")


async def start(bot, message):
            text = f"Hi {message.from_user.mention(style='md')}, I Am Alive."
            buttons = ButtonMaker()
            buttons.ubutton("⭐ Bot By 𝚂𝚊𝚑𝚒𝚕 ⭐", "https://t.me/nik66")
            buttons.ubutton("❤ Join Channel ❤", "https://t.me/nik66x")
            await sendMessage(message, text, buttons=buttons.build_menu(1))
            return


async def uptime(_, message):
    await sendMessage(message, f'♻Bot UpTime {bot_uptime()}')
    return

async def send_log(_, message):
    await sendMessage(message, get_logs_msg(log_file))
    await sendFile(message, log_file)
    return

async def bot_stats(_, message):
    await sendMessage(message, (await get_host_stats()))
    return

async def main(bot_name):
    if isfile(".restartmsg"):
        try:
            with open(".restartmsg") as f:
                    chat_id, msg_id = map(int, f)
            await bot.edit_message_text(chat_id, msg_id, "Restarted successfully!")  
        except Exception as e:
            LOGGER.error(str(e))
        remove(".restartmsg")
    await gather(start_cleanup(), set_commands(bot))
    await sync_to_async(start_aria2_listener, wait=False)
    bot.add_handler(MessageHandler(start, filters= command(Commands.StartCommand)))
    bot.add_handler(MessageHandler(restart, filters= command(Commands.RestartCommand)))
    bot.add_handler(MessageHandler(uptime, filters= command(Commands.UpTimeCommand)))
    bot.add_handler(MessageHandler(send_log, filters= command(Commands.LogCommand)))
    bot.add_handler(MessageHandler(bot_stats, filters= command(Commands.StatsCommand)))
    LOGGER.info(f'✅@{bot_name} Started Successfully!✅')
    LOGGER.info(f"⚡Bot By Sahil Nolia⚡")
    signal(SIGINT, exit_clean_up)

botloop.run_until_complete(main(bot.get_me().username))

botloop.run_forever()

