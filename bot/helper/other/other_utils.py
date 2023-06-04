from string import ascii_lowercase, digits
from random import choices
from shutil import rmtree
from time import time
from bot import botStartTime, LOGGER, user_data
from shlex import split as shlexsplit
from typing import Tuple
from os.path import exists, isfile, getsize as os_getsize, join as os_join
from os import walk as os_walk
from psutil import disk_usage, cpu_percent, swap_memory, cpu_count, virtual_memory, net_io_counters, boot_time
from asyncio import create_subprocess_exec, create_subprocess_shell
from asyncio.subprocess import PIPE



###############------User Data------###############

def update_user_data(id_, key, value):
    if id_ in user_data:
        user_data[id_][key] = value
    else:
        user_data[id_] = {key: value}

def is_sudo(user_id):
    if user_id in user_data:
        return user_data[user_id].get('is_sudo')
    return False


###############------Time_Functions------###############
def get_readable_time(seconds: int) -> str:
    result = ''
    (days, remainder) = divmod(seconds, 86400)
    days = int(days)
    if days != 0:
        result += f'{days}d'
    (hours, remainder) = divmod(remainder, 3600)
    hours = int(hours)
    if hours != 0:
        result += f'{hours}h'
    (minutes, seconds) = divmod(remainder, 60)
    minutes = int(minutes)
    if minutes != 0:
        result += f'{minutes}m'
    seconds = int(seconds)
    result += f'{seconds}s'
    return result


class Timer:
    def __init__(self, time_between=5):
        self.start_time = time()
        self.time_between = time_between

    def can_send(self):
        if time() > (self.start_time + self.time_between):
            self.start_time = time()
            return True
        return False


def bot_uptime():
    return get_readable_time(time() - botStartTime)


###############------Generate_Random_String------###############
def gen_random_string(k):
    return str(''.join(choices(ascii_lowercase + digits, k=k)))



###############------Remove_Directory------###############
def remove_dir(dir):
    try:
        rmtree(dir)
        LOGGER.info(f'successfully deleted directory {dir}')
    except Exception as e:
        LOGGER.info(f'failed to delete directory {dir} : {str(e)}')
    return


###############------Size_Functions------###############
def get_human_size(num, format='B'):
    base = 1024.0
    if format=='B':
            sufix_list = ['B','KB','MB','GB','TB','PB','EB','ZB', 'YB']
    elif format=='KB':
            sufix_list = ['KB','MB','GB','TB','PB','EB','ZB', 'YB']
    elif format=='MB':
            sufix_list = ['MB','GB','TB','PB','EB','ZB', 'YB']
    for unit in sufix_list:
        if abs(num) < base:
            return f"{round(num, 2)} {unit}"
        num /= base


def get_path_size(path: str):
    if isfile(path):
        return os_getsize(path)
    total_size = 0
    for root, dirs, files in os_walk(path):
        for f in files:
            abs_path = os_join(root, f)
            total_size += os_getsize(abs_path)
    return total_size


###############------Get_Logs_From_File------###############
def get_logs_msg(log_file):
    with open(log_file, 'r', encoding="utf-8") as f:
                logFileLines = f.read().splitlines()
    Loglines = ''
    ind = 1
    if len(logFileLines):
        while len(Loglines) <= 3000:
            Loglines = logFileLines[-ind]+'\n'+Loglines
            if ind == len(logFileLines): break
            ind += 1
        startLine = f"Generated Last {ind} Lines from {str(log_file)}: \n\n---------------- START LOG -----------------\n\n"
        endLine = "\n---------------- END LOG -----------------"
        return startLine+Loglines+endLine
    else:
        return "Currently there is no error log"
    

###############------Executions------###############
async def execute(cmnd: str) -> Tuple[str, str, int, int]:
    LOGGER.info(cmnd)
    cmnds = shlexsplit(cmnd)
    process = await create_subprocess_exec(
        *cmnds,
        stdout=PIPE,
        stderr=PIPE
    )
    stdout, _ = await process.communicate()
    return stdout.decode('utf-8', 'replace').strip()


async def cmd_exec(cmd, shell=False):
    if shell:
        proc = await create_subprocess_shell(cmd, stdout=PIPE, stderr=PIPE)
    else:
        proc = await create_subprocess_exec(*cmd, stdout=PIPE, stderr=PIPE)
    stdout, stderr = await proc.communicate()
    stdout = stdout.decode().strip()
    stderr = stderr.decode().strip()
    return stdout, stderr, proc.returncode


###############------Get_Stats_Message------###############
async def get_host_stats():
        if exists('.git'):
                last_commit = await execute("git log -1 --date=short --pretty=format:'%cd <b>From</b> %cr'")
        else:
                last_commit = 'No UPSTREAM_REPO'
        total, used, free, disk = disk_usage('/')
        swap = swap_memory()
        memory = virtual_memory()
        stats =f'<b>Commit Date:</b> {last_commit}\n\n'\
                    f'<b>Bot Uptime:</b> {get_readable_time(time() - botStartTime)}\n'\
                    f'<b>OS Uptime:</b> {get_readable_time(time() - boot_time())}\n\n'\
                    f'<b>Total Disk Space:</b> {get_human_size(total)}\n'\
                    f'<b>Used:</b> {get_human_size(used)} | <b>Free:</b> {get_human_size(free)}\n\n'\
                    f'<b>Upload:</b> {get_human_size(net_io_counters().bytes_sent)}\n'\
                    f'<b>Download:</b> {get_human_size(net_io_counters().bytes_recv)}\n\n'\
                    f'<b>CPU:</b> {cpu_percent(interval=0.5)}%\n'\
                    f'<b>RAM:</b> {memory.percent}%\n'\
                    f'<b>DISK:</b> {disk}%\n\n'\
                    f'<b>Physical Cores:</b> {cpu_count(logical=False)}\n'\
                    f'<b>Total Cores:</b> {cpu_count(logical=True)}\n\n'\
                    f'<b>SWAP:</b> {get_human_size(swap.total)} | <b>Used:</b> {swap.percent}%\n'\
                    f'<b>Memory Total:</b> {get_human_size(memory.total)}\n'\
                    f'<b>Memory Free:</b> {get_human_size(memory.available)}\n'\
                    f'<b>Memory Used:</b> {get_human_size(memory.used)}'
        return stats