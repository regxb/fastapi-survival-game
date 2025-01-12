import os

from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.environ.get("POSTGRES_HOST")
DB_PORT = os.environ.get("POSTGRES_PORT")
DB_NAME = os.environ.get("POSTGRES_DB")
DB_USER = os.environ.get("POSTGRES_USER")
DB_PASS = os.environ.get("POSTGRES_PASSWORD")

TEST_DB_PORT = os.environ.get("TEST_POSTGRES_PORT")
TEST_DB_NAME = os.environ.get("TEST_POSTGRES_DB")
TEST_DB_USER = os.environ.get("TEST_POSTGRES_USER")
TEST_DB_PASS = os.environ.get("TEST_POSTGRES_PASSWORD")

DEV = os.environ.get("DEV")

BOT_TOKEN = os.environ.get("BOT_TOKEN")

REDIS_URL = os.environ.get("REDIS_URL")
