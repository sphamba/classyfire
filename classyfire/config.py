import os

from dotenv import load_dotenv

load_dotenv()

DB_PATH = "db.json"
LANG = os.getenv("CLASSYFIRE_LANG", "en")
