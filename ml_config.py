from asyncio import Lock
from threading import Thread
from time import sleep
from subprocess import run as srun
from aria2p import API as ariaAPI, Client as ariaClient
from config import LOGGER
from os.path import exists
from os import getcwd



Interval = []
DRIVES_NAMES = []
DRIVES_IDS = []
INDEX_URLS = []
aria2_options = {}
queued_dl = {}
queued_up = {}
non_queued_dl = set()
non_queued_up = set()

DOWNLOAD_DIR = f"{getcwd()}/downloads/"



download_dict_lock = Lock()
status_reply_dict_lock = Lock()
queue_dict_lock = Lock()
status_reply_dict = {}
download_dict = {}

if not exists('.netrc'):
    with open('.netrc', 'w'):
        pass
srun(["chmod", "600", ".netrc"])
srun(["cp", ".netrc", "/root/.netrc"])
srun(["chmod", "+x", "aria.sh"])
srun("./aria.sh", shell=True)


aria2 = ariaAPI(ariaClient(host="http://localhost", port=6800, secret=""))

def aria2c_init():
    try:
        LOGGER.info("Initializing Aria2c")
        link = "https://linuxmint.com/torrents/lmde-5-cinnamon-64bit.iso.torrent"
        dire = DOWNLOAD_DIR.rstrip("/")
        aria2.add_uris([link], {'dir': dire})
        sleep(3)
        downloads = aria2.get_downloads()
        sleep(10)
        aria2.remove(downloads, force=True, files=True, clean=True)
    except Exception as e:
        LOGGER.error(f"Aria2c initializing error: {e}")


Thread(target=aria2c_init).start()
sleep(1.5)

aria2c_global = ['bt-max-open-files', 'download-result', 'keep-unfinished-download-result', 'log', 'log-level',
                 'max-concurrent-downloads', 'max-download-result', 'max-overall-download-limit', 'save-session',
                 'max-overall-upload-limit', 'optimize-concurrent-downloads', 'save-cookies', 'server-stat-of']

if not aria2_options:
    aria2_options = aria2.client.get_global_option()
else:
    a2c_glo = {op: aria2_options[op]
               for op in aria2c_global if op in aria2_options}
    aria2.set_global_options(a2c_glo)
