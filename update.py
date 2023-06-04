from logger import LOGGER, log_file
from os.path import exists
from subprocess import run as srun, call as scall
from pymongo import MongoClient
from requests import get
from os import environ
from dotenv import load_dotenv


if exists(log_file):
    with open(log_file, 'r+') as f:
        f.truncate(0)


def dw_file_from_url(url, filename):
        r = get(url, allow_redirects=True, stream=True, timeout=60)
        with open(filename, 'wb') as fd:
                for chunk in r.iter_content(chunk_size=1024 * 10):
                        if chunk:
                                fd.write(chunk)
        return

CONFIG_FILE_URL = environ.get("CONFIG_FILE_URL", '')

if len(CONFIG_FILE_URL) and str(CONFIG_FILE_URL).startswith("http"):
        LOGGER.info(f"Downloading Config File From URL {CONFIG_FILE_URL}")
        dw_file_from_url(CONFIG_FILE_URL, "config.env")

if exists('config.env'):
        load_dotenv('config.env', override=True)

BOT_TOKEN = environ.get('BOT_TOKEN', '')
if len(BOT_TOKEN) == 0:
    LOGGER.error("BOT_TOKEN variable is missing! Exiting now")
    exit(1)

bot_id = BOT_TOKEN.split(':', 1)[0]
DATABASE = environ.get("MONGODB_URI", "")
DB_NAME = environ.get("DB_NAME","Nik66Bots")
UPSTREAM_REPO = environ.get("UPSTREAM_REPO", "")
UPSTREAM_BRANCH = environ.get("UPSTREAM_BRANCH", "")
UPDATE_PACKAGES = environ.get("UPDATE_PACKAGES", "")

if len(DATABASE) !=0 and DATABASE.lower()!='false':
    client = MongoClient(DATABASE)
    db = client[DB_NAME]
    if config_dict := db.config.find_one({'_id': bot_id}):
        LOGGER.info("Getting Update Data From Database")
        UPSTREAM_REPO = config_dict['UPSTREAM_REPO']
        UPSTREAM_BRANCH = config_dict['UPSTREAM_BRANCH']
        UPDATE_PACKAGES = config_dict['UPDATE_PACKAGES']
    client.close()


if UPDATE_PACKAGES.lower() == 'true':
    LOGGER.info(f"Updating Packages")
    scall("pip install -r requirements.txt --ignore-installed", shell=True)

if len(UPSTREAM_BRANCH) == 0:
    UPSTREAM_BRANCH = 'master'

if len(UPSTREAM_REPO) != 0:
    if exists('.git'):
        srun(["rm", "-rf", ".git"])
    
    update = srun([f"git init -q \
            && git config --global user.email nik66x@gmail.com \
            && git config --global user.name nik66 \
            && git add . \
            && git commit -sm update -q \
            && git remote add origin {UPSTREAM_REPO} \
            && git fetch origin -q \
            && git reset --hard origin/{UPSTREAM_BRANCH} -q"], shell=True)
    UPSTREAM_REPO_URL = (UPSTREAM_REPO[:8] if UPSTREAM_REPO[:8] and UPSTREAM_REPO[:8].endswith('/') else UPSTREAM_REPO[:7]) + UPSTREAM_REPO.split('@')[1] if '@github.com' in UPSTREAM_REPO else UPSTREAM_REPO
    if update.returncode == 0:
        LOGGER.info(f'✅Successfully updated with latest commit from {UPSTREAM_REPO_URL}')
    else:
        LOGGER.error(f'❗Something went wrong while updating, check {UPSTREAM_REPO_URL} if valid or not!')